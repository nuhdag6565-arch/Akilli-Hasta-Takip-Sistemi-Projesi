"""
Modül Adı: predict.py
Açıklama : Eğitilmiş HistGBM modeli kullanarak inme riski tahmini yapar.

           Geliştirmeler (v2):
           • Klinik skor: TOPLAMA → ÇARPIMSAL (Hazard Ratio) modeli
             (Framingham Stroke Risk Profile'a uygun)
           • Daha granüler yaş eğrisi (6 → 12 basamak)
           • "Hiç İçmedi" HR katkısı sıfır (önceden "Eski İçici" ile eşdeğer tutuluyordu)
           • Adaptif blend: risk faktörü sayısına göre klinik/ML ağırlığı dinamik
           • Özellik mühendisliği: train.py ile birebir aynı dönüşümler

Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-06-08
Version  : 2.0
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

try:
    from model.train import model_yukle, ozellik_muhendisligi
except ImportError:
    from train import model_yukle, ozellik_muhendisligi


# ── Risk seviyeleri ──────────────────────────────────────────────
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

# ── Geçerli kategorik değerler ───────────────────────────────────
GECERLI_CINSIYETLER = {"Erkek", "Kadın", "Diğer"}
GECERLI_EVLI        = {"Evet", "Hayır"}
GECERLI_CALISMA     = {"Çalışan", "Serbest", "Hükümet", "İşsiz", "Çocuk"}
GECERLI_IKAMET      = {"Kırsal", "Kentsel"}
GECERLI_SIGARA      = {"Hiç İçmedi", "Eski İçici", "Halen İçiyor"}


# ════════════════════════════════════════════════════════════════
# MODEL SINGLETON
# ════════════════════════════════════════════════════════════════

_model_cache = None

def _model_getir() -> tuple:
    global _model_cache
    if _model_cache is None:
        _model_cache = model_yukle()
    return _model_cache


# ════════════════════════════════════════════════════════════════
# VERİ DOĞRULAMA
# ════════════════════════════════════════════════════════════════

def hasta_verisi_dogrula(veri: dict) -> dict:
    hatalar = []
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

    try:
        yas = float(veri["yas"])
        if not (0 <= yas <= 120):
            hatalar.append("Yaş 0-120 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Yaş sayısal bir değer olmalıdır.")

    try:
        bmi = float(veri["vucut_kitle_indeksi"])
        if not (10 <= bmi <= 100):
            hatalar.append("Vücut Kitle İndeksi 10-100 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Vücut Kitle İndeksi sayısal bir değer olmalıdır.")

    try:
        seker = float(veri["ortalama_seker"])
        if not (40 <= seker <= 400):
            hatalar.append("Ortalama şeker değeri 40-400 arasında olmalıdır.")
    except (ValueError, TypeError):
        hatalar.append("Ortalama şeker sayısal bir değer olmalıdır.")

    for alan in ["hipertansiyon", "kalp_hastaligi"]:
        try:
            if int(veri[alan]) not in (0, 1):
                hatalar.append(f"'{alan}' sadece 0 veya 1 olabilir.")
        except (ValueError, TypeError):
            hatalar.append(f"'{alan}' sayısal (0/1) bir değer olmalıdır.")

    for alan, gecerli in {
        "cinsiyet"    : GECERLI_CINSIYETLER,
        "evli_mi"     : GECERLI_EVLI,
        "calisma_tipi": GECERLI_CALISMA,
        "ikamet_tipi" : GECERLI_IKAMET,
        "sigara_durumu": GECERLI_SIGARA,
    }.items():
        if alan in veri and veri[alan] not in gecerli:
            hatalar.append(
                f"'{alan}' için geçersiz değer: '{veri[alan]}'. "
                f"Kabul edilen: {sorted(gecerli)}"
            )

    return {"gecerli": len(hatalar) == 0, "hatalar": hatalar}


# ════════════════════════════════════════════════════════════════
# KLİNİK SKOR — ÇARPIMSAL HAZARD RATIO MODELİ
#
# Tıbbi dayanak:
#   • Framingham Stroke Risk Profile (Wolf et al., 1991; D'Agostino et al., 1994)
#   • AHA/ASA 2021 Stroke Prevention Guidelines
#   • Meta-analiz HR değerleri: Feigin et al., Lancet Neurology 2016
#
# Formül: P(inme) = 1 − (1 − P_baz)^HR_toplam
#   HR_toplam = ∏ (bireysel hazard ratio'lar)
#   Bu formül, Cox orantılı hazard modelinden türetilmiştir ve
#   risk faktörlerinin bağımsız çarpımsal katkısını doğru modeller.
# ════════════════════════════════════════════════════════════════

def _klinik_skor_hesapla(veri: dict) -> float:
    yas      = float(veri.get("yas",                    50))
    cinsiyet = str(veri.get("cinsiyet",                 ""))
    hiper    = int(veri.get("hipertansiyon",             0))
    kalp     = int(veri.get("kalp_hastaligi",            0))
    seker    = float(veri.get("ortalama_seker",          90))
    sigara   = str(veri.get("sigara_durumu",             ""))
    bmi      = float(veri.get("vucut_kitle_indeksi",     25))

    # ── 1. Yaşa göre baz risk ────────────────────────────────────
    # İnme insidansı 10 yıllık kohort verilerine göre kalibre edilmiştir.
    # Risk her ~10 yılda yaklaşık 2 katına çıkar (üstel büyüme).
    if   yas <  30: baz = 0.003
    elif yas <  35: baz = 0.007
    elif yas <  40: baz = 0.013
    elif yas <  45: baz = 0.022
    elif yas <  50: baz = 0.036
    elif yas <  55: baz = 0.058
    elif yas <  60: baz = 0.088
    elif yas <  65: baz = 0.125
    elif yas <  70: baz = 0.175
    elif yas <  75: baz = 0.240
    elif yas <  80: baz = 0.320
    else:           baz = 0.420

    # ── 2. Hazard Ratio çarpımı ───────────────────────────────────
    hr = 1.0

    # Hipertansiyon: en önemli modifiye edilebilir RF — HR ≈ 2.0
    # (Lewington et al., Lancet 2002; Feigin et al., 2016)
    if hiper:
        hr *= 2.0

    # Kalp hastalığı (AF, KKY, geçirilmiş MI): HR ≈ 2.5–4.0
    # AF tek başına HR ~4 (Wolf et al.); genel KH için HR ~3 kullanıldı
    if kalp:
        hr *= 3.0

    # Sigara:
    #   Aktif içici → HR ≈ 1.5 (Shinton & Beevers, BMJ 1989)
    #   Eski içici  → HR ≈ 1.1 (kalıntı risk ~5-10 yıl sürer)
    #   Hiç içmedi  → HR = 1.0 (referans kategori, artış yok)
    if   sigara == "Halen İçiyor": hr *= 1.50
    elif sigara == "Eski İçici":   hr *= 1.10
    # "Hiç İçmedi" → hr *= 1.0 (katkı yok)

    # Kan şekeri / Diyabet:
    #   ≥250 mg/dL → ağır hiperglisemi, HR ≈ 1.8
    #   ≥180 mg/dL → diyabetik aralık,  HR ≈ 1.5
    #   ≥126 mg/dL → diyabet eşiği,     HR ≈ 1.25
    #   (Emerging Risk Factors Collaboration, JAMA 2010)
    if   seker >= 250: hr *= 1.80
    elif seker >= 180: hr *= 1.50
    elif seker >= 126: hr *= 1.25

    # Obezite (BMI):
    #   ≥40 → morbid obezite,  HR ≈ 1.30
    #   ≥35 → ciddi obezite,   HR ≈ 1.20
    #   ≥30 → obezite,         HR ≈ 1.10
    #   (Strazzullo et al., Obes Rev 2010)
    if   bmi >= 40: hr *= 1.30
    elif bmi >= 35: hr *= 1.20
    elif bmi >= 30: hr *= 1.10

    # Erkek cinsiyet (<65 yaş): HR ≈ 1.10
    # (65+ yaşta cinsiyet farkı daralır, kadın riski artar)
    if cinsiyet == "Erkek" and yas < 65:
        hr *= 1.10

    # ── 3. Mutlak risk hesaplama ─────────────────────────────────
    # Cox modelinden türetilmiş dönüşüm:
    # P = 1 − (1 − P_baz)^HR
    risk = 1.0 - (1.0 - baz) ** hr

    # ── 4. Klinik minimum eşikler (AHA/ACC ikincil korunma kılavuzu) ─
    # Çarpımsal formül küçük baz risklerde yetersiz kalır; genç hastalarda
    # ciddi risk faktörleri varlığında mutlak minimum uygulanır.
    #
    # • Kalp hastalığı (tek başına): her yaşta en az "Orta" başlangıcı
    if kalp:
        risk = max(risk, 0.15)

    # • Hipertansiyon (tek başına): en az "Orta"
    if hiper:
        risk = max(risk, 0.12)

    # • HT + Kalp hastalığı birlikte: AHA Tier-1 yüksek risk → "Yüksek"
    if hiper and kalp:
        risk = max(risk, 0.32)

    # • HT veya KH + aktif sigara: ek ağırlama
    if (hiper or kalp) and sigara == "Halen İçiyor":
        risk = max(risk, 0.25)

    # • HT veya KH + diyabetik kan şekeri
    if (hiper or kalp) and seker >= 126:
        risk = max(risk, 0.22)

    return min(0.95, risk)


def _risk_seviyesi_belirle(risk_skoru: float) -> str:
    for seviye, (alt, ust) in RISK_SEVIYELERI.items():
        if alt <= risk_skoru < ust:
            return seviye
    return "Yüksek"


# ════════════════════════════════════════════════════════════════
# UZMAN ÖNERİ ÜRETİCİ
# ════════════════════════════════════════════════════════════════

def _uzman_oneri_uret(risk_seviyesi: str, veri: dict) -> dict:
    yas            = float(veri.get("yas",                  50))
    hipertansiyon  = int(veri.get("hipertansiyon",           0))
    kalp_hastaligi = int(veri.get("kalp_hastaligi",          0))
    bmi            = float(veri.get("vucut_kitle_indeksi",   25))
    seker          = float(veri.get("ortalama_seker",        90))
    sigara         = veri.get("sigara_durumu",               "")

    doktor_onerileri = []
    yasam_tarzi      = []
    izleme           = []

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

    if kalp_hastaligi:
        aci = "ACİL" if risk_seviyesi == "Yüksek" else "Öncelikli"
        doktor_onerileri.append({
            "uzmanlik": "Kardiyoloji",
            "aciliyet": aci,
            "neden"   : "Kalp hastalığı inme riskini 3 kat artırır; düzenli takip şarttır",
        })
        izleme.append(
            "EKG ve ekokardiyografi için kardiyoloji randevusu alın; kalp ilaçlarını aksatmayın"
        )

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

    if bmi > 35:
        doktor_onerileri.append({
            "uzmanlik": "Beslenme ve Diyet / İç Hastalıkları",
            "aciliyet": "Öncelikli",
            "neden"   : f"BMI {bmi:.1f} — ağır obezite kardiyovasküler riskleri artırır",
        })
        yasam_tarzi.append(
            "Ağırlık yönetimi için diyetisyen desteği alın; kalori kısıtlamalı diyet başlatın"
        )
    elif bmi > 30:
        yasam_tarzi.append(
            "BMI idealin üzerinde — haftada 5 gün en az 30 dakika tempolu yürüyüş yapın"
        )

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
    elif sigara == "Hiç İçmedi":
        yasam_tarzi.append(
            "Sigara kullanmamanız kardiyovasküler sağlığınızı önemli ölçüde koruyor "
            "— pasif sigara dumanından da uzak durmaya özen gösterin"
        )

    if yas >= 65:
        yasam_tarzi.append(
            "Ani yüz sarkması, kol-bacak güçsüzlüğü veya konuşma güçlüğünde derhal 112 arayın"
        )
        izleme.append("6 ayda bir nöroloji ve kardiyoloji kontrolü önerilir")
    elif yas >= 50:
        izleme.append(
            "Yılda bir kapsamlı kardiyovasküler risk değerlendirmesi yaptırın"
        )

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

    uzm_listesi = " | ".join(d["uzmanlik"] for d in doktor_onerileri[:2])
    if risk_seviyesi == "Yüksek":
        ozet = f"ACİL: {uzm_listesi} uzmanına bu hafta başvurun."
    elif risk_seviyesi == "Orta":
        ozet = f"Öncelikli: {uzm_listesi} konsültasyonu önerilir."
    else:
        ozet = f"Rutin kontrol: {uzm_listesi} yeterlidir."

    aciliyet_map = {"Yüksek": "ACİL",    "Orta": "Öncelikli", "Düşük": "Rutin"}
    renk_map     = {"Yüksek": "#ef4444", "Orta": "#f59e0b",   "Düşük": "#22c55e"}

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
# train.py'daki ozellik_muhendisligi() ile birebir aynı adımlar
# ════════════════════════════════════════════════════════════════

def _ozellikleri_hazirla(veri: dict, encoders: dict,
                         ozellik_adlari: list) -> np.ndarray:
    df = pd.DataFrame([veri])

    # Sayısal alanları float'a çevir
    for alan in ["yas", "ortalama_seker", "vucut_kitle_indeksi",
                 "hipertansiyon", "kalp_hastaligi"]:
        if alan in df.columns:
            df[alan] = pd.to_numeric(df[alan], errors="coerce").fillna(0)

    # Sigara: ML modeli 2 sınıf (0/1) biliyor
    # "Hiç İçmedi" → 0 (Eski İçici ile eşdeğer ML anlamında)
    # Klinik skorda "Hiç İçmedi" için HR = 1.0 uygulandığından doğruluk korunur.
    if "sigara_durumu" in df.columns:
        df["sigara_durumu"] = df["sigara_durumu"].replace(
            "Hiç İçmedi", "Eski İçici"
        )

    # Kategorik kodlama
    for alan in ["cinsiyet", "evli_mi", "calisma_tipi",
                 "ikamet_tipi", "sigara_durumu"]:
        if alan in df.columns and alan in encoders:
            enc = encoders[alan]
            if isinstance(enc, dict):
                df[alan] = df[alan].astype(str).map(enc).fillna(0).astype(int)
            else:
                try:
                    df[alan] = enc.transform(df[alan].astype(str))
                except (ValueError, AttributeError):
                    df[alan] = 0

    # Özellik mühendisliği — train.py ile birebir aynı
    df = ozellik_muhendisligi(df)

    # Eğitimdeki özellik sırasına hizala
    for ozellik in ozellik_adlari:
        if ozellik not in df.columns:
            df[ozellik] = 0

    return df[ozellik_adlari].values


# ════════════════════════════════════════════════════════════════
# ANA TAHMİN FONKSİYONU
# ════════════════════════════════════════════════════════════════

def hasta_risk_tahmini(hasta_verisi: dict) -> dict:
    """
    Tek bir hasta için inme risk tahmini.

    Hibrit skor = w_klinik × Klinik_HR_skoru + w_ml × ML_skoru
    w_klinik = 0.60 + 0.06 × (risk faktörü sayısı, maks 5)
    → 1 RF: %66 klinik  / %34 ML
    → 3 RF: %78 klinik  / %22 ML
    → 5 RF: %90 klinik  / %10 ML

    Klinik skor Framingham tabanlı çarpımsal HR formülü kullanır;
    ML skoru HistGBM'in predict_proba() çıktısıdır.
    """
    try:
        dogrulama = hasta_verisi_dogrula(hasta_verisi)
        if not dogrulama["gecerli"]:
            return {
                "basarili": False,
                "mesaj"   : "Geçersiz veri: " + "; ".join(dogrulama["hatalar"]),
                "risk_skoru": None, "risk_yuzdesi": None,
                "risk_seviyesi": None, "risk_rengi": None,
                "oneri": None, "tahmin_tarihi": None,
            }

        model, encoders, ozellik_adlari = _model_getir()
        X = _ozellikleri_hazirla(hasta_verisi, encoders, ozellik_adlari)

        # ML olasılığı
        ml_skoru = float(model.predict_proba(X)[0][1])

        # Klinik skor (Framingham — çarpımsal HR)
        klinik_skoru = _klinik_skor_hesapla(hasta_verisi)

        # Adaptif blend ağırlığı
        n_rf = sum([
            int(hasta_verisi.get("hipertansiyon",   0)),
            int(hasta_verisi.get("kalp_hastaligi",  0)),
            1 if hasta_verisi.get("sigara_durumu") == "Halen İçiyor" else 0,
            1 if float(hasta_verisi.get("ortalama_seker",       90)) >= 126 else 0,
            1 if float(hasta_verisi.get("vucut_kitle_indeksi",  25)) >= 30  else 0,
        ])
        # Klinik ağırlık: 0.60 (0 RF) → 0.90 (5 RF)
        w_klinik = min(0.90, 0.60 + 0.06 * n_rf)
        w_ml     = 1.0 - w_klinik

        risk_skoru = min(0.95, w_klinik * klinik_skoru + w_ml * ml_skoru)

        # Klinik minimum eşikler — blend sonrası da uygulanır (ML seyreltmesini önler)
        hiper = int(hasta_verisi.get("hipertansiyon", 0))
        kalp  = int(hasta_verisi.get("kalp_hastaligi", 0))
        sig   = hasta_verisi.get("sigara_durumu", "")
        sek   = float(hasta_verisi.get("ortalama_seker", 90))
        if hiper:
            risk_skoru = max(risk_skoru, 0.12)
        if kalp:
            risk_skoru = max(risk_skoru, 0.15)
        if hiper and kalp:
            risk_skoru = max(risk_skoru, 0.32)
        if (hiper or kalp) and sig == "Halen İçiyor":
            risk_skoru = max(risk_skoru, 0.25)
        if (hiper or kalp) and sek >= 126:
            risk_skoru = max(risk_skoru, 0.22)
        risk_skoru    = min(0.95, risk_skoru)

        risk_seviyesi = _risk_seviyesi_belirle(risk_skoru)
        oneri_dict    = _uzman_oneri_uret(risk_seviyesi, hasta_verisi)

        return {
            "basarili"              : True,
            "risk_skoru"            : round(risk_skoru,       4),
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
            "basarili": False, "mesaj": str(e),
            "risk_skoru": None, "risk_yuzdesi": None,
            "risk_seviyesi": None, "risk_rengi": None,
            "oneri": None, "tahmin_tarihi": None,
        }
    except Exception as e:
        return {
            "basarili": False, "mesaj": f"Model tahmin hatası: {str(e)}",
            "risk_skoru": None, "risk_yuzdesi": None,
            "risk_seviyesi": None, "risk_rengi": None,
            "oneri": None, "tahmin_tarihi": None,
        }


def toplu_tahmin(hasta_listesi: list) -> list:
    sonuclar = []
    for i, hasta in enumerate(hasta_listesi):
        sonuc = hasta_risk_tahmini(hasta)
        sonuc["sira"] = i + 1
        sonuclar.append(sonuc)
    basarili = sum(1 for s in sonuclar if s["basarili"])
    print(f"✅ Toplu tahmin: {basarili}/{len(sonuclar)} başarılı")
    return sonuclar


def mongodb_risk_kaydet(db, hasta_id: str, doktor_id: str,
                        tahmin_sonucu: dict) -> dict:
    if not tahmin_sonucu.get("basarili"):
        return {"basarili": False, "tahmin_id": None,
                "mesaj": "Kaydedilecek geçerli tahmin yok"}
    try:
        mevcut_sayi = db.risk_tahminleri.count_documents({})
        tahmin_no   = f"TP-{str(mevcut_sayi + 1).zfill(5)}"
        belge = {
            "tahmin_no"      : tahmin_no,
            "hasta_id"       : hasta_id,
            "doktor_id"      : doktor_id,
            "model_versiyon" : "2.0-HistGBM",
            "risk_skoru"     : tahmin_sonucu["risk_skoru"],
            "risk_seviyesi"  : tahmin_sonucu["risk_seviyesi"],
            "tahmin_tarihi"  : datetime.now(),
            "oneri"          : tahmin_sonucu["oneri"],
            "onay_durumu"    : "Beklemede",
            "olusturma_tarihi": datetime.now(),
        }
        db.risk_tahminleri.insert_one(belge)
        return {"basarili": True, "tahmin_id": tahmin_no,
                "mesaj": f"Risk tahmini kaydedildi: {tahmin_no}"}
    except Exception as e:
        return {"basarili": False, "tahmin_id": None,
                "mesaj": f"Veritabanı kayıt hatası: {str(e)}"}


def api_risk_tahmini(request_json: dict) -> dict:
    sonuc = hasta_risk_tahmini(request_json)
    if not sonuc["basarili"]:
        return {"hata": sonuc["mesaj"], "durum": "hata"}, 400
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
    print("\n" + "═" * 62)
    print("  TAHMİN MODÜLİ v2.0 TEST")
    print("═" * 62)

    test_hastalari = [
        {
            "ad": "Yüksek Risk (67y, KH+, Obez, Sigara)",
            "yas": 67, "cinsiyet": "Erkek",
            "hipertansiyon": 0, "kalp_hastaligi": 1,
            "evli_mi": "Evet", "calisma_tipi": "Çalışan", "ikamet_tipi": "Kentsel",
            "ortalama_seker": 228.69, "vucut_kitle_indeksi": 36.6,
            "sigara_durumu": "Halen İçiyor",
        },
        {
            "ad": "Düşük Risk (25y, sağlıklı)",
            "yas": 25, "cinsiyet": "Kadın",
            "hipertansiyon": 0, "kalp_hastaligi": 0,
            "evli_mi": "Hayır", "calisma_tipi": "Çalışan", "ikamet_tipi": "Kentsel",
            "ortalama_seker": 80.0, "vucut_kitle_indeksi": 22.5,
            "sigara_durumu": "Hiç İçmedi",
        },
        {
            "ad": "Orta Risk (55y, HT+, Sigara)",
            "yas": 55, "cinsiyet": "Erkek",
            "hipertansiyon": 1, "kalp_hastaligi": 0,
            "evli_mi": "Evet", "calisma_tipi": "Çalışan", "ikamet_tipi": "Kentsel",
            "ortalama_seker": 140, "vucut_kitle_indeksi": 28.5,
            "sigara_durumu": "Halen İçiyor",
        },
        {
            "ad": "Yaşlı sağlıklı (72y, risk faktörü yok)",
            "yas": 72, "cinsiyet": "Kadın",
            "hipertansiyon": 0, "kalp_hastaligi": 0,
            "evli_mi": "Evet", "calisma_tipi": "Serbest", "ikamet_tipi": "Kırsal",
            "ortalama_seker": 95.0, "vucut_kitle_indeksi": 24.0,
            "sigara_durumu": "Hiç İçmedi",
        },
    ]

    for hasta in test_hastalari:
        ad = hasta.pop("ad")
        sonuc = hasta_risk_tahmini(hasta)
        print(f"\n{'─'*50}")
        print(f"  {ad}")
        if sonuc["basarili"]:
            print(f"  Risk  : %{sonuc['risk_yuzdesi']:.1f}  [{sonuc['risk_seviyesi']}]")
            print(f"  Öneri : {sonuc['oneri']}")
        else:
            print(f"  ❌ {sonuc['mesaj']}")

    print("\n" + "═" * 62 + "\n")
