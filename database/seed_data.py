"""
Modül Adı: Seed Data Loader
Açıklama: Veritabanını örnek verilerle doldurur - Doktorlar, Hastalar, Tıbbi Kayıtlar, Yaşam Tarzı
Sorumlu: Nuh Dağ (Veritabanı)
Tarih: 2026-05-05
Version: 2.0
"""

import pandas as pd
from datetime import datetime, timedelta
import random
from database.connection import baglanti_olustur
from database.schema import koleksiyonlari_olustur

# ============================================================================
# ÖRNEK VERİ KÜMELERİ
# ============================================================================

DOKTOR_LISTESI = [
    {
        "kullanici_no": "KL-0001",
        "ad": "Ahmet",
        "soyad": "Yılmaz",
        "email": "ahmet.yilmaz@hospital.com",
        "tc_no": "12345678901",
        "telefon": "05551234567",
        "rol": "doktor",
        "uzmanlık_alani": "Kardiyoloji",
        "departman": "Kardiyoloji Kliniği",
        "aktif": True,
    },
    {
        "kullanici_no": "KL-0002",
        "ad": "Fatma",
        "soyad": "Kaya",
        "email": "fatma.kaya@hospital.com",
        "tc_no": "23456789012",
        "telefon": "05559876543",
        "rol": "doktor",
        "uzmanlık_alani": "Nöroloji",
        "departman": "Nöroloji Kliniği",
        "aktif": True,
    },
    {
        "kullanici_no": "KL-0003",
        "ad": "Mehmet",
        "soyad": "Demir",
        "email": "mehmet.demir@hospital.com",
        "tc_no": "34567890123",
        "telefon": "05553334444",
        "rol": "yönetici",
        "uzmanlık_alani": "Hastane Yönetimi",
        "departman": "İdari",
        "aktif": True,
    },
]

SIKAYET_LISTESI = [
    "Göğüste ağrı",
    "Baş ağrısı",
    "Nefes darlığı",
    "Baş dönmesi",
    "Kolda/bacakta zayıflık",
    "Konuşmada güçlük",
    "Hiçbir şikayet yok",
]

TANI_LISTESI = [
    "Hipertansiyon kontrol altında",
    "Kalp hastalığı öncü belirtileri",
    "Diyabet belirlendi",
    "Yüksek kolesterol",
    "İnme riski altında",
    "Normal sağlık durumu",
]

# ============================================================================
# DOKTOR VERİSİ YÜKLEME
# ============================================================================

def doktor_verisi_yukle(db):
    """Örnek doktor verilerini yükler."""
    print("\n👨‍⚕️  DOKTOR VERİSİ YÜKLENIYOR...")
    print("-" * 60)
    
    db.kullanicilar.delete_many({})
    
    for doktor in DOKTOR_LISTESI:
        doktor["kayit_tarihi"] = datetime.now()
        doktor["olusturma_tarihi"] = datetime.now()
        doktor["son_giris_tarihi"] = datetime.now() - timedelta(days=random.randint(0, 30))
        
        try:
            sonuc = db.kullanicilar.insert_one(doktor)
            print(f"✅ {doktor['ad']} {doktor['soyad']} ({doktor['rol']}) eklendi")
        except Exception as e:
            print(f"❌ Doktor eklenirken hata: {str(e)}")
    
    print(f"📊 Toplam {db.kullanicilar.count_documents({})} doktor/kullanıcı yüklendi\n")

# ============================================================================
# HASTA VERİSİ YÜKLEME (CSV'den + Örnek Veri)
# ============================================================================

