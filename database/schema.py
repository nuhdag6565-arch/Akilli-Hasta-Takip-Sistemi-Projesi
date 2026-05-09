"""
Modül Adı: Database Schema
Açıklama: MongoDB veritabanı koleksiyonlarının şemasını oluşturur ve optimize edilmiş indeksler tanımlar
Sorumlu: Nuh Dağ (Veritabanı)
Tarih: 2026-05-05
Version: 2.0
"""

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import OperationFailure
from database.connection import baglanti_olustur

# ============================================================================
# VERİTABANI ŞEMA TASARIMI
# ============================================================================

KOLEKSIYON_ŞEMALARI = {
    "kullanicilar": {
        "description": "Sistem kullanıcıları (Doktor, Yönetici, Teknisyen)",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["kullanici_no", "ad", "soyad", "email", "rol", "aktif"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "kullanici_no": {"bsonType": "string", "description": "Benzersiz kullanıcı ID (KL-0001)"},
                    "ad": {"bsonType": "string", "description": "Kullanıcının adı"},
                    "soyad": {"bsonType": "string", "description": "Kullanıcının soyadı"},
                    "email": {"bsonType": "string", "description": "E-posta adresi"},
                    "tc_no": {"bsonType": "string", "description": "TC kimlik numarası (opsiyonel)"},
                    "telefon": {"bsonType": "string", "description": "Telefon numarası"},
                    "rol": {"enum": ["doktor", "yönetici", "teknisyen", "hemşire"], "description": "Sistem rolü"},
                    "uzmanlık_alani": {"bsonType": "string", "description": "Doktor ise uzmanlık alanı"},
                    "departman": {"bsonType": "string", "description": "Çalıştığı departman"},
                    "sifre_hash": {"bsonType": "string", "description": "Kullanıcı şifre hash'i"},
                    "aktif": {"bsonType": "bool", "description": "Kullanıcı aktif mi?"},
                    "kayit_tarihi": {"bsonType": "date", "description": "Kayıt tarihi"},
                    "son_giris_tarihi": {"bsonType": "date", "description": "Son giriş tarihi"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Profil oluşturma tarihi"}
                }
            }
        }
    },
    
    "hastalar": {
        "description": "Hastalar - Demografik ve temel sağlık bilgileri",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["hasta_no", "tc_no", "ad", "soyad", "yas", "cinsiyet"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "hasta_no": {"bsonType": "string", "description": "Benzersiz hasta ID (HS-0001)"},
                    "tc_no": {"bsonType": "string", "description": "TC kimlik numarası (unique)"},
                    "ad": {"bsonType": "string", "description": "Hastanın adı"},
                    "soyad": {"bsonType": "string", "description": "Hastanın soyadı"},
                    "dogum_tarihi": {"bsonType": "date", "description": "Doğum tarihi"},
                    "dogum_yili": {"bsonType": "int", "minimum": 1900, "maximum": 2100, "description": "Doğum yılı"},
                    "yas": {"bsonType": "int", "minimum": 0, "maximum": 150, "description": "Yaş (0-150)"},
                    "cinsiyet": {"enum": ["Erkek", "Kadın"], "description": "Cinsiyet"},
                    "telefon": {"bsonType": "string", "description": "Telefon numarası"},
                    "email": {"bsonType": "string", "description": "E-posta adresi"},
                    "evli_mi": {"bsonType": "string", "description": "Medeni durum"},
                    "calisma_tipi": {"bsonType": "string", "description": "İstihdam türü"},
                    "ikamet_tipi": {"bsonType": "string", "description": "Yaşanılan bölge türü"},
                    "adres": {"bsonType": "string", "description": "Ev adresi"},
                    "sehir": {"bsonType": "string", "description": "Şehir"},
                    "ilce": {"bsonType": "string", "description": "İlçe"},
                    "posta_kodu": {"bsonType": "string", "description": "Posta kodu"},
                    "acil_iletisim": {"bsonType": "string", "description": "Acil iletişim kişi"},
                    "acil_telefon": {"bsonType": "string", "description": "Acil telefon numarası"},
                    "kan_grubu": {"enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Bilinmiyor"], "description": "Kan grubu"},
                    "sigorta_numarasi": {"bsonType": "string", "description": "Sağlık sigortası numarası"},
                    "aktif": {"bsonType": "bool", "description": "Hasta aktif mi?"},
                    "basvuru_tarihi": {"bsonType": "date", "description": "Başvuru tarihi"},
                    "kayit_tarihi": {"bsonType": "date", "description": "Kayıt tarihi"},
                    "son_ziyaret_tarihi": {"bsonType": "date", "description": "Son ziyaret tarihi"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Sistem kaydı oluşturma tarihi"}
                }
            }
        }
    },
    
    "tibbi_kayitlar": {
        "description": "Tıbbi veriler - Her vizit/muayene sonuçları",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["kayit_no", "hasta_id", "kayit_tarihi"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "kayit_no": {"bsonType": "string", "description": "Benzersiz tıbbi kayıt ID (TK-0001)"},
                    "hasta_id": {"bsonType": "string", "description": "Hasta ID referansı"},
                    "doktor_id": {"bsonType": "string", "description": "Doktor ID referansı"},
                    "kayit_tarihi": {"bsonType": "date", "description": "Muayene tarihi"},
                    "ziyaret_tipi": {"enum": ["Rutin Kontrol", "Acil", "Takip", "Danışma"], "description": "Ziyaret türü"},
                    "sikayet": {"bsonType": "string", "description": "Hasta şikayetleri"},
                    "tanı": {"bsonType": "string", "description": "Doktor tanısı"},
                    "hipertansiyon": {"bsonType": "bool", "description": "Hipertansiyon var mı?"},
                    "kalp_hastaligi": {"bsonType": "bool", "description": "Kalp hastalığı var mı?"},
                    "ortalama_seker": {"bsonType": "double", "description": "Ortalama kan şekeri seviyesi"},
                    "vucut_kitle_indeksi": {"bsonType": "double", "description": "BMI değeri"},
                    "ilaç_reçetesi": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "ilaç_adi": {"bsonType": "string"},
                                "doz": {"bsonType": "string"},
                                "sıklık": {"bsonType": "string"},
                                "süre": {"bsonType": "int"}
                            }
                        },
                        "description": "Reçete edilen ilaçlar"
                    },
                    "tıbbi_testler": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Önerilen tıbbi testler"
                    },
                    "notlar": {"bsonType": "string", "description": "Doktor notları"},
                    "tavsiye": {"bsonType": "string", "description": "Sağlık tavsiyesi"},
                    "sonraki_randevu": {"bsonType": "date", "description": "Sonraki randevu tarihi"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Kayıt oluşturma tarihi"}
                }
            }
        }
    },
    
    "yasam_tarzi": {
        "description": "Yaşam tarzı verileri - Sigara, alkol, egzersiz, beslenme",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["hasta_id"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "hasta_id": {"bsonType": "string", "description": "Hasta ID referansı"},
                    "sigara_durumu": {"enum": ["Hiç İçmedi", "Eski İçici", "Halen İçiyor"], "description": "Sigara kullanım durumu"},
                    "sigarayı_birakma_yili": {"bsonType": "int", "description": "Sigara bırakıldı mı? Hangi yılda?"},
                    "gunluk_sigara": {"bsonType": "int", "description": "Günlük sigara sayısı"},
                    "alkol_durumu": {"enum": ["Hiç", "Nadiren", "Hafta Sonu", "Düzenli"], "description": "Alkol tüketimi"},
                    "gunluk_alkol": {"bsonType": "string", "description": "Günlük alkol tüketim miktarı"},
                    "egzersiz_durumu": {"enum": ["Hiç", "Nadiren", "Haftada 1-2", "Haftada 3+"], "description": "Egzersiz sıklığı"},
                    "gunluk_adim": {"bsonType": "int", "description": "Ortalama günlük adım sayısı"},
                    "beslenme_tipi": {"enum": ["Dengeli", "Yüksek Tuz", "Yüksek Yağ", "Yüksek Şeker"], "description": "Beslenme şekli"},
                    "gunluk_su": {"bsonType": "int", "description": "Günlük su tüketimi (ml)"},
                    "uyku_saati": {"bsonType": "int", "description": "Günlük uyku saati"},
                    "stres_seviyesi": {"bsonType": "int", "minimum": 1, "maximum": 10, "description": "Stres seviyesi (1-10)"},
                    "sosyal_aktivite": {"enum": ["Çok Aktif", "Aktif", "Orta", "Pasif"], "description": "Sosyal aktivite seviyesi"},
                    "is_stresi": {"bsonType": "bool", "description": "İş stresi yaşıyor mu?"},
                    "guncellenme_tarihi": {"bsonType": "date", "description": "Son güncelleme tarihi"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Kayıt oluşturma tarihi"}
                }
            }
        }
    },
    
    "risk_tahminleri": {
        "description": "ML model tahminleri - İnme riski puanları",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["tahmin_no", "hasta_id", "risk_skoru", "tahmin_tarihi"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "tahmin_no": {"bsonType": "string", "description": "Benzersiz tahmin ID (TP-0001)"},
                    "hasta_id": {"bsonType": "string", "description": "Hasta ID referansı"},
                    "model_versiyon": {"bsonType": "string", "description": "Kullanılan model sürümü"},
                    "risk_skoru": {"bsonType": "double", "minimum": 0.0, "maximum": 1.0, "description": "Risk puanı (0.0-1.0)"},
                    "risk_seviyesi": {"enum": ["Düşük", "Orta", "Yüksek"], "description": "Risk kategorisi"},
                    "tahmin_tarihi": {"bsonType": "date", "description": "Tahmin yapılan tarih"},
                    "giriş_parametreleri": {
                        "bsonType": "object",
                        "description": "Modele girilen parametreler"
                    },
                    "oneri": {"bsonType": "string", "description": "Sistem önerisi"},
                    "doktor_notu": {"bsonType": "string", "description": "Doktor görüşü"},
                    "onay_durumu": {"enum": ["Beklemede", "Onaylandı", "Reddedildi"], "description": "Doktor onayı"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Tahmin oluşturma tarihi"}
                }
            }
        }
    },
    
    "yasam_tarzi_degisiklikleri": {
        "description": "Yaşam tarzı değişikliklerinin loglanması (audit trail)",
        "validators": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["hasta_id", "degisiklik_tarihi", "degisiklik_turu"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "hasta_id": {"bsonType": "string", "description": "Hasta ID referansı"},
                    "degisiklik_turu": {"bsonType": "string", "description": "Ne değiştirildi?"},
                    "eski_deger": {"bsonType": "string", "description": "Eski değer"},
                    "yeni_deger": {"bsonType": "string", "description": "Yeni değer"},
                    "degisiklik_tarihi": {"bsonType": "date", "description": "Değişiklik tarihi"},
                    "dokumanlar": {"bsonType": "string", "description": "Belge adı"},
                    "olusturma_tarihi": {"bsonType": "date", "description": "Log oluşturma tarihi"}
                }
            }
        }
    }
}

