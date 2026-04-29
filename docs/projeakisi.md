# Akıllı Hasta Takip Sistemi - Proje Akışı ve Haftalık İlerleme

Bu dosya, takımımızın haftalık proje ilerlemesini, alınan teknik kararları ve üyelerin görev dağılımlarını içermektedir.

---

## 1. Hafta Geliştirmeleri ve Görev Dağılımı

* **Nuh Dağ (Scrum Master):** GitHub reposu oluşturuldu, branch koruma kuralları ayarlandı. Kaggle'dan "İnme (Stroke) Riski" veri seti temin edilerek ön işleme tamamlandı ve (`temizlenmis_hasta_verisi.csv`) repoya eklendi.
* **Aslıhan İlhan:** Geliştirme Ortamı Kurulumu yapılmıştır.

---

### 📄 Proje Analizi ve Tanımlama (Sorumlu: Mustafa Haccar)

#### 1. Problem Tanımı (Neyi Çözüyoruz?)
Dünya genelinde inme (felç), ölüm nedenleri arasında üst sıralarda yer almakta ve hayatta kalanlarda ciddi fiziksel kısıtlamalara yol açmaktadır. Mevcut sağlık sistemlerinde risk analizi genellikle bir semptom ortaya çıktıktan sonra yapılır. Çözmeyi amaçladığımız temel problemler:
* **Veri Karmaşıklığı:** Yaş, BMI ve glikoz seviyesi gibi birbirinden bağımsız görünen değişkenlerin bir araya geldiğinde oluşturduğu riskin insan gözüyle analiz edilmesinin zorluğu.
* **Geç Teşhis:** Risk faktörlerinin semptomlar oluşmadan önce fark edilememesi.
* **Önleyici Sağlık Eksikliği:** Kişiye özel risk skorlamasının eksikliği nedeniyle yaşam tarzı değişikliklerine gidilmemesi.

#### 2. Projenin Genel Hedefleri
Projenin ana hedefi, veriye dayalı bir erken uyarı mekanizması oluşturmaktır. Alt hedefler ise şunlardır:
* **Tahminleme Gücü:** Mevcut veri setini kullanarak %80 ve üzeri doğruluk oranına sahip bir makine öğrenimi modeli eğitmek.
* **Korelasyon Analizi:** Hangi faktörün (örneğin; sigara kullanımı mı yoksa yaş mı?) inme riski üzerinde daha baskın olduğunu istatistiksel olarak ortaya koymak.
* **Erişilebilirlik:** Hazırlanan modelin ve temizlenmiş veri setinin GitHub üzerinden diğer araştırmacıların kullanımına sunulması.

#### 3. Proje Kapsamı (Neleri Yapacağız?)
Proje, verinin ham halinden çalışan bir modele kadar olan tüm yazılım yaşam döngüsünü kapsar:
* **Veri Madenciliği ve Temizliği:** Eksik verilerin (Missing Values) tespiti, aykırı değerlerin (Outliers) filtrelenmesi ve verinin normalize edilmesi.
* **Özellik Mühendisliği (Feature Engineering):** Kategorik verilerin (Cinsiyet, Sigara durumu vb.) modelin anlayabileceği sayısal değerlere dönüştürülmesi.
* **Model Seçimi ve Eğitimi:** Lojistik Regresyon, Rastgele Orman (Random Forest) veya Destek Vektör Makineleri (SVM) gibi algoritmaların performanslarının karşılaştırılması.
* **Dokümantasyon:** Proje analiz raporu ve kodların GitHub üzerinden profesyonel bir README dosyası ile sunulması.

#### 4. Nihai Çıktı (Sonuçta Elimizde Ne Olacak?)
Projenin sonunda ortaya çıkacak somut çıktılar şunlardır:
* **Eğitilmiş Bir Model:** Yeni girilen bir hasta verisi (Örn: 55 yaş, 140 glikoz, sigara içiyor) için % olarak risk tahmini yapan bir yazılım modülü.
* **Analiz Raporu:** Hangi değişkenlerin inme riskini ne kadar artırdığını gösteren grafiksel raporlar.
* **Açık Kaynak Reposu:** Temizlenmiş veri seti ve modelleme kodlarını içeren, yazılım mühendisliği standartlarına uygun bir GitHub projesi.

