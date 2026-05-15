"""
Modül Adı: predict.py
Açıklama : Eğitilmiş Random Forest modeli kullanarak inme riski tahmini yapar.
           Tek hasta tahmini, toplu tahmin ve MongoDB kayıt desteği içerir.
           Flask API ve Streamlit Dashboard tarafından kullanılır.
Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-05-11
Version  : 1.0
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

# Model yükleme fonksiyonu
# Hem proje kökünden (python -m model.predict) hem de
# doğrudan (python model/predict.py) çalıştırılabilmesi için
try:
    from model.train import model_yukle
except ImportError:
    from train import model_yukle


# ── Risk seviyeleri (agent.md) ──
RISK_SEVIYELERI = {
    "Düşük" : (0.00, 0.10),
    "Orta"  : (0.10, 0.30),
    "Yüksek": (0.30, 1.00),
}

RISK_RENKLERI = {
    "Düşük" : "#00AA00",
    "Orta"  : "#FFAA00",
    "Yüksek": "#FF0000",
}

# ── Geçerli kategorik değerler (train.py KATEGORIK_ESLESME ile eşleşmeli) ──
GECERLI_CINSIYETLER    = {"Erkek", "Kadın", "Diğer"}
GECERLI_EVLI           = {"Evet", "Hayır"}
GECERLI_CALISMA        = {"Çalışan", "Serbest", "Hükümet", "İşsiz", "Çocuk"}
GECERLI_IKAMET         = {"Kırsal", "Kentsel"}
GECERLI_SIGARA         = {"Eski İçici", "Halen İçiyor"}


# ════════════════════════════════════════════════════════════════
# MODEL SINGLETON — tek seferinde yüklenir
# ════════════════════════════════════════════════════════════════

_model_cache = None

def _model_getir() -> tuple:
    """
    Modeli önbelleğe alarak döndürür. İlk çağrıda diskten yükler.

    Returns:
        tuple: (model, encoders, ozellik_adlari)

    Raises:
        FileNotFoundError: Model dosyaları yoksa
    """
    global _model_cache
    if _model_cache is None:
        _model_cache = model_yukle()
    return _model_cache


# ════════════════════════════════════════════════════════════════
# VERİ DOĞRULAMA
# ════════════════════════════════════════════════════════════════

def hasta_verisi_dogrula(veri: dict) -> dict:
    """
    Gelen hasta verisini doğrular; eksik veya hatalı alan varsa bildirir.

    Args:
        veri (dict): Ham hasta verisi

    Returns:
        dict: {"gecerli": bool, "hatalar": list[str]}
    """
    hatalar = []

    # Zorunlu alanlar
    zorunlu = [
        "yas", "cinsiyet", "hipertansiyon", "kalp_hastaligi",
        "evli_mi", "calisma_tipi", "ikamet_tipi",
        "ortalama_seker", "vucut_kitle_indeksi", "sigara_durumu"
    ]
    for alan in zorunlu:
        if alan not in veri or veri[alan] is None or veri[alan] == "":
            hatalar.append(f"Gerekli alan boş: '{alan}'")

    if hatalar:
        return {"gecerli": False, "hatalar": hatalar}

    # Yaş
    try:
        yas = float(veri["yas"])
        if not (0 <= yas <= 120):
            hatalar.append("Yaş 0-120 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Yaş sayısal bir değer olmalıdır.")

    # BMI
    try:
        bmi = float(veri["vucut_kitle_indeksi"])
        if not (10 <= bmi <= 100):
            hatalar.append("Vücut Kitle İndeksi 10-100 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Vücut Kitle İndeksi sayısal bir değer olmalıdır.")

    # Ortalama şeker
    try:
        seker = float(veri["ortalama_seker"])
        if not (40 <= seker <= 400):
            hatalar.append("Ortalama şeker değeri 40-400 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Ortalama şeker sayısal bir değer olmalıdır.")

    # İkili değerler
    for alan in ["hipertansiyon", "kalp_hastaligi"]:
        try:
            deger = int(veri[alan])
            if deger not in (0, 1):
                hatalar.append(f"'{alan}' sadece 0 veya 1 olabilir.")
        except (ValueError, TypeError):
            hatalar.append(f"'{alan}' sayısal (0/1) bir değer olmalıdır.")

    # Kategorik değerler
    kategorik_kontrol = {
        "cinsiyet"    : GECERLI_CINSIYETLER,
        "evli_mi"     : GECERLI_EVLI,
        "calisma_tipi": GECERLI_CALISMA,
        "ikamet_tipi" : GECERLI_IKAMET,
        "sigara_durumu": GECERLI_SIGARA,
    }
    for alan, gecerli_degerler in kategorik_kontrol.items():
        if alan in veri and veri[alan] not in gecerli_degerler:
            hatalar.append(
                f"'{alan}' için geçersiz değer: '{veri[alan]}'. "
                f"Kabul edilen: {sorted(gecerli_degerler)}"
            )

    return {"gecerli": len(hatalar) == 0, "hatalar": hatalar}


# ════════════════════════════════════════════════════════════════
# RİSK HESAPLAMA YARDIMCISI
# ════════════════════════════════════════════════════════════════

def _risk_seviyesi_belirle(risk_skoru: float) -> str:
    """
    Risk skorunu kategoriye çevirir.

    Args:
        risk_skoru (float): 0.0 - 1.0 arası skor

    Returns:
        str: "Düşük", "Orta" veya "Yüksek"
    """
    for seviye, (alt, ust) in RISK_SEVIYELERI.items():
        if alt <= risk_skoru < ust:
            return seviye
    return "Yüksek"  # 1.0 kenar durumu


def _uzman_oneri_uret(risk_seviyesi: str, veri: dict) -> dict:
    """
    Risk seviyesi ve hasta verilerine göre yapılandırılmış uzman önerisi üretir.

    Returns:
        dict: {doktor_onerileri, yasam_tarzi_onerileri, izleme_onerileri,
               aciliyet, aciliyet_rengi, ozet}
    """
    yas            = float(veri.get("yas", 50))
    hipertansiyon  = int(veri.get("hipertansiyon", 0))
    kalp_hastaligi = int(veri.get("kalp_hastaligi", 0))
    bmi            = float(veri.get("vucut_kitle_indeksi", 25))
    seker          = float(veri.get("ortalama_seker", 90))
    sigara         = veri.get("sigara_durumu", "")

    doktor_onerileri = []
    yasam_tarzi      = []
    izleme           = []

    # ── Temel nöroloji önerisi (risk seviyesine göre) ──
    if risk_seviyesi == "Yüksek":
        doktor_onerileri.append({
            "uzmanlik": "Nöroloji",
            "aciliyet": "ACİL",
            "neden"   : "Yüksek inme riski — bu hafta randevu alın",
        })
    elif risk_seviyesi == "Orta":
        doktor_onerileri.append({
            "uzmanlik": "Nöroloji",
            "aciliyet": "Öncelikli",
            "neden"   : "Orta düzeyde inme riski — 1 ay içinde değerlendirme önerilir",
        })
    else:
        doktor_onerileri.append({
            "uzmanlik": "İç Hastalıkları / Genel Pratisyen",
            "aciliyet": "Rutin",
            "neden"   : "Yıllık rutin kontrol yeterlidir",
        })

    # ── Hipertansiyon ──
    if hipertansiyon:
        aci = "ACİL" if risk_seviyesi == "Yüksek" else "Öncelikli"
        doktor_onerileri.append({
            "uzmanlik": "Kardiyoloji",
            "aciliyet": aci,
            "neden"   : "Tansiyon kontrolü ve ilaç düzenlemesi gereklidir",
        })
        yasam_tarzi.append(
            "Günlük tuz alımını 5 g altında tutun — işlenmiş ve hazır gıdalardan kaçının"
        )
        izleme.append(
            "Günde sabah-akşam tansiyon ölçümü yapın; sonuçları takip defterine kaydedin"
        )

    # ── Kalp hastalığı ──
    if kalp_hastaligi:
        aci = "ACİL" if risk_seviyesi == "Yüksek" else "Öncelikli"
        doktor_onerileri.append({
            "uzmanlik": "Kardiyoloji",
            "aciliyet": aci,
            "neden"   : "Kalp hastalığı inme riskini 2-4 kat artırır; düzenli kardiyoloji takibi şarttır",
        })
        izleme.append(
            "EKG ve ekokardiyografi için kardiyoloji randevusu alın; kalp ilaçlarını aksatmayın"
        )

    # ── Yüksek kan şekeri ──
    if seker > 180:
        doktor_onerileri.append({
            "uzmanlik": "Endokrinoloji (Diyabet)",
            "aciliyet": "Öncelikli",
            "neden"   : f"Kan şekeri {seker:.0f} mg/dL — diyabet inme riskini belirgin artırır",
        })
        yasam_tarzi.append(
            "Düşük glisemik indeksli besinler tercih edin; şekerli içecek ve beyaz ekmekten kaçının"
        )
        izleme.append("3 ayda bir HbA1c testi ve açlık kan şekeri ölçümü yaptırın")
    elif seker > 126:
        yasam_tarzi.append(
            "Kan şekeriniz sınır değerde — şeker ve rafine karbonhidrat tüketimini azaltın"
        )
        izleme.append("Yılda iki kez açlık kan şekeri kontrolü yaptırın")

    # ── Obezite ──
    if bmi > 35:
        doktor_onerileri.append({
            "uzmanlik": "Beslenme ve Diyet / İç Hastalıkları",
            "aciliyet": "Öncelikli",
            "neden"   : f"BMI {bmi:.1f} — ağır obezite tüm kardiyovasküler riskleri artırır",
        })
        yasam_tarzi.append(
            "Ağırlık yönetimi için diyetisyen desteği alın; kalori kısıtlamalı diyet başlatın"
        )
    elif bmi > 30:
        yasam_tarzi.append(
            "BMI idealin üzerinde — haftada 5 gün en az 30 dakika tempolu yürüyüş yapın"
        )

    # ── Sigara ──
    if sigara == "Halen İçiyor":
        yasam_tarzi.append(
            "Sigarayı bırakmak inme riskini 2-4 yıl içinde yarıya indirir "
            "— sigara bırakma polikliniğine veya ALO 171 hattına başvurun"
        )
        izleme.append(
            "Sigara bırakma desteği için aile hekiminizle görüşün veya ALO 171 hattını arayın"
        )
    elif sigara == "Eski İçici":
        yasam_tarzi.append(
            "Sigarayı bıraktınız — bu kararlılığı sürdürün ve pasif dumanından da uzak durun"
        )

    # ── Yaşa göre ek öneriler ──
    if yas >= 65:
        yasam_tarzi.append(
            "İlaçlarınızı düzenli alın; ani yüz sarkması, kol-bacak güçsüzlüğü "
            "veya konuşma güçlüğünde derhal 112 arayın"
        )
        izleme.append("6 ayda bir nöroloji ve kardiyoloji kontrolü önerilir")
    elif yas >= 50:
        izleme.append(
            "Yılda bir kapsamlı kardiyovasküler risk değerlendirmesi yaptırın"
        )

    # ── Evrensel yaşam tarzı önerileri ──
    yasam_tarzi.append(
        "Haftada 150 dakika orta şiddetli aerobik egzersiz yapın (yürüyüş, yüzme, bisiklet)"
    )
    yasam_tarzi.append(
        "Akdeniz diyeti benimseyin: bol sebze-meyve, tam tahıl, zeytinyağı, balık"
    )
    yasam_tarzi.append(
        "Stres yönetimi için meditasyon veya nefes egzersizleri uygulayın; "
        "günde 7-8 saat düzenli uyku sağlayın"
    )
    yasam_tarzi.append("Alkol tüketimini sınırlayın veya tamamen bırakın")

    if not izleme:
        izleme.append(
            "Yıllık rutin kontrolde tansiyon, kan şekeri ve kolesterol ölçümü yaptırmayı unutmayın"
        )

    # ── Özet metin (backward-compat oneri alanı) ──
    uzm_listesi = " | ".join(d["uzmanlik"] for d in doktor_onerileri[:2])
    if risk_seviyesi == "Yüksek":
        ozet = f"ACİL: {uzm_listesi} uzmanına bu hafta başvurun."
    elif risk_seviyesi == "Orta":
        ozet = f"Öncelikli: {uzm_listesi} konsültasyonu önerilir."
    else:
        ozet = f"Rutin kontrol: {uzm_listesi} yeterlidir."

    aciliyet_map = {"Yüksek": "ACİL",     "Orta": "Öncelikli", "Düşük": "Rutin"}
    renk_map     = {"Yüksek": "#ef4444",  "Orta": "#f59e0b",   "Düşük": "#22c55e"}

    return {
        "doktor_onerileri"      : doktor_onerileri,
        "yasam_tarzi_onerileri" : yasam_tarzi,
        "izleme_onerileri"      : izleme,
        "aciliyet"              : aciliyet_map[risk_seviyesi],
        "aciliyet_rengi"        : renk_map[risk_seviyesi],
        "ozet"                  : ozet,
    }


# ════════════════════════════════════════════════════════════════
# ÖZELLİK HAZIRLAMA
# ════════════════════════════════════════════════════════════════

def _ozellikleri_hazirla(veri: dict, encoders: dict, ozellik_adlari: list) -> np.ndarray:
    """
    Ham hasta verisini modelin beklediği formata dönüştürür.

    Args:
        veri (dict): Ham hasta verisi
        encoders (dict): Label encoder sözlüğü
        ozellik_adlari (list): Eğitimde kullanılan özellik isimleri

    Returns:
        np.ndarray: Model için hazır özellik vektörü (1 x n_features)

    Raises:
        ValueError: Dönüşüm hatası
    """
    df = pd.DataFrame([veri])

    # Sayısal alanları float'a çevir
    sayisal_alanlar = ["yas", "ortalama_seker", "vucut_kitle_indeksi",
                       "hipertansiyon", "kalp_hastaligi"]
    for alan in sayisal_alanlar:
        if alan in df.columns:
            df[alan] = pd.to_numeric(df[alan], errors="coerce").fillna(0)

    # Kategorik alanları encode et (dict-tabanlı, CSV sırasına uygun)
    kategorik_alanlar = ["cinsiyet", "evli_mi", "calisma_tipi",
                         "ikamet_tipi", "sigara_durumu"]
    for alan in kategorik_alanlar:
        if alan in df.columns and alan in encoders:
            enc = encoders[alan]
            if isinstance(enc, dict):
                df[alan] = df[alan].astype(str).map(enc).fillna(0).astype(int)
            else:
                # Eski LabelEncoder nesneleri için geriye dönük uyumluluk
                try:
                    df[alan] = enc.transform(df[alan].astype(str))
                except (ValueError, AttributeError):
                    df[alan] = 0

    # Eğitimdeki özellik sırasına uy, eksik olanları 0 ile doldur
    for ozellik in ozellik_adlari:
        if ozellik not in df.columns:
            df[ozellik] = 0

    return df[ozellik_adlari].values


# ════════════════════════════════════════════════════════════════
# ANA TAHMİN FONKSİYONLARI
# ════════════════════════════════════════════════════════════════

def hasta_risk_tahmini(hasta_verisi: dict) -> dict:
    """
    Tek bir hasta için inme risk tahmini yapar.

    Args:
        hasta_verisi (dict): {
            "yas": int,
            "cinsiyet": str,          # "Erkek" | "Kadın"
            "hipertansiyon": int,     # 0 | 1
            "kalp_hastaligi": int,    # 0 | 1
            "evli_mi": str,           # "Evet" | "Hayır" | "Eski" | "Hiç"
            "calisma_tipi": str,      # "Çalışan" | "Serbest" | "Hükümet" | "İşsiz"
            "ikamet_tipi": str,       # "Kırsal" | "Kentsel"
            "ortalama_seker": float,
            "vucut_kitle_indeksi": float,
            "sigara_durumu": str      # "Hiç İçmedi" | "Eski İçici" | "Halen İçiyor"
        }

    Returns:
        dict: {
            "basarili": bool,
            "risk_skoru": float,          # 0.0 - 1.0
            "risk_yuzdesi": float,        # 0.0 - 100.0
            "risk_seviyesi": str,         # "Düşük" | "Orta" | "Yüksek"
            "risk_rengi": str,            # HEX renk kodu
            "oneri": str,
            "tahmin_tarihi": str,
            "mesaj": str                  # Hata durumunda açıklama
        }
    """
    try:
        # Doğrulama
        dogrulama = hasta_verisi_dogrula(hasta_verisi)
        if not dogrulama["gecerli"]:
            return {
                "basarili"     : False,
                "risk_skoru"   : None,
                "risk_yuzdesi" : None,
                "risk_seviyesi": None,
                "risk_rengi"   : None,
                "oneri"        : None,
                "tahmin_tarihi": None,
                "mesaj"        : "Geçersiz veri: " + "; ".join(dogrulama["hatalar"]),
            }

        # Model yükle
        model, encoders, ozellik_adlari = _model_getir()

        # Özellikleri hazırla
        X = _ozellikleri_hazirla(hasta_verisi, encoders, ozellik_adlari)

        # Tahmin
        risk_skoru    = float(model.predict_proba(X)[0][1])
        risk_seviyesi = _risk_seviyesi_belirle(risk_skoru)
        oneri_dict    = _uzman_oneri_uret(risk_seviyesi, hasta_verisi)

        return {
            "basarili"              : True,
            "risk_skoru"            : round(risk_skoru, 4),
            "risk_yuzdesi"          : round(risk_skoru * 100, 2),
            "risk_seviyesi"         : risk_seviyesi,
            "risk_rengi"            : RISK_RENKLERI[risk_seviyesi],
            "oneri"                 : oneri_dict["ozet"],
            "doktor_onerileri"      : oneri_dict["doktor_onerileri"],
            "yasam_tarzi_onerileri" : oneri_dict["yasam_tarzi_onerileri"],
            "izleme_onerileri"      : oneri_dict["izleme_onerileri"],
            "aciliyet"              : oneri_dict["aciliyet"],
            "aciliyet_rengi"        : oneri_dict["aciliyet_rengi"],
            "tahmin_tarihi"         : datetime.now().isoformat(),
            "mesaj"                 : "Tahmin başarıyla tamamlandı",
        }

    except FileNotFoundError as e:
        return {
            "basarili": False,
            "mesaj"   : f"Model tahmin hatasıyla karşılaşıldı: {str(e)}",
            "risk_skoru": None, "risk_yuzdesi": None,
            "risk_seviyesi": None, "risk_rengi": None,
            "oneri": None, "tahmin_tarihi": None,
        }
    except Exception as e:
        return {
            "basarili": False,
            "mesaj"   : f"Model tahmin hatasıyla karşılaşıldı: {str(e)}",
            "risk_skoru": None, "risk_yuzdesi": None,
            "risk_seviyesi": None, "risk_rengi": None,
            "oneri": None, "tahmin_tarihi": None,
        }


def toplu_tahmin(hasta_listesi: list) -> list:
    """
    Birden fazla hasta için toplu tahmin yapar.

    Args:
        hasta_listesi (list): Hasta veri sözlükleri listesi

    Returns:
        list: Her hasta için tahmin sonuçları listesi
    """
    sonuclar = []
    for i, hasta in enumerate(hasta_listesi):
        sonuc = hasta_risk_tahmini(hasta)
        sonuc["sira"] = i + 1
        sonuclar.append(sonuc)

    basarili = sum(1 for s in sonuclar if s["basarili"])
    print(f"✅ Toplu tahmin: {basarili}/{len(sonuclar)} başarılı")

    return sonuclar


def mongodb_risk_kaydet(
    db,
    hasta_id: str,
    doktor_id: str,
    tahmin_sonucu: dict
) -> dict:
    """
    Tahmin sonucunu MongoDB risk_tahminleri koleksiyonuna kaydeder.

    Args:
        db: MongoDB veritabanı nesnesi (database.connection'dan)
        hasta_id (str): Hasta ID'si (HS-0001 formatı)
        doktor_id (str): Doktor ID'si (KL-0001 formatı)
        tahmin_sonucu (dict): hasta_risk_tahmini() çıktısı

    Returns:
        dict: {"basarili": bool, "tahmin_id": str, "mesaj": str}
    """
    if not tahmin_sonucu.get("basarili"):
        return {
            "basarili" : False,
            "tahmin_id": None,
            "mesaj"    : "Kaydedilecek geçerli tahmin yok",
        }

    try:
        # Sıradaki tahmin numarasını belirle
        mevcut_sayi   = db.risk_tahminleri.count_documents({})
        tahmin_no     = f"TP-{str(mevcut_sayi + 1).zfill(5)}"

        belge = {
            "tahmin_no"          : tahmin_no,
            "hasta_id"           : hasta_id,
            "doktor_id"          : doktor_id,
            "model_versiyon"     : "1.0-RandomForest",
            "risk_skoru"         : tahmin_sonucu["risk_skoru"],
            "risk_seviyesi"      : tahmin_sonucu["risk_seviyesi"],
            "tahmin_tarihi"      : datetime.now(),
            "oneri"              : tahmin_sonucu["oneri"],
            "onay_durumu"        : "Beklemede",
            "olusturma_tarihi"   : datetime.now(),
        }

        sonuc = db.risk_tahminleri.insert_one(belge)

        return {
            "basarili" : True,
            "tahmin_id": tahmin_no,
            "mesaj"    : f"Risk tahmini veritabanına kaydedildi: {tahmin_no}",
        }

    except Exception as e:
        return {
            "basarili" : False,
            "tahmin_id": None,
            "mesaj"    : f"Veritabanı kayıt hatası: {str(e)}",
        }


# ════════════════════════════════════════════════════════════════
# FLASK API UYUMLU YARDIMCI
# ════════════════════════════════════════════════════════════════

def api_risk_tahmini(request_json: dict) -> dict:
    """
    Flask API endpoint'i için hazır çıktı üretir.
    api/app.py içindeki /api/risk-tahmini endpoint'i tarafından kullanılır.

    Args:
        request_json (dict): API isteğinden gelen JSON verisi

    Returns:
        dict: API yanıt objesi
    """
    sonuc = hasta_risk_tahmini(request_json)

    if not sonuc["basarili"]:
        return {
            "hata"   : sonuc["mesaj"],
            "durum"  : "hata",
        }, 400

    return {
        "risk_skoru"   : sonuc["risk_skoru"],
        "risk_yuzdesi" : sonuc["risk_yuzdesi"],
        "risk_seviyesi": sonuc["risk_seviyesi"],
        "oneri"        : sonuc["oneri"],
        "tahmin_tarihi": sonuc["tahmin_tarihi"],
        "durum"        : "basarili",
    }, 200


# ════════════════════════════════════════════════════════════════
# MANUEL TEST
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("  TAHMİN MODÜLİ TEST")
    print("═" * 60)

    # Örnek hasta verileri (agent.md API örneğinden)
    # Test verileri — train.py KATEGORIK_ESLESME ile eşleşen değerler kullanılıyor
    test_hastalari = [
        {
            "ad_soyad"           : "Yüksek Risk Hastası",
            "yas"                : 67,
            "cinsiyet"           : "Erkek",
            "hipertansiyon"      : 0,
            "kalp_hastaligi"     : 1,
            "evli_mi"            : "Evet",
            "calisma_tipi"       : "Çalışan",
            "ikamet_tipi"        : "Kentsel",
            "ortalama_seker"     : 228.69,
            "vucut_kitle_indeksi": 36.6,
            "sigara_durumu"      : "Halen İçiyor",
        },
        {
            "ad_soyad"           : "Düşük Risk Hastası",
            "yas"                : 25,
            "cinsiyet"           : "Kadın",
            "hipertansiyon"      : 0,
            "kalp_hastaligi"     : 0,
            "evli_mi"            : "Hayır",
            "calisma_tipi"       : "Çalışan",
            "ikamet_tipi"        : "Kentsel",
            "ortalama_seker"     : 80.0,
            "vucut_kitle_indeksi": 22.5,
            "sigara_durumu"      : "Eski İçici",
        },
        {
            "ad_soyad"           : "API Örneği (agent.md)",
            "yas"                : 55,
            "cinsiyet"           : "Erkek",
            "hipertansiyon"      : 1,
            "kalp_hastaligi"     : 0,
            "evli_mi"            : "Evet",
            "calisma_tipi"       : "Çalışan",
            "ikamet_tipi"        : "Kentsel",
            "ortalama_seker"     : 140,
            "vucut_kitle_indeksi": 28.5,
            "sigara_durumu"      : "Halen İçiyor",
        },
    ]

    for i, hasta in enumerate(test_hastalari, 1):
        ad  = hasta.pop("ad_soyad")
        sonuc = hasta_risk_tahmini(hasta)
        print(f"\n--- Hasta {i}: {ad} ---")
        if sonuc["basarili"]:
            print(f"  Risk Skoru   : {sonuc['risk_skoru']} ({sonuc['risk_yuzdesi']}%)")
            print(f"  Risk Seviyesi: {sonuc['risk_seviyesi']}")
            print(f"  Öneri        : {sonuc['oneri']}")
        else:
            print(f"  ❌ Hata: {sonuc['mesaj']}")

    print("\n" + "═" * 60 + "\n")