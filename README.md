# Akıllı Hasta Takip Sistemi

Makine öğrenimi algoritmaları kullanarak hastaların sağlık durumunu tahmin eden ve risk faktörlerini belirleyen bir sistem.

## Proje Hakkında

Bu proje Fırat Üniversitesi Yazılım Mühendisliği bölümü kapsamında geliştirilmektedir. Hastaların tıbbi kayıtları, yaşam tarzı bilgileri ve sensör verileri kullanılarak kişiselleştirilmiş sağlık önerileri sunulmaktadır.

## Teknolojiler

- **Python** — Ana programlama dili
- **MongoDB** — Veritabanı
- **scikit-learn** — Makine öğrenimi
- **TensorFlow/Keras** — Derin öğrenme
- **Streamlit** — Web arayüzü
- **Flask** — REST API

## Kurulum

1. Repoyu klonla:
```
git clone https://github.com/nuhdag6565-arch/Akilli-Hasta-Takip-Sistemi-Projesi.git
```

2. Kütüphaneleri kur:
```
pip install -r requirements.txt
```

3. MongoDB'nin çalıştığından emin ol, sonra veritabanını kur:
```
python database/schema.py
python database/seed_data.py
```

## Proje Yapısı
```
├── data/               # Veri dosyaları
├── database/           # MongoDB bağlantı ve şema modülleri
├── model/              # ML model eğitimi ve tahmin
├── api/                # REST API
├── frontend/           # Streamlit arayüzü
├── docs/               # Proje belgeleri
└── tests/              # Test dosyaları
```

## Ekip

| İsim | Rol |
|------|-----|
| Nuh Dağ | Scrum Master / Veritabanı |
| Mustafa Haccar | Proje Analizi |
| Aslıhan İlhan | Geliştirme Ortamı Kurulumu |
| Amr Khaled | Teknoloji Araştırması / ML |
| Necmihan Aksu | Gereksinim Toplama |

## Teslim Edilecekler

- [x] Veri toplama ve ön işleme modülü
- [x] Veritabanı tasarımı
- [ ] Makine öğrenimi model geliştirme
- [ ] Risk tahmini ve erken uyarı sistemi
- [ ] Web/Mobil arayüz
- [ ] Kişiselleştirilmiş sağlık önerileri

[Akıllı Hasta Takip Sistemi Tasarım Dosyasını Görüntülemek İçin Tıklayın](./AkilliHastaSystemi.pdf)