def hasta_verisi_yukle_csv(db):
    """CSV dosyasından hasta verilerini yükler."""
    print("\n🏥 HASTA VERİSİ YÜKLENIYOR (CSV'den)...")
    print("-" * 60)
    
    db.hastalar.delete_many({})
    db.tibbi_kayitlar.delete_many({})
    db.yasam_tarzi.delete_many({})
    
    try:
        df = pd.read_csv("data/processed/temizlenmis_hasta_verisi.csv")
        print(f"📄 CSV okundu: {len(df)} hasta kaydı bulundu")
        
        # Sigara durumu mapping
        sigara_mapping = {
            0: "Hiç İçmedi",
            1: "Halen İçiyor",
            2: "Eski İçici"
        }
        
        # Çalışma tipi mapping
        calisma_mapping = {
            0: "Özel Sektör",
            1: "Kamu",
            2: "Serbest Meslek",
            3: "Çocuk",
            4: "Emekli"
        }
        
        # CSV verileri uygun formata dönüştür
        for idx, row in df.iterrows():
            # Cinsiyet dönüşümü: 0=Kadın, 1=Erkek
            cinsiyet = "Erkek" if int(row.get("cinsiyet", 0)) == 1 else "Kadın"
            
            # Yaş hesaplama
            yas = int(row.get("yas", 0))
            dogum_yili = datetime.now().year - yas
            
            # Hasta demografik verisi
            hasta = {
                "hasta_no": f"HS-{str(idx + 1).zfill(4)}",
                "tc_no": f"{10000000000 + idx}",  # Benzersiz TC numarası
                "ad": f"Hasta_{idx+1}",
                "soyad": f"Kaydı",
                "dogum_yili": dogum_yili,
                "yas": yas,
                "cinsiyet": cinsiyet,
                "telefon": f"0555{str(idx).zfill(7)}",
                "email": f"hasta{idx+1}@email.com",
                "evli_mi": "Evet" if int(row.get("evli_mi", 0)) == 1 else "Hayır",
                "calisma_tipi": calisma_mapping.get(int(row.get("calisma_tipi", 0)), "Bilinmiyor"),
                "ikamet_tipi": "Kentsel" if int(row.get("ikamet_tipi", 0)) == 1 else "Kırsal",
                "kan_grubu": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                "sigorta_numarasi": f"SGT{str(idx).zfill(8)}",
                "aktif": True,
                "basvuru_tarihi": datetime.now() - timedelta(days=random.randint(1, 365)),
                "olusturma_tarihi": datetime.now(),
            }
            
            db.hastalar.insert_one(hasta)
            
            # Yaşam tarzı verisi - CSV'den gelen verilerle
            sigara_kodu = int(row.get("sigara_durumu", 0))
            yasam_tarzi = {
                "hasta_id": hasta["hasta_no"],
                "sigara_durumu": sigara_mapping.get(sigara_kodu, "Hiç İçmedi"),
                "alkol_durumu": random.choice(["Hiç", "Nadiren", "Hafta Sonu", "Düzenli"]),
                "egzersiz_durumu": random.choice(["Hiç", "Nadiren", "Haftada 1-2", "Haftada 3+"]),
                "gunluk_adim": random.randint(2000, 15000),
                "beslenme_tipi": random.choice(["Dengeli", "Yüksek Tuz", "Yüksek Yağ", "Yüksek Şeker"]),
                "gunluk_su": random.randint(1000, 3000),
                "uyku_saati": random.randint(5, 9),
                "stres_seviyesi": random.randint(1, 10),
                "guncellenme_tarihi": datetime.now(),
                "olusturma_tarihi": datetime.now(),
            }
            db.yasam_tarzi.insert_one(yasam_tarzi)
            
            # Tıbbi kayıt oluştur (CSV'deki sağlık verileriyle)
            if random.random() > 0.5:  # %50 hastaya tıbbi kayıt ekle
                tibbi_kayit = {
                    "kayit_no": f"TK-{str(idx + 1).zfill(5)}",
                    "hasta_id": hasta["hasta_no"],
                    "doktor_id": random.choice(["KL-0001", "KL-0002"]),
                    "kayit_tarihi": datetime.now() - timedelta(days=random.randint(1, 180)),
                    "ziyaret_tipi": random.choice(["Rutin Kontrol", "Acil", "Takip"]),
                    "sikayet": random.choice(SIKAYET_LISTESI),
                    "tanı": random.choice(TANI_LISTESI),
                    "hipertansiyon": bool(int(row.get("hipertansiyon", 0))),
                    "kalp_hastaligi": bool(int(row.get("kalp_hastaligi", 0))),
                    "ortalama_seker": float(row.get("ortalama_seker", 0)),
                    "vucut_kitle_indeksi": float(row.get("vucut_kitle_indeksi", 0)),
                    "notlar": "CSV verisinden yüklendi",
                    "olusturma_tarihi": datetime.now(),
                }
                db.tibbi_kayitlar.insert_one(tibbi_kayit)
        
        print(f"✅ {db.hastalar.count_documents({})} hasta yüklendi")
        print(f"✅ {db.yasam_tarzi.count_documents({})} yaşam tarzı kaydı yüklendi")
        print(f"✅ {db.tibbi_kayitlar.count_documents({})} tıbbi kayıt yüklendi\n")
        return True
        
    except FileNotFoundError:
        print("⚠️  CSV dosyası bulunamadı. Örnek veri kullanılacak.\n")
        return False
    except Exception as e:
        print(f"❌ CSV yükleme hatası: {str(e)}\n")
        return False