---

### 💻 Teknoloji Araştırması ve Seçimi (Sorumlu: Amr Khaled Abdo Abdullah Mohammed)

#### 1. Giriş
Bu projede amaç, bireylerin inme (stroke) riskini tahmin edebilen bir makine öğrenimi modeli geliştirmektir. Problem türü ikili sınıflandırma (binary classification) problemidir. Modelin çıktısı iki değer alacaktır:
* **0:** İnme riski düşük / yok
* **1:** İnme riski yüksek
Bu doğrultuda, veri işleme, dengesiz veri setini yönetme, model eğitimi ve son kullanıcıya sunum (web arayüzü) süreçleri için endüstri standartlarına uygun yapay zeka ve makine öğrenimi teknolojileri seçilmiştir.

#### 2. Programlama Dili ve Ortam Yönetimi
* **Python:** Projede ana programlama dili olarak seçilmiştir. Geniş kütüphane ekosistemi, veri analizi araçları ve makine öğrenimi süreçlerindeki global endüstri standardı olması bu kararın temel nedenidir.
* **Geliştirme Ortamı (VS Code ve venv):** Geliştirme süreci bulut üzerinde değil, yerel ortamda Visual Studio Code (VS Code) kullanılarak yürütülmüştür. Proje bağımlılıklarının izole edilmesi ve sürümlerin çakışmaması amacıyla Python sanal ortamı (venv) kullanılarak profesyonel bir yazılım mimarisi kurulmuştur.

#### 3. Veri Ön İşleme ve Dengeleme Kütüphaneleri
* **Pandas ve NumPy:** Tablo formatındaki CSV verilerini okumak, eksik verileri temizlemek, özellikleri sayısallaştırmak (One-Hot Encoding) ve matris işlemleri yapmak için projede aktif olarak kullanılmaktadır.
* **Imbalanced-learn (SMOTE):** Tıbbi veri setlerinde sıkça karşılaşılan "dengesiz sınıf" (az sayıda hasta, çok sayıda sağlıklı birey) problemini çözmek için projeye entegre edilmiştir. Modelin sadece çoğunluğu ezberlemesini önlemek amacıyla SMOTE algoritması kullanılmış ve azınlıkta olan riskli hasta verileri sentetik olarak çoğaltılarak veri seti matematiksel olarak dengelenmiştir.

#### 4. Makine Öğrenimi Motoru: Scikit-learn
Projede makine öğrenimi algoritmalarını uygulamak, veriyi eğitim/test olarak bölmek ve başarı oranlarını hesaplamak için Scikit-learn kütüphanesi kullanılmıştır. İkili sınıflandırma için Logistic Regression, Decision Tree, SVM ve KNN gibi algoritmalar incelenmiş olup; ağaç tabanlı yapısı ve karmaşık tıbbi verilerdeki yüksek isabet oranı sebebiyle sistemin çekirdek beyni olarak **Random Forest (Rastgele Orman)** algoritması seçilmiştir.

#### 5. Web Arayüzü ve Sunum: Streamlit
Geliştirilen makine öğrenimi modelinin tıp profesyonelleri tarafından erişilebilir olması için **Streamlit** kütüphanesi tercih edilmiştir. Hastanın bulgularının girilebildiği, arka planda Random Forest modeline veri gönderen ve sonucu görsel bir "Risk Metresi" ile raporlayan profesyonel bir Karar Destek Paneli inşa edilmiştir.

---

### 📋 Gereksinim Toplama ve Belgeleme (Sorumlu: Necmihan Aksu )

#### 1. Gereksinim Toplama Süreci
Gereksinim toplama süreci, geliştirilecek sistemin kullanıcı ihtiyaçlarını ve teknik beklentilerini belirlemek amacıyla yapılan analiz aşamasıdır. Akıllı Hasta Takip Sistemi projesi için gereksinimler; hastalar, doktorlar, hastane yönetimi ve geliştirme ekibi dikkate alınarak belirlenmiştir.

