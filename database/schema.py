"""
Modül Adı: schema.py
Açıklama : İnme Risk Sistemi için MongoDB koleksiyonlarını,
           JSON Schema doğrulama kurallarını ve performans
           indekslerini oluşturur.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0

Koleksiyonlar
─────────────
  hastalar            → Hasta kimlik ve demografik bilgileri
  tibbi_bilgiler      → Muayenede ölçülen klinik değerler
  yasam_tarzi         → Sigara, egzersiz, medeni durum vb.
  inme_risk_tahminleri→ ML modelinin ürettiği risk skoru ve öneriler
  doktorlar           → Sistemi kullanan doktor hesapları
"""

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import OperationFailure, CollectionInvalid
from database.connection import baglanti_olustur


# ════════════════════════════════════════════════════════════════
# KOLEKSIYON ŞEMALARI  (JSON Schema doğrulama kuralları)
# ════════════════════════════════════════════════════════════════

SEMA = {

    # ── 1. HASTALAR ──────────────────────────────────────────────
    "hastalar": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["hasta_id", "ad", "soyad", "yas", "cinsiyet"],
                "properties": {
                    "hasta_id":   {
                        "bsonType": "string",
                        "description": "Benzersiz hasta numarası  (HS-00001)"
                    },
                    "ad":         {"bsonType": "string"},
                    "soyad":      {"bsonType": "string"},
                    "yas":        {
                        "bsonType": "int",
                        "minimum": 0,
                        "maximum": 130,
                        "description": "Yaş 0-130 arasında olmalı"
                    },
                    "cinsiyet": {
                        "enum": ["Erkek", "Kadın"],
                        "description": "Sadece 'Erkek' veya 'Kadın'"
                    },
                    "telefon":        {"bsonType": "string"},
                    "email":          {"bsonType": "string"},
                    "dogum_tarihi":   {"bsonType": "string"},  # "YYYY-MM-DD"
                    "kayit_tarihi":   {"bsonType": "date"},
                    "aktif":          {"bsonType": "bool"},
                }
            }
        },
        "validationAction": "warn"   # Kural ihlalinde hata değil uyarı ver
    },

    # ── 2. TIBBİ BİLGİLER ────────────────────────────────────────
    #   Doktor muayenede bu verileri sisteme girer.
    #   ML modeli bu koleksiyondaki değerleri kullanarak risk hesaplar.
    "tibbi_bilgiler": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["kayit_id", "hasta_id", "muayene_tarihi"],
                "properties": {
                    "kayit_id":         {"bsonType": "string"},
                    "hasta_id":         {"bsonType": "string"},
                    "doktor_id":        {"bsonType": "string"},
                    "muayene_tarihi":   {"bsonType": "date"},

                    # ─ Klinik Ölçümler ─────────────────────────
                    "hipertansiyon": {
                        "bsonType": "int",
                        "enum": [0, 1],
                        "description": "0=Yok  1=Var"
                    },
                    "kalp_hastaligi": {
                        "bsonType": "int",
                        "enum": [0, 1],
                        "description": "0=Yok  1=Var"
                    },
                    "ortalama_seker": {
                        "bsonType": "double",
                        "minimum": 0,
                        "description": "mg/dL cinsinden ortalama kan şekeri"
                    },
                    "vucut_kitle_indeksi": {
                        "bsonType": "double",
                        "minimum": 0,
                        "description": "BMI (kg/m²)"
                    },

                    # ─ Doktor Notları ───────────────────────────
                    "sikayet":          {"bsonType": "string"},
                    "tani_notu":        {"bsonType": "string"},
                    "ilac_recetesi":    {"bsonType": "array"},
                    "olusturma_tarihi": {"bsonType": "date"},
                }
            }
        },
        "validationAction": "warn"
    },

    # ── 3. YAŞAM TARZI ────────────────────────────────────────────
    "yasam_tarzi": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["hasta_id"],
                "properties": {
                    "hasta_id": {"bsonType": "string"},
                    "evli_mi": {
                        "enum": ["Evet", "Hayır", "Eski", "Hiç"],
                        "description": "Medeni durum"
                    },
                    "calisma_tipi": {
                        "enum": [
                            "Özel Sektör", "Kamu",
                            "Serbest Meslek", "Emekli",
                            "Öğrenci", "İşsiz", "Çocuk"
                        ]
                    },
                    "ikamet_tipi": {
                        "enum": ["Kentsel", "Kırsal"]
                    },
                    "sigara_durumu": {
                        "enum": ["Hiç İçmedi", "Eski İçici", "Halen İçiyor"],
                        "description": "Tütün kullanım durumu"
                    },
                    "guncelleme_tarihi": {"bsonType": "date"},
                }
            }
        },
        "validationAction": "warn"
    },

    # ── 4. İNME RİSK TAHMİNLERİ ──────────────────────────────────
    #   ML modelinden gelen sonuçlar burada saklanır.
    "inme_risk_tahminleri": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "tahmin_id", "hasta_id",
                    "risk_skoru", "risk_seviyesi", "tahmin_tarihi"
                ],
                "properties": {
                    "tahmin_id":     {"bsonType": "string"},
                    "hasta_id":      {"bsonType": "string"},
                    "doktor_id":     {"bsonType": "string"},
                    "model_surumu":  {"bsonType": "string"},

                    "risk_skoru": {
                        "bsonType": "double",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "0.0 – 1.0 arası olasılık değeri"
                    },
                    "risk_seviyesi": {
                        "enum": ["Düşük", "Orta", "Yüksek"],
                        "description": "Düşük<0.33  Orta<0.66  Yüksek≥0.66"
                    },
                    "risk_yuzdesi": {
                        "bsonType": "double",
                        "description": "risk_skoru × 100  (örn. 75.4)"
                    },

                    # Modele giren parametrelerin anlık görüntüsü
                    "model_girdileri": {"bsonType": "object"},

                    # Doktora gösterilen öneri listesi
                    "oneriler": {
                        "bsonType": "array",
                        "description": "Risk seviyesine göre yapılması gerekenler"
                    },

                    "tahmin_tarihi":   {"bsonType": "date"},
                    "doktor_notu":     {"bsonType": "string"},
                    "onay_durumu": {
                        "enum": ["Beklemede", "Onaylandı", "Reddedildi"]
                    },
                }
            }
        },
        "validationAction": "warn"
    },

    # ── 5. DOKTORLAR ─────────────────────────────────────────────
    "doktorlar": {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["doktor_id", "ad", "soyad", "uzmanlik"],
                "properties": {
                    "doktor_id":     {"bsonType": "string"},
                    "ad":            {"bsonType": "string"},
                    "soyad":         {"bsonType": "string"},
                    "uzmanlik":      {"bsonType": "string"},
                    "email":         {"bsonType": "string"},
                    "sifre_hash":    {"bsonType": "string"},
                    "aktif":         {"bsonType": "bool"},
                    "kayit_tarihi":  {"bsonType": "date"},
                }
            }
        },
        "validationAction": "warn"
    },
}


