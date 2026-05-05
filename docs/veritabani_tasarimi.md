# Veritabanı Şema Tasarımı ve NoSQL Veritabanı Seçimi

## 📝 Açıklama

Bu doküman, Akıllı Hasta Takip Sistemi projesi için NoSQL veritabanı şema tasarımını ve veritabanı seçim sürecini detaylandırır. Hasta verilerini (tıbbi kayıtlar, yaşam tarzı bilgileri, sensör verileri) etkin bir şekilde depolamak için MongoDB veritabanı seçilmiş ve optimize edilmiş şema tasarlanmıştır.

## 🎯 Proje Gereksinimleri

- **Veri Türleri**: Hasta demografik bilgileri, tıbbi kayıtlar, yaşam tarzı verileri, sensör okumaları, risk tahminleri
- **Erişim Desenleri**: Hasta bazlı sorgulamalar, tarih bazlı filtreleme, risk skorlarına göre sıralama
- **Veri İlişkileri**: Hasta merkezli ilişkisel veri modeli
- **Ölçeklenebilirlik**: Büyüyen hasta sayısı ve veri hacmi
- **Performans**: Hızlı sorgulama ve indeksleme

## 🔍 NoSQL Veritabanı Seçenekleri Karşılaştırması

### MongoDB (Belge Tabanlı)
- **Artılar**: Esnek şema, JSON benzeri dokümanlar, güçlü sorgulama yetenekleri, indeksleme, aggregation pipeline
- **Eksiler**: ACID garantisi sınırlı, büyük dokümanlarda performans düşüşü
- **Uygunluk**: Yüksek (tıbbi verilerin karmaşık yapısı için ideal)

### Cassandra (Sütun Tabanlı)
- **Artılar**: Yüksek yazma performansı, dağıtık mimari, zaman serisi verileri için optimize
- **Eksiler**: Karmaşık sorgular zor, öğrenme eğrisi yüksek
- **Uygunluk**: Orta (sensör verileri için uygun, ama genel kullanım için fazla karmaşık)

### Redis (Anahtar-Değer)
- **Artılar**: Çok hızlı okuma/yazma, cache olarak mükemmel
- **Eksiler**: Karmaşık sorgular yok, kalıcı depolama sınırlı
- **Uygunluk**: Düşük (ana veritabanı olarak yetersiz)

### CouchDB (Belge Tabanlı)
- **Artılar**: Offline senkronizasyon, REST API, esnek replikasyon
- **Eksiler**: Sorgulama yetenekleri sınırlı, performans MongoDB'den düşük
- **Uygunluk**: Orta (mobil senkronizasyon için uygun)

## ✅ MongoDB Seçimi Gerekçesi

MongoDB, aşağıdaki nedenlerle proje için en uygun NoSQL veritabanıdır:

1. **Esnek Şema**: Tıbbi verilerin değişken yapısı (farklı test türleri, ilaç reçeteleri) için ideal
2. **Doküman Modeli**: Hasta verilerinin doğal hiyerarşik yapısını destekler
3. **Güçlü Sorgulama**: Aggregation pipeline ile karmaşık analizler
4. **İndeksleme**: Hasta ID, tarih, risk skorları üzerinde optimize indeksler
5. **Python Entegrasyonu**: PyMongo kütüphanesi ile kolay bağlantı
6. **Topluluk Desteği**: Sağlık sektöründe yaygın kullanım
7. **JSON Schema Validation**: Veri kalitesi garantisi

## 🏗️ Veritabanı Şema Tasarımı

### Koleksiyon Yapısı

#### 1. `kullanicilar` Koleksiyonu
Sistem kullanıcıları (doktorlar, yöneticiler, teknisyenler)

```json
{
  "kullanici_no": "KL-0001",
  "ad": "Ahmet",
  "soyad": "Yılmaz",
  "email": "ahmet.yilmaz@hospital.com",
  "rol": "doktor",
  "uzmanlık_alani": "Kardiyoloji",
  "aktif": true
}
```