#### 2. Veri Kaynağı Gereksinimleri
Proje kapsamında sağlık risk tahmini yapabilmek için Kaggle platformundan elde edilen veri seti kullanılmıştır. Veri seti proje ekibi tarafından temizlenmiş ve `temizlenmis_hasta_verisi.csv` adıyla proje deposuna eklenmiştir.
Bu veri seti **5110 hasta kaydı** ve **12 sağlık değişkeni** içermektedir.
Kullanılan değişkenler: `hasta_id`, `cinsiyet`, `yas`, `hipertansiyon`, `kalp_hastaligi`, `evli_mi`, `calisma_tipi`, `ikamet_tipi`, `ortalama_seker`, `vucut_kitle_indeksi (BMI)`, `sigara_durumu`, `inme_durumu` (hedef değişken).
* **GR-01:** Sistem `temizlenmis_hasta_verisi.csv` dosyasındaki verileri kullanarak sağlık risk tahmini gerçekleştirebilmelidir.

#### 3. Fonksiyonel Gereksinimler
* **FR-01:** Sistem CSV formatındaki veri setini hatasız okuyabilmelidir.
* **FR-02:** Sistem hastalara ait demografik ve klinik sağlık verilerini analiz edebilmelidir.
* **FR-03:** Sistem, makine öğrenimi algoritmaları (Random Forest) kullanarak sağlık risk tahmini yapabilmelidir.
* **FR-04:** Sistem, analiz sonucuna göre kullanıcıya risk seviyesini gösteren jenerik tıbbi yönlendirmeler sunabilmelidir.
* **FR-05:** Sistem, doktorların hastaların sağlık verilerini hızlıca girip test edebileceği bir web arayüzü (Dashboard) sağlamalıdır.
* **FR-06:** Sistem yüksek riskli durumlarda arayüz üzerinden görsel uyarı (Kırmızı Alarm/Risk Metresi) verebilmelidir.

#### 4. Teknik (Fonksiyonel Olmayan) Gereksinimler
* **Performans:** Sistem anlık veri girişlerinde saniyeler içinde analiz sonucunu arayüze yansıtabilmelidir.
* **Doğruluk:** Kullanılacak makine öğrenimi modeli sağlık risk tahmini için en az %80 doğruluk oranını hedeflemelidir. 
* **Güvenlik ve Mimari:** Mevcut sistem bir yerel prototip (MVP) olarak çalışacak olup, veri setinin ve modelin dış erişime kapalı, güvenli bir lokal sanal ortamda (`venv`) muhafaza edilmesi sağlanmalıdır.
* **Kullanılabilirlik:** Sistem, tıp profesyonellerini yormayacak şekilde karanlık tema (Dark Mode) desteğine sahip, ergonomik ve anlaşılır bir kullanıcı arayüzüne sahip olmalıdır.

#### 5. Sistem Kısıtlamaları
* Sistem analiz için sadece belirlenen CSV formatındaki özellikleri kabul edecektir.
* Sistem geliştirme süresi proje takvimi ile sınırlıdır ve canlı bir hastane veritabanı entegrasyonu bu fazın kapsamı dışındadır.

---

## 📅 2. Hafta: Gereksinim Analizi ve Planlama

**Sorumlu:** Yasmin Hammuş (Dokümantasyon Sorumlusu)

### 📋 Yapılan Çalışmalar
* **İş Paketi Tanımlama:** Proje başlangıç ve planlama aşaması (İP-01) tamamlanarak iş paketleri detaylandırıldı.
* **Kapsam Yönetimi:** Sistemin fonksiyonel sınırları belirlendi; HBYS standartlarına uygun veri girişi ve inme riski tahminleme süreçleri analiz edildi.
* **Risk Analizi:** Projenin başarı ölçütleri ve olası "kapsam kayması" (scope creep) riskleri değerlendirildi.

---

## 📅 3. Hafta: Sistem Tasarımı ve Veri Modelleme

**Sorumlu:** Yasmin Hammuş (Dokümantasyon Sorumlusu)

### 🏗 Mimari ve Tasarım
* **Sistem Mimarisi (İP-03):** Projenin teknik altyapısı ve modül etkileşimleri planlandı.
* **Nesne Yönelimli Modelleme (OOP):** * `Kisi` üst sınıfından türetilen `Hasta` sınıf yapısı tasarlandı.
    * Kalıtım (Inheritance) hiyerarşisi oluşturularak TC Kimlik ve iletişim bilgilerinin standartlaştırılması sağlandı.