# ════════════════════════════════════════════════════════════════
# İNDEKS TANIMLARI
# ════════════════════════════════════════════════════════════════

INDEKSLER = {
    "hastalar": [
        ([("hasta_id",   ASCENDING)], {"unique": True,  "name": "idx_hasta_id_unique"}),
        ([("ad",         ASCENDING),
          ("soyad",      ASCENDING)], {"name": "idx_ad_soyad"}),
        ([("yas",        ASCENDING)], {"name": "idx_yas"}),
        ([("kayit_tarihi", DESCENDING)], {"name": "idx_kayit_tarihi"}),
    ],
    "tibbi_bilgiler": [
        ([("kayit_id",       ASCENDING)],  {"unique": True, "name": "idx_kayit_id_unique"}),
        ([("hasta_id",       ASCENDING),
          ("muayene_tarihi", DESCENDING)], {"name": "idx_hasta_muayene"}),
        ([("doktor_id",      ASCENDING)],  {"name": "idx_doktor_id"}),
        ([("muayene_tarihi", DESCENDING)], {"name": "idx_muayene_tarihi"}),
    ],
    "yasam_tarzi": [
        ([("hasta_id", ASCENDING)], {"unique": True, "name": "idx_yt_hasta_id_unique"}),
    ],
    "inme_risk_tahminleri": [
        ([("tahmin_id",    ASCENDING)],  {"unique": True, "name": "idx_tahmin_id_unique"}),
        ([("hasta_id",    ASCENDING),
          ("tahmin_tarihi", DESCENDING)], {"name": "idx_hasta_tahmin"}),
        ([("risk_seviyesi", ASCENDING)], {"name": "idx_risk_seviyesi"}),
        ([("risk_skoru",    DESCENDING)], {"name": "idx_risk_skoru"}),
        ([("tahmin_tarihi", DESCENDING)], {"name": "idx_tahmin_tarihi"}),
    ],
    "doktorlar": [
        ([("doktor_id", ASCENDING)], {"unique": True, "name": "idx_doktor_id_unique"}),
        ([("email",     ASCENDING)], {"unique": True, "name": "idx_doktor_email_unique"}),
    ],
}