def hasta_verisi_yukle_ornekler(db):
    """Örnek hasta verileri oluşturur."""
    print("\n🏥 ÖRNEK HASTA VERİSİ OLUŞTURULUYOR...")
    print("-" * 60)
    
    if db.hastalar.count_documents({}) > 0:
        print(f"ℹ️  Hastalar zaten yüklü ({db.hastalar.count_documents({})}")
        return
    
    örnek_hastalar = []
    for i in range(1, 101):  # 100 örnek hasta
        hasta = {
            "hasta_no": f"HS-{str(i).zfill(4)}",
            "tc_no": f"{10000000000 + i}",
            "ad": f"Örnek_{i}",
            "soyad": f"Hastası",
            "yas": random.randint(18, 85),
            "cinsiyet": random.choice(["Erkek", "Kadın"]),
            "telefon": f"0555{str(i).zfill(7)}",
            "email": f"hasta{i}@example.com",
            "adres": f"{i}. Sokak Ev {i}",
            "sehir": random.choice(["İstanbul", "Ankara", "İzmir", "Gaziantep"]),
            "kan_grubu": random.choice(["A+", "O+", "B+"]),
            "sigorta_numarasi": f"SGT{str(i).zfill(8)}",
            "aktif": True,
            "basvuru_tarihi": datetime.now() - timedelta(days=random.randint(1, 365)),
            "olusturma_tarihi": datetime.now(),
        }
        örnek_hastalar.append(hasta)
    
    db.hastalar.insert_many(örnek_hastalar)
    print(f"✅ {len(örnek_hastalar)} örnek hasta eklendi\n")

# ============================================================================
# TIBBİ KAYIT YÜKLEME
# ============================================================================

def tibbi_kayitlar_yukle(db):
    """Örnek tıbbi kayıtlar oluşturur."""
    print("\n📋 TIBBİ KAYITLAR OLUŞTURULUYOR...")
    print("-" * 60)
    
    db.tibbi_kayitlar.delete_many({})
    
    hastalar = list(db.hastalar.find({}, {"hasta_no": 1, "_id": 0}))
    doktorlar = list(db.kullanicilar.find({"rol": "doktor"}, {"kullanici_no": 1, "_id": 0}))
    
    if not hastalar or not doktorlar:
        print("⚠️  Doktor veya hasta verisi bulunamadı!\n")
        return
    
    kayit_sayisi = 0
    for hasta in hastalar[:50]:  # İlk 50 hastaya muayene kaydı ekle
        # Rastgele 1-3 muayene kaydı
        muayene_sayisi = random.randint(1, 3)
        
        for j in range(muayene_sayisi):
            kayit = {
                "kayit_no": f"TK-{str(kayit_sayisi + 1).zfill(5)}",
                "hasta_id": hasta["hasta_no"],
                "doktor_id": random.choice(doktorlar)["kullanici_no"],
                "kayit_tarihi": datetime.now() - timedelta(days=random.randint(1, 180)),
                "ziyaret_tipi": random.choice(["Rutin Kontrol", "Acil", "Takip"]),
                "sikayet": random.choice(SIKAYET_LISTESI),
                "tanı": random.choice(TANI_LISTESI),
                "ilaç_reçetesi": [
                    {
                        "ilaç_adi": "Aspirin",
                        "doz": "100mg",
                        "sıklık": "Günde 1 defa",
                        "süre": 30
                    }
                ] if random.random() > 0.3 else [],
                "notlar": "Hasta genel durumu iyi, takip gerekir.",
                "tavsiye": "Düzenli egzersiz, sağlıklı beslenme",
                "olusturma_tarihi": datetime.now(),
            }
            db.tibbi_kayitlar.insert_one(kayit)
            kayit_sayisi += 1
    
    print(f"✅ {kayit_sayisi} tıbbi kayıt oluşturuldu\n")