* **Sektörel Standartlar:** Türkiye'deki Hastane Bilgi Yönetim Sistemleri (HBYS) standartları incelenerek veri modelleri bu kriterlere göre optimize edildi.

---

## 🛡️ 2. ve 3. Hafta: Teknik Tasarım ve Risk Yönetimi
**Dokümantasyon Hazırlığı:** Yasmin Hammuş  
**İş Paketleri ve Risk Analizi:** Mustafa Haccar
### 🏗️ Nesne Yönelimli Tasarım (OOP)
Haftalık geliştirme sürecinde, sistemin sürdürülebilirliği için **Kalıtım (Inheritance)** yapısı kullanılmıştır. Türkiye'deki HBYS standartlarına uygun olarak tüm aktörler ortak bir `Kisi` üst sınıfından türetilmiştir.
* **Sektörel Standartlar:** TC kimlik doğrulaması ve iletişim bilgilerinin tek formatta tutulması sağlanmıştır.
* **Kod Uygulaması:** `Hasta` sınıfı, `Kisi` sınıfından `extends` anahtar kelimesi ile türetilerek kodun tekrar yazılması önlenmiştir.
### 📊 Risk Analiz Tablosu
Projenin başarısını korumak amacıyla aşağıdaki olası riskler belirlenmiştir:

| Risk | Olasılık | Etki | Önlem |
| :--- | :--- | :--- | :--- |
| **Gereksinim Değişikliği** | Yüksek | Yüksek | Değişiklik kontrol süreci uygulanmalı. |
| **Kaynak Yetersizliği** | Orta | Yüksek | Yedek kaynak planı hazırlanmalı. |
| **Teknik Borç Birikimi** | Orta | Orta | Kod inceleme süreçleri sıkılaştırılmalı. |
| **Paydaş Onay Gecikmesi** | Düşük | Orta | Erken iletişim ve onay takibi sağlanmalı. |

### 📝 Sonuç ve Stratejik Öneriler
* **Sürekli İyileştirme:** Her faz sonunda retrospektif yapılarak süreç iyileştirilecektir.
* **Onay Mekanizması:** Çıktılar belgelenerek paydaş onayına sunulacak ve kayıt altına alınacaktır.
* **Bağımlılık Yönetimi:** İş paketleri arasındaki bağımlılıklar göz önünde bulundurularak süreç takip edilecektir.
---

4. Hafta Geliştirmeleri ve Görev Dağılımı
Necmihan Aksu (Gereksinim Toplama ve Belgeleme)
Bu hafta, projenin temelini oluşturan gereksinimlerin analizi, sınıflandırılması ve dökümantasyon süreci başarıyla tamamlanmıştır. Yapılan çalışmalar projenin teknik çerçevesini netleştirmiştir.
Gerçekleştirilen Detaylı Faaliyetler:
Veri Kaynağı Analizi ve Gereksinimleri: Sistemde kullanılacak veri seti tanımlanmış olup, 5110 hasta kaydı üzerinde çalışma yapılmıştır. Analiz ve modelleme süreçleri için kritik öneme sahip 12 temel sağlık değişkeni belirlenmiştir.
Fonksiyonel Gereksinimlerin Tanımlanması (FR-01 - FR-06): Sistemin gerçekleştirmesi gereken temel işlevler FR-01 ile FR-06 kodları arasında detaylandırılmış ve standartlara uygun şekilde dökümante edilmiştir.
Teknik ve Kalite Gereksinimlerinin Belirlenmesi: Sistemin performans hedefi olarak minimum %80 doğruluk oranı belirlenmiştir. Projenin sürdürülebilirliği için güvenlik protokolleri ve kullanılabilirlik kriterleri sisteme entegre edilmiştir.
Sistem Kısıtlamalarının Belgelenmesi: Yazılımın çalışma ortamı, donanım limitleri ve teknik kısıtlamalar belirlenerek risk yönetimi kapsamında dökümante edilmiştir.
Yasamin Hammuş (Dökümantasyon Sorumlusu)
Proje ilerlemesinin kayıt altına alınması ve dökümantasyonun güncel tutulması süreçlerini yönetmiştir.
Haftalık Geliştirme Denetimi: Hafta boyunca yapılan tüm teknik geliştirmeler gözden geçirilmiş ve proje hedefleriyle tutarlılığı kontrol edilmiştir.
4. Hafta Rapor Güncellemesi ve Entegrasyonu: Haftalık ilerleme raporu en güncel verilerle revize edilmiş ve ana proje dökümanına resmi olarak eklenmiştir.

  ## 📄 5. Hafta Geliştirmeleri: Veri Seti Dokümantasyonu