# ════════════════════════════════════════════════════════════════
# KURULUM FONKSİYONU
# ════════════════════════════════════════════════════════════════

def sema_olustur():
    """
    Veritabanı koleksiyonlarını ve indekslerini oluşturur.
    Zaten varsa atlar (idempotent).

    Returns:
        bool: Başarılıysa True, hata olursa False.
    """
    db = baglanti_olustur()
    if db is None:
        return False

    mevcut = set(db.list_collection_names())
    print("\n" + "=" * 55)
    print("  VERİTABANI ŞEMA KURULUMU BAŞLIYOR")
    print("=" * 55)

    # ── Koleksiyonları oluştur ──────────────────────────────────
    print("\n[1/2] Koleksiyonlar oluşturuluyor...")
    for ad, ayarlar in SEMA.items():
        if ad in mevcut:
            print(f"  ATLA  : {ad}  (zaten var)")
            continue
        try:
            db.create_collection(ad, **ayarlar)
            print(f"  TAMAM : {ad}  oluşturuldu")
        except CollectionInvalid:
            print(f"  ATLA  : {ad}  (zaten var)")
        except Exception as e:
            print(f"  HATA  : {ad}  → {e}")

    # ── İndeksleri oluştur ─────────────────────────────────────
    print("\n[2/2] İndeksler oluşturuluyor...")
    for koleksiyon_adi, indeks_listesi in INDEKSLER.items():
        kol = db[koleksiyon_adi]
        for alanlar, secenekler in indeks_listesi:
            try:
                kol.create_index(alanlar, **secenekler)
                print(f"  TAMAM : {koleksiyon_adi}.{secenekler['name']}")
            except OperationFailure as e:
                if "already exists" in str(e):
                    print(f"  ATLA  : {secenekler['name']}  (zaten var)")
                else:
                    print(f"  HATA  : {e}")

    # ── Özet ───────────────────────────────────────────────────
    print("\n" + "─" * 55)
    print("DURUM  | KOLEKSİYON               | BELGE | İNDEKS")
    print("─" * 55)
    for ad in sorted(SEMA.keys()):
        kol   = db[ad]
        belge = kol.count_documents({})
        indx  = len(list(kol.list_indexes()))
        print(f"  {'✅' if ad in db.list_collection_names() else '❌'}  "
              f"  {ad:<25}  {belge:>5}  {indx:>6}")
    print("─" * 55)
    print("Şema kurulumu tamamlandı.\n")
    return True


if __name__ == "__main__":
    sema_olustur()