# ============================================================================
# İNDEKS TANIMI
# ============================================================================

INDEKSLER = {
    "kullanicilar": [
        ({"kullanici_no": ASCENDING}, {"unique": True}),
        ({"email": ASCENDING}, {"unique": True}),
        ({"tc_no": ASCENDING}, {}),
        ({"rol": ASCENDING}, {}),
        ({"aktif": ASCENDING}, {}),
    ],
    
    "hastalar": [
        ({"hasta_no": ASCENDING}, {"unique": True}),
        ({"tc_no": ASCENDING}, {"unique": True}),
        ({"ad": ASCENDING, "soyad": ASCENDING}, {}),
        ({"email": ASCENDING}, {}),
        ({"aktif": ASCENDING, "kayit_tarihi": DESCENDING}, {}),
    ],
    
    "tibbi_kayitlar": [
        ({"kayit_no": ASCENDING}, {"unique": True}),
        ({"hasta_id": ASCENDING, "kayit_tarihi": DESCENDING}, {}),
        ({"doktor_id": ASCENDING}, {}),
        ({"kayit_tarihi": DESCENDING}, {}),
        ({"ziyaret_tipi": ASCENDING}, {}),
    ],
    
    "yasam_tarzi": [
        ({"hasta_id": ASCENDING}, {"unique": True}),
        ({"guncellenme_tarihi": DESCENDING}, {}),
        ({"sigara_durumu": ASCENDING}, {}),
        ({"egzersiz_durumu": ASCENDING}, {}),
    ],
    
    "risk_tahminleri": [
        ({"tahmin_no": ASCENDING}, {"unique": True}),
        ({"hasta_id": ASCENDING, "tahmin_tarihi": DESCENDING}, {}),
        ({"risk_seviyesi": ASCENDING}, {}),
        ({"risk_skoru": DESCENDING}, {}),
        ({"tahmin_tarihi": DESCENDING}, {}),
    ],
    
    "yasam_tarzi_degisiklikleri": [
        ({"hasta_id": ASCENDING, "degisiklik_tarihi": DESCENDING}, {}),
        ({"degisiklik_turu": ASCENDING}, {}),
    ]
}

