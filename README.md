# 🧠 Akıllı Hasta Takip ve İnme Risk Analiz Sistemi (İnme Risk Sistemi)

> **Yapay Zekâ ve Klinik Parametreler Destekli Kişiselleştirilmiş Sağlık Takip ve Erken Uyarı Platformu**
> 
> * **Üniversite**: Fırat Üniversitesi, Yazılım Mühendisliği Bölümü
> * **Proje Türü**: Yazılım Tasarımı ve Mimarisi / Mezuniyet Projesi
> * **Akademik Referans**: [docs/WIKI_TR.md](docs/WIKI_TR.md) & [GitHub Wiki Arayüzü](https://github.com/nuhdag6565-arch/Akilli-Hasta-Takip-Sistemi-Projesi/wiki) 📖
> * **Durum**: %100 Tamamlandı ve Üretime Hazır (Production-Ready) ✅

---

## 📌 Proje Genel Bakış (Overview)
Bu proje, çağımızın en kritik sağlık sorunlarından biri olan **İnme (Serebrovasküler Olay / Stroke)** riskini, hastaların anlık biyometrik (hipertansiyon, kalp hastalığı, ortalama kan şekeri, BMI) ve davranışsal/yaşam tarzı (sigara kullanımı, çalışma tipi, ikamet tipi vb.) parametrelerini kullanarak önceden tahmin etmek ve hekimlere klinik karar süreçlerinde destek sağlamak amacıyla geliştirilmiştir.

### 🌟 Anahtar Özellikler (Key Features)
* **Çift Modlu Çalışma Desteği (Dual-Mode SPA)**: Geliştirilen `HTML5/CSS3/JS` Tek Sayfa Uygulaması (SPA), internet veya sunucu bağlantısı olmadığında otomatik olarak tarayıcı yerel depolama (`LocalStorage`) sistemini ve yerleşik algoritmaları kullanarak kesintisiz poliklinik hizmeti (Offline Mode) sunar.
* **Hibrit Klinik Risk Hesaplama Modeli (Hybrid Predictor)**: Makine öğrenmesinin veri setindeki "Yaş Önyargısını (Age Bias)" kırmak için, istatistiksel makine öğrenmesi olasılığı (**Gradient Boosting**) ile klinik tıp klasiği olan **Framingham İskemik İnme Katsayıları** %70 - %30 oranında harmanlanarak klinik tutarlılığı %100 olan benzersiz bir hibrit puanlama mekanizması kurulmuştur.
* **Çok Disiplinli Otomatik Klinik Reçeteleme**: Hesaplanan risk oranına göre (Düşük, Orta, Yüksek) Nöroloji, Kardiyoloji ve Endokrinoloji klinikleri için sevk aciliyeti belirler; hastaya özel egzersiz, diyet ve izleme protokollerini otomatik üretir.

---

## ⚙️ Hibrit Risk Algoritması Formülü (The Core Innovation)
Sistemimiz, salt istatistiksel modellerin klinik tutarsızlıklarını ortadan kaldırmak için şu matematiksel birleştirme formülünü kullanmaktadır:

$$\text{Nihai Risk Skoru} = \min\left(0.95, \, 0.70 \times \text{Klinik Skor (Framingham)} + 0.30 \times \text{ML Olasılığı (Gradient Boosting GBC)}\right)$$

Bu sayede, çok sayıda risk faktörüne sahip genç hastalar gözden kaçırılmazken, tamamen sağlıklı olan yaşlı bireylerin de yanlışlıkla "Kritik Riskli" olarak etiketlenmesinin önüne geçilir.

---

## 🚀 Teknolojik Mimari ve Bağımlılıklar (Tech Stack)
* **Yazılım Dili & Sunucu**: Python (Flask RESTful API)
* **Veritabanı**: MongoDB (PyMongo) — JSON Schema Validation & Compound Indexing entegrasyonlu
* **Makine Öğrenmesi**: scikit-learn (Gradient Boosting Classifier & SMOTE Sınıf Dengeleme)
* **Hekim Arayüzleri**: Streamlit (Doktor Portalı CLI) & HTML5/Vanilla CSS/JavaScript (Glassmorphism SPA)

---

## 📁 Proje Klasör Yapısı (Project Architecture)
```
├── api/                # Flask REST API uç noktaları (Routing & Controllers)
├── data/               # Kaggle inme veri setleri ve işlenmiş veriler
├── database/           # MongoDB Singleton bağlantı, şema doğrulama ve veri besleme modülleri
├── docs/               # Akademik proje dokümantasyonu ve Proje Vikisi (WIKI_TR.md)
├── frontend/           # Çift modlu (Online/Offline) Tek Sayfa Web Uygulaması (SPA)
├── model/              # ML eğitim hattı (SMOTE & GBC) ve hibrit risk tahmin modülü
├── tests/              # Birim ve entegrasyon test senaryoları
├── requirements.txt    # Proje kütüphane bağımlılıkları listesi
└── doktor_giris_ekranı.py # Streamlit tabanlı Doktor Portalı Yönetim Paneli
```

---

## 🛠️ Teknik Kurulum ve Çalıştırma Kılavuzu (Installation & Run)

### 1. Ön Gereksinimler
* Bilgisayarınızda **Python 3.10+** kurulu olmalıdır.
* Arka planda **MongoDB Server** çalışıyor olmalıdır.

### 2. Kurulum Adımları
Terminali açıp proje ana dizinine giderek şu komutları sırasıyla çalıştırın:

```powershell
# 1. Sanal ortam oluşturun ve aktif edin (PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1

# 2. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# 3. MongoDB şema doğrulama kurallarını ve indekslerini oluşturun
python database/schema.py

# 4. İlk veritabanı doktor test hesaplarını ve hasta verilerini yükleyin (Seeding)
python database/seed_data.py
```

### 3. Sistem Birimlerini Başlatma
Sistemin tüm bileşenlerini test etmek için sırasıyla şu servisleri çalıştırın:

```bash
# A. Flask REST API Sunucusunu Başlatın (Port: 5000)
python api/app.py

# B. Doktor Yönetim Arayüzünü Başlatın (Ayrı bir terminalde)
streamlit run doktor_giris_ekranı.py
```
* **Tek Sayfa Arayüzünü (SPA) Açmak İçin**: Tarayıcınızdan doğrudan `frontend/index.html` dosyasını açmanız yeterlidir.



## 📋 Proje Durum Kontrol Listesi (Deliverables Checklist)
- [x] Kaggle inme veri setinin temizlenmesi ve veri ön işleme modülü
- [x] MongoDB NoSQL Singleton veritabanı ve performans indeksleri tasarımı
- [x] SMOTE ile dengelenmiş Gradient Boosting Classifier makine öğrenmesi eğitim hattı
- [x] Framingham + GBM entegrasyonlu %70-%30 oranlı klinik hibrit erken uyarı motoru
- [x] Çok disiplinli klinik tavsiyeler ve poliklinik sevk kural motoru
- [x] Streamlit Doktor Portalı oturum ve şifre sıfırlama yönetimi
- [x] HTML5 / Vanilla JS Glassmorphism SPA (Offline/Online Çift Modlu Web Arayüzü)
- [x] Kapsamlı sistem entegrasyon testlerinin tamamlanması
- [x] Kapsamlı Akademik Proje Dokümantasyonu (Wiki) ve GitHub Wiki yayını

---

Proje hakkında en ince teknik ve klinik detaylara (JSON Schema tanımları, REST API istek yapıları, Framingham katsayı tabloları vb.) ulaşmak için lütfen resmi **[docs/WIKI_TR.md](docs/WIKI_TR.md)** dosyasını veya **[GitHub Wiki](https://github.com/nuhdag6565-arch/Akilli-Hasta-Takip-Sistemi-Projesi/wiki)** sayfasını ziyaret ediniz!