#### 2. `hastalar` Koleksiyonu
Hasta demografik ve temel bilgileri

```json
{
  "hasta_no": "HS-0001",
  "tc_no": "12345678901",
  "ad": "Mehmet",
  "soyad": "Demir",
  "yas": 45,
  "cinsiyet": "Erkek",
  "kan_grubu": "A+",
  "aktif": true
}
```

#### 3. `tibbi_kayitlar` Koleksiyonu
Her muayene/takip ziyareti için tıbbi veriler

```json
{
  "kayit_no": "TK-0001",
  "hasta_id": "HS-0001",
  "doktor_id": "KL-0001",
  "kayit_tarihi": "2024-01-15",
  "ziyaret_tipi": "Rutin Kontrol",
  "tanı": "Hipertansiyon",
  "ilaç_reçetesi": [
    {
      "ilaç_adi": "Aspirin",
      "doz": "100mg",
      "sıklık": "Günde 1 kez"
    }
  ]
}
```

#### 4. `yasam_tarzi` Koleksiyonu
Hasta yaşam tarzı bilgileri

```json
{
  "hasta_id": "HS-0001",
  "sigara_durumu": "Halen İçiyor",
  "gunluk_sigara": 10,
  "egzersiz_durumu": "Haftada 1-2",
  "beslenme_tipi": "Yüksek Tuz"
}
```

#### 5. `risk_tahminleri` Koleksiyonu
ML model risk tahminleri

```json
{
  "tahmin_no": "TP-0001",
  "hasta_id": "HS-0001",
  "risk_skoru": 0.75,
  "risk_seviyesi": "Yüksek",
  "tahmin_tarihi": "2024-01-15"
}
```

#### 6. `sensor_verileri` Koleksiyonu
IoT sensörlerinden gelen veriler

```json
{
  "sensor_id": "BP-001",
  "hasta_id": "HS-0001",
  "veri_turu": "Kan Basıncı",
  "deger": 140,
  "birim": "mmHg",
  "zaman_damgasi": "2024-01-15T10:30:00Z"
}
```

#### 7. `audit_log` Koleksiyonu
Sistem değişikliklerinin loglanması

```json
{
  "kullanici_id": "KL-0001",
  "islem": "HASTA_GUNCELLEME",
  "kayit_id": "HS-0001",
  "eski_deger": "yas: 44",
  "yeni_deger": "yas: 45",
  "zaman": "2024-01-15T10:30:00Z"
}
```

### İndeks Tasarımı

Performans optimizasyonu için aşağıdaki indeksler tanımlanmıştır:

- **Unique İndeksler**: `kullanici_no`, `email`, `tc_no`, `hasta_no`, `kayit_no`, `tahmin_no`
- **Bileşik İndeksler**: `hasta_id + tarih` kombinasyonları
- **Tek İndeksler**: Rol, aktif durum, risk seviyesi vb. filtreleme alanları

## 🚀 Kurulum ve Yapılandırma

### MongoDB Kurulumu

1. **Windows için MongoDB Community Server indirin**:
   ```
   https://www.mongodb.com/try/download/community
   ```

2. **Kurulum**:
   - MSI dosyasını çalıştırın
   - "Complete" kurulum seçin
   - MongoDB Compass araçını da yükleyin

3. **Servisi başlatın**:
   ```bash
   net start MongoDB
   ```

4. **Bağlantıyı test edin**:
   ```python
   from pymongo import MongoClient
   client = MongoClient("mongodb://localhost:27017/")
   print(client.list_database_names())
   ```

### Python Bağımlılıkları

```bash
pip install pymongo
```

### Veritabanı Başlatma

```python
from database.schema import koleksiyonlari_olustur

# Koleksiyonları ve indeksleri oluştur
koleksiyonlari_olustur()
```

## 📖 Kullanım Kılavuzu