**Sorumlu:** Yasmin Hammuş (Dokümantasyon Sorumlusu)
### 📊 Veri Seti Özeti: `temizlenmis_hasta_verisi.csv`
* **Dosya Konumu:** `data/processed/temizlenmis_hasta_verisi.csv`
* **Açıklama:** Bu veri seti, inme (felç) riski tahmini modelleri geliştirmek amacıyla ön işlemeden geçirilmiş ve analiz için optimize edilmiştir.
* **Toplam Kayıt Sayısı:** 5111 Hasta
* **Toplam Sütun Sayısı:** 12
---
### 🔍 Sütun Açıklamaları (Özellik Matrisi)

| Sütun Adı | Açıklama | Değer Aralığı / Kodlama |
| :--- | :--- | :--- |
| **hasta_id** | Hasta benzersiz kimlik numarası | Integer |
| **cinsiyet** | Hastanın cinsiyeti | 0 = Kadın, 1 = Erkek |
| **yas** | Hastanın yaşı | Sayısal |
| **hipertansiyon** | Yüksek tansiyon durumu | 0 = Yok, 1 = Var |
| **kalp_hastaligi** | Kalp hastalığı geçmişi | 0 = Yok, 1 = Var |
| **evli_mi** | Medeni durum | 0 = Hayır, 1 = Evet |
| **calisma_tipi** | İstihdam türü | Kategorik |
| **ikamet_tipi** | Yaşanılan bölge türü | 0 = Kırsal, 1 = Kentsel |
| **ortalama_seker** | Kandaki ortalama glikoz seviyesi | Sayısal (mg/dL) |
| **vucut_kitle_indeksi** | Vücut Kitle İndeksi (BMI) | Sayısal (kg/m²) |
| **sigara_durumu** | Tütün kullanım alışkanlığı | Kategorik |
| **inme_durumu** | **Hedef Değişken (Label)** | **0 = Yok, 1 = Var** |

---
### 🛠 Yapılan İşlemler
* **Veri Temizleme:** Eksik veriler (NaN) tespit edilerek temizlendi.
* **Veri Tipleri:** Tüm sütunlar makine öğrenmesi algoritmalarının işleyebileceği sayısal ve kategorik formatlara dönüştürüldü.
* **Model Hazırlığı:** Veri seti, eğitim (train) ve test aşamaları için hazır hale getirildi.


  ## 6. Hafta Geliştirmeleri

**Yasmin Hammuş (Dokümantasyon Sorumlusu):**

### connection.py
- MongoDB bağlantı modülü
- Fonksiyonlar: baglanti_olustur(), baglanti_kapat()
- Veritabanı: hasta_takip_sistemi / localhost:27017

### doktor_ekle.py
- Doktor kayıt modülü
- Fonksiyonlar: doktor_ekle(), doktorlari_listele(), tc_dogrula()
- SHA256 şifreleme, otomatik DR-0001 numaralandırma

### hasta_ekle.py
- Hasta kayıt modülü
- Fonksiyonlar: hasta_ekle(), hastalari_listele(), tc_dogrula()
- Otomatik HS-0001 numaralandırma

### schema.py
- Veritabanı koleksiyon modülü
- Koleksiyonlar: kullanicilar, hastalar, tibbi_kayitlar, yasam_tarzi, risk_tahminleri

### seed_data.py
- CSV'den MongoDB'ye veri yükleme modülü
- 5111 hasta kaydını veritabanına aktarır

### model/
- Henüz geliştirilmedi
- Makine öğrenimi modeli 
  bu klasöre eklenecek

  ### frontend/
- Henüz geliştirilmedi
- Streamlit arayüzü eklenecek

### tests/
- Henüz geliştirilmedi
- Test dosyaları eklenecek

  



  