# ============================================================================
# RİSK TAHMİNİ YÜKLEME
# ============================================================================

def risk_tahminleri_yukle(db):
    """Örnek risk tahmin kayıtları oluşturur."""
    print("\n🎯 RİSK TAHMİNLERİ OLUŞTURULUYOR...")
    print("-" * 60)
    
    db.risk_tahminleri.delete_many({})
    
    hastalar = list(db.hastalar.find({}, {"hasta_no": 1, "_id": 0}))[:50]
    
    tahmin_sayisi = 0
    for hasta in hastalar:
        # Rastgele risk puanı (risk faktörlerine bağlı)
        risk_skoru = random.uniform(0, 1)
        
        if risk_skoru < 0.33:
            risk_seviyesi = "Düşük"
            oneri = "Düzenli sağlık kontrolleri yeterli"
        elif risk_skoru < 0.66:
            risk_seviyesi = "Orta"
            oneri = "Aylık kontrollere geliniz. Yaşam tarzı değişikliği önerilir."
        else:
            risk_seviyesi = "Yüksek"
            oneri = "Acil doktor danışması alınız. Hastaneye başvurunuz."
        
        tahmin = {
            "tahmin_no": f"TP-{str(tahmin_sayisi + 1).zfill(5)}",
            "hasta_id": hasta["hasta_no"],
            "model_versiyon": "1.0-RandomForest",
            "risk_skoru": round(risk_skoru, 4),
            "risk_seviyesi": risk_seviyesi,
            "tahmin_tarihi": datetime.now() - timedelta(days=random.randint(0, 30)),
            "giriş_parametreleri": {
                "yas": random.randint(18, 85),
                "cinsiyet": random.choice(["Erkek", "Kadın"]),
                "hipertansiyon": random.randint(0, 1),
                "kalp_hastaligi": random.randint(0, 1),
                "sigara_durumu": random.choice(["Hiç", "Eski", "Halen"]),
            },
            "oneri": oneri,
            "onay_durumu": random.choice(["Beklemede", "Onaylandı"]),
            "olusturma_tarihi": datetime.now(),
        }
        db.risk_tahminleri.insert_one(tahmin)
        tahmin_sayisi += 1
    
    print(f"✅ {tahmin_sayisi} risk tahmin kaydı oluşturuldu\n")

# ============================================================================
# ANA FONKSİYON
# ============================================================================

def veritabani_doldir():
    """Tüm örnek verileri yükler."""
    print("\n" + "="*60)
    print("🚀 VERİTABANI SEED SÜRECI BAŞLATILIYOR")
    print("="*60)
    
    db = baglanti_olustur()
    if db is None:
        print("❌ Veritabanı bağlantısı başarısız!")
        return False
    
    # Şema oluştur
    koleksiyonlari_olustur()
    
    # Verileri yükle
    doktor_verisi_yukle(db)
    
    # CSV'den yükle, başarısız olursa örnek veri kullan
    if not hasta_verisi_yukle_csv(db):
        hasta_verisi_yukle_ornekler(db)
    
    tibbi_kayitlar_yukle(db)
    risk_tahminleri_yukle(db)
    
    # Özet
    print("\n" + "="*60)
    print("📊 VERİTABANI YÜKLEME ÖZETI")
    print("="*60)
    print(f"✅ Doktor/Kullanıcı: {db.kullanicilar.count_documents({})}")
    print(f"✅ Hasta: {db.hastalar.count_documents({})}")
    print(f"✅ Tıbbi Kayıt: {db.tibbi_kayitlar.count_documents({})}")
    print(f"✅ Yaşam Tarzı: {db.yasam_tarzi.count_documents({})}")
    print(f"✅ Risk Tahminleri: {db.risk_tahminleri.count_documents({})}")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    veritabani_doldir()