### Temel İşlemler

```python
from database.connection import baglanti_olustur

# Bağlantı oluştur
db = baglanti_olustur()

# Hasta ekleme
hasta = {
    "hasta_no": "HS-0001",
    "ad": "Ahmet",
    "soyad": "Yılmaz",
    "yas": 50
}
db.hastalar.insert_one(hasta)

# Hasta sorgulama
hasta = db.hastalar.find_one({"hasta_no": "HS-0001"})

# Risk tahminleri sorgulama
yuksek_riskliler = list(db.risk_tahminleri.find({"risk_seviyesi": "Yüksek"}))
```

### Aggregation Örnekleri

```python
# Yaş gruplarına göre hasta sayısı
pipeline = [
    {"$group": {"_id": "$yas", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]
sonuc = list(db.hastalar.aggregate(pipeline))

# Ortalama risk skoru
pipeline = [
    {"$group": {"_id": None, "ortalama_risk": {"$avg": "$risk_skoru"}}}
]
sonuc = list(db.risk_tahminleri.aggregate(pipeline))
```

## 🔧 Bakım ve Optimizasyon

### İndeks Bakımı
- Düzenli indeks kullanım istatistiklerini kontrol edin
- Kullanılmayan indeksleri kaldırın
- Büyük koleksiyonlarda background indexing kullanın

### Performans İzleme
- MongoDB Profiler ile yavaş sorguları tespit edin
- Explain plan ile sorgu optimizasyonu yapın
- Connection pooling ayarlarını optimize edin

### Yedekleme
```bash
# Veritabanı yedekleme
mongodump --db akıllı_hasta_takip_sistemi --out backup/

# Geri yükleme
mongorestore --db akıllı_hasta_takip_sistemi backup/akıllı_hasta_takip_sistemi
```

## 📊 Veri Modeli Diyagramı

```
┌─────────────────┐    ┌──────────────────┐
│    kullanicilar │    │     hastalar     │
│                 │    │                  │
│ - kullanici_no  │    │ - hasta_no       │
│ - ad, soyad     │    │ - ad, soyad      │
│ - rol           │    │ - yas, cinsiyet  │
│ - uzmanlik      │    │ - iletisim       │
└─────────────────┘    └──────────────────┘
         │                       │
         │                       │
         v                       v
┌─────────────────┐    ┌──────────────────┐
│ tibbi_kayitlar  │    │   yasam_tarzi    │
│                 │    │                  │
│ - kayit_no      │◄───┤ - hasta_id       │
│ - hasta_id      │    │ - sigara         │
│ - doktor_id     │    │ - egzersiz       │
│ - tanı, ilaç    │    │ - beslenme       │
└─────────────────┘    └──────────────────┘
         │                       │
         │                       │
         v                       v
┌─────────────────┐    ┌──────────────────┐
│ risk_tahminleri │    │ sensor_verileri  │
│                 │    │                  │
│ - tahmin_no     │    │ - sensor_id      │
│ - hasta_id      │    │ - hasta_id       │
│ - risk_skoru    │    │ - veri_turu      │
│ - model_version │    │ - deger, birim   │
└─────────────────┘    └──────────────────┘
```

## 🎯 Sonuç

MongoDB, Akıllı Hasta Takip Sistemi için ideal bir NoSQL çözümüdür:

- **Esnek Veri Modeli**: Tıbbi verilerin karmaşık ve değişken yapısını destekler
- **Yüksek Performans**: Optimize edilmiş indeksler ve sorgular
- **Ölçeklenebilirlik**: Büyüyen veri hacmine uyum
- **Geliştirici Dostu**: Python entegrasyonu ve zengin sorgulama yetenekleri
- **Veri Kalitesi**: JSON Schema validation ile tutarlılık garantisi

Bu tasarım, sistemin güvenilir, hızlı ve bakımı kolay bir veritabanı altyapısı sağlamaktadır.