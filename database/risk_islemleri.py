"""
Modül Adı: risk_islemleri.py
Açıklama : ML modelinden gelen inme risk sonuçlarını veritabanına
           kaydeder ve doktora gösterilecek öneri listesini üretir.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0

Akış
────
  1. ML modeli  predict.py üzerinden risk_skoru (0.0 – 1.0) üretir.
  2. Bu modül skoru yorumlar, seviyeyi belirler, önerileri oluşturur.
  3. Sonucu  inme_risk_tahminleri  koleksiyonuna kaydeder.
  4. Doktora gösterilmek üzere tam sonuç nesnesini döndürür.
"""

from datetime import datetime
from database.connection import baglanti_olustur


# ════════════════════════════════════════════════════════════════
# RİSK SEVİYESİ VE ÖNERİLER
# ════════════════════════════════════════════════════════════════

ONERILER = {
    "Düşük": [
        "Düzenli yıllık check-up yaptırın.",
        "Haftada en az 150 dakika orta yoğunlukta egzersiz yapın.",
        "Sağlıklı ve dengeli beslenmeye devam edin.",
        "Sigara kullanmıyorsanız başlamayın.",
        "Kan basıncı ve kan şekerinizi yılda bir ölçtürün.",
    ],
    "Orta": [
        "⚠️  Kardiyoloji veya Nöroloji uzmanına başvurunuz.",
        "3 ayda bir kan basıncı, kan şekeri ve kolesterol kontrolü yaptırın.",
        "Sigara kullanıyorsanız bırakma programına katılın.",
        "Tuz tüketimini günlük 5 gr altına indirin.",
        "Aktif yaşam tarzı benimseyin; oturma sürelerini kısaltın.",
        "Stres yönetimi için psikolojik destek alabilirsiniz.",
        "Düzenli ilaç kullanıyorsanız kesinlikle aksatmayın.",
    ],
    "Yüksek": [
        "🚨  ACİL: En kısa sürede nöroloji uzmanına başvurun.",
        "Kan basıncınızı günlük olarak ölçün ve kaydedin.",
        "Ani baş ağrısı, konuşma güçlüğü veya uyuşma hissinde 112'yi arayın.",
        "Mevcut ilaçlarınızı doktor onayı olmadan kesmeyin.",
        "Sigara ve alkolü derhal bırakın.",
        "Yüksek yağlı, tuzlu ve şekerli gıdalardan kaçının.",
        "Yalnız yaşıyorsanız yakınlarınızı durumunuzdan haberdar edin.",
        "Hastane takibi için randevu alın, muayeneyi ertelemeyin.",
    ],
}


def _risk_seviyesi_belirle(skor: float) -> str:
    """
    Risk skorunu (0.0 – 1.0) seviyeye dönüştürür.
    Eşikler predict.py ile aynıdır.

    < 0.10  → Düşük
    < 0.30  → Orta
    ≥ 0.30  → Yüksek
    """
    if skor < 0.10:
        return "Düşük"
    elif skor < 0.30:
        return "Orta"
    return "Yüksek"


def _tahmin_id_olustur(db) -> str:
    toplam = db.inme_risk_tahminleri.count_documents({})
    return f"RT-{str(toplam + 1).zfill(5)}"


# ════════════════════════════════════════════════════════════════
# RİSK KAYDETME
# ════════════════════════════════════════════════════════════════