# ============================================================================
# FONKSİYONLAR
# ============================================================================

def koleksiyonlari_olustur():
    """
    Veritabanı koleksiyonlarını JSON Schema validators ile oluşturur.
    
    Returns:
        bool: Başarılı olup olmadığını gösterir
    """
    db = baglanti_olustur()
    if db is None:
        print("ERROR: Database connection failed.")
        return False

    print("Database schema creation started...\n")
    mevcut = db.list_collection_names()

    for koleksiyon_adi, schema in KOLEKSIYON_ŞEMALARI.items():
        if koleksiyon_adi in mevcut:
            print(f"SKIP: {koleksiyon_adi} collection already exists.")
            continue
        
        try:
            validator = schema.get("validators", {})
            if validator:
                db.create_collection(koleksiyon_adi, validator=validator)
            else:
                db.create_collection(koleksiyon_adi)
            print(f"OK: {koleksiyon_adi} collection created.")
        except Exception as e:
            print(f"ERROR: Failed to create {koleksiyon_adi}: {str(e)}")

    print("\n" + "="*60)
    print("INDEXES ARE BEING CREATED...")
    print("="*60 + "\n")
    
    for koleksiyon_adi, indexler in INDEKSLER.items():
        if koleksiyon_adi not in db.list_collection_names():
            print(f"SKIP: {koleksiyon_adi} collection not found.")
            continue
        
        koleksiyon = db[koleksiyon_adi]
        for index_spec, options in indexler:
            try:
                index_adi = koleksiyon.create_index(list(index_spec.items()), **options)
                print(f"OK: {koleksiyon_adi} index created: {index_adi}")
            except OperationFailure as e:
                if "already exists" not in str(e):
                    print(f"ERROR: {koleksiyon_adi} index error: {str(e)}")

    print("\n" + "="*60)
    print("DATABASE STATUS")
    print("="*60)
    print("Database Name:", db.name)
    print(f"Total Collections: {len(db.list_collection_names())}")
    print("Collections:")
    for k in sorted(db.list_collection_names()):
        koleksiyon = db[k]
        belge_sayisi = koleksiyon.count_documents({})
        index_sayisi = len(list(koleksiyon.list_indexes()))
        print(f"  {k:25} | {belge_sayisi:6} documents | {index_sayisi} indexes")
    
    return True

if __name__ == "__main__":
    koleksiyonlari_olustur()