def risk_sonucu_kaydet(
    hasta_id: str,
    doktor_id: str,
    risk_skoru: float,
    model_girdileri: dict,
    model_surumu: str = "RandomForest-v1.0",
    doktor_notu: str = "",
) -> dict:
    """
    ML modelinden gelen risk skorunu veritabanına kaydeder.

    Args:
        hasta_id        : HS-XXXXX formatında hasta ID
        doktor_id       : DR-XXXXX formatında doktor ID
        risk_skoru      : 0.0 – 1.0 arası olasılık (modelden gelir)
        model_girdileri : Modele giren parametre sözlüğü
        model_surumu    : Hangi model versiyonu kullanıldı
        doktor_notu     : Doktorun eklemek istediği not

    Returns:
        dict: {
            "basarili"     : True/False,
            "tahmin_id"    : "RT-XXXXX",
            "risk_skoru"   : 0.754,
            "risk_yuzdesi" : 75.4,
            "risk_seviyesi": "Yüksek",
            "oneriler"     : [...],
            "mesaj"        : "...",
        }
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False, "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # Hasta var mı?
    if db.hastalar.find_one({"hasta_id": hasta_id}) is None:
        return {"basarili": False,
                "mesaj": f"'{hasta_id}' ID'li hasta bulunamadı."}

    # Skor aralığı geçerli mi?
    if not (0.0 <= risk_skoru <= 1.0):
        return {"basarili": False,
                "mesaj": "Risk skoru 0.0 – 1.0 arasında olmalıdır."}

    seviye   = _risk_seviyesi_belirle(risk_skoru)
    yuzdesi  = round(risk_skoru * 100, 2)
    oneriler = ONERILER[seviye]

    try:
        tahmin_id = _tahmin_id_olustur(db)

        belge = {
            "tahmin_id":      tahmin_id,
            "hasta_id":       hasta_id,
            "doktor_id":      doktor_id,
            "model_surumu":   model_surumu,

            "risk_skoru":     round(risk_skoru, 4),
            "risk_yuzdesi":   yuzdesi,
            "risk_seviyesi":  seviye,

            "model_girdileri": model_girdileri,
            "oneriler":        oneriler,

            "tahmin_tarihi":  datetime.now(),
            "doktor_notu":    doktor_notu.strip(),
            "onay_durumu":    "Beklemede",
        }

        db.inme_risk_tahminleri.insert_one(belge)

        print(f"✅ Risk tahmini kaydedildi → {tahmin_id}"
              f"  |  Hasta: {hasta_id}"
              f"  |  Seviye: {seviye}  (%{yuzdesi})")

        return {
            "basarili":      True,
            "tahmin_id":     tahmin_id,
            "risk_skoru":    round(risk_skoru, 4),
            "risk_yuzdesi":  yuzdesi,
            "risk_seviyesi": seviye,
            "oneriler":      oneriler,
            "mesaj":         f"Risk tahmini kaydedildi. Seviye: {seviye} (%{yuzdesi})",
        }

    except Exception as e:
        return {"basarili": False, "mesaj": f"Hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# VERİ OKUMA
# ════════════════════════════════════════════════════════════════

def doktor_risk_gecmisi(doktor_id: str, limit: int = 100, offset: int = 0) -> list:
    """
    Belirtilen doktora ait tüm risk tahminlerini döndürür.
    En yeniden eskiye sıralı.

    Returns:
        list: Tahmin kayıtları listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    return list(
        db.inme_risk_tahminleri
        .find({"doktor_id": doktor_id}, {"_id": 0})
        .sort("tahmin_tarihi", -1)
        .skip(offset)
        .limit(limit)
    )


def hasta_risk_gecmisi(hasta_id: str, limit: int = 10) -> list:
    """
    Hastanın geçmiş risk tahminlerini en yeniden eskiye sıralar.

    Returns:
        list: Tahmin kayıtları listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    return list(
        db.inme_risk_tahminleri
        .find({"hasta_id": hasta_id}, {"_id": 0})
        .sort("tahmin_tarihi", -1)
        .limit(limit)
    )


def yuksek_riskli_hastalar(limit: int = 100) -> list:
    """
    Sistemdeki yüksek riskli hastaları listeler.
    Risk skoru en yüksekten en düşüğe sıralanır.

    Returns:
        list: Tahmin + hasta adı birleştirilmiş liste
    """
    db = baglanti_olustur()
    if db is None:
        return []

    tahminler = list(
        db.inme_risk_tahminleri
        .find({"risk_seviyesi": "Yüksek"}, {"_id": 0})
        .sort("risk_skoru", -1)
        .limit(limit)
    )

    # Her tahmine hasta adını ekle
    for t in tahminler:
        hasta = db.hastalar.find_one(
            {"hasta_id": t["hasta_id"]},
            {"ad": 1, "soyad": 1, "yas": 1, "_id": 0}
        )
        if hasta:
            t["hasta_adi"] = f"{hasta['ad']} {hasta['soyad']}"
            t["yas"]       = hasta.get("yas", "-")

    return tahminler


def risk_istatistikleri() -> dict:
    """
    Sistemdeki tüm tahminlerin özet istatistiklerini döndürür.

    Returns:
        dict: Seviye bazında sayılar ve ortalama skor
    """
    db = baglanti_olustur()
    if db is None:
        return {}

    pipeline = [
        {"$group": {
            "_id":           "$risk_seviyesi",
            "sayi":          {"$sum": 1},
            "ort_skor":      {"$avg": "$risk_skoru"},
            "en_yuksek":     {"$max": "$risk_skoru"},
        }},
        {"$sort": {"ort_skor": -1}}
    ]

    sonuclar   = list(db.inme_risk_tahminleri.aggregate(pipeline))
    toplam     = db.inme_risk_tahminleri.count_documents({})

    return {
        "toplam_tahmin": toplam,
        "seviye_dagilimi": {
            r["_id"]: {
                "sayi":      r["sayi"],
                "oran":      round(r["sayi"] / toplam * 100, 1) if toplam else 0,
                "ort_skor":  round(r["ort_skor"] * 100, 1),
                "en_yuksek": round(r["en_yuksek"] * 100, 1),
            }
            for r in sonuclar
        }
    }


# ════════════════════════════════════════════════════════════════
# HIZLI TEST
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    sonuc = risk_sonucu_kaydet(
        hasta_id        = "HS-00001",
        doktor_id       = "DR-00001",
        risk_skoru      = 0.76,
        model_girdileri = {
            "yas": 58, "cinsiyet": "Erkek",
            "hipertansiyon": 1, "kalp_hastaligi": 0,
            "ortalama_seker": 148.5, "vucut_kitle_indeksi": 29.3,
            "sigara_durumu": "Halen İçiyor",
        },
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
