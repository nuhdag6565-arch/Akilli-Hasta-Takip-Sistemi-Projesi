# Akıllı Hasta Takip Sistemi - Proje Akışı ve Haftalık İlerleme

Bu dosya, takımımızın haftalık proje ilerlemesini ve üyelerin görev dağılımlarını içermektedir.

## 1. Hafta
* **Nuh Dağ (Scrum Master):** GitHub reposu oluşturuldu, branch koruma kuralları ayarlandı. Kaggle'dan "İnme (Stroke) Riski" veri seti temin edilerek ön işleme tamamlandı ve (`temizlenmis_hasta_verisi.csv`) repoya eklendi.
* **Mustafa Haccar:** Proje analiz dokümanı hazırlandı, detaylar aşağıdadır.
* **Necmihan Aksu:** [Bu hafta ne yaptığı buraya yazılacak]
* **Aslıhan İlhan:** [Bu hafta ne yaptığı buraya yazılacak]
* **Amr Khaled Abdo Abdullah Mohammed:
* **# Teknoloji Araştırması ve Seçimi

## 1. Giriş

Bu projede amaç, bireylerin inme (stroke) riskini tahmin edebilen bir makine öğrenimi modeli geliştirmektir. Problem türü ikili sınıflandırma (binary classification) problemidir. Modelin çıktısı iki değer alacaktır:

* **0:** İnme riski yok
* **1:** İnme riski var

Bu nedenle proje kapsamında veri işleme, model eğitimi ve analiz süreçleri için uygun yapay zeka ve makine öğrenimi teknolojileri araştırılmıştır.

---

## 2. Programlama Dili: Python

Projede ana programlama dili olarak **Python** seçilmiştir. Python günümüzde veri bilimi, yapay zeka ve makine öğrenimi alanlarında en yaygın kullanılan dillerden biridir. Bunun başlıca nedenleri şunlardır:

* Geniş kütüphane ekosistemine sahip olması
* Veri analizi ve makine öğrenimi için güçlü araçlar sunması
* Okunabilir ve anlaşılır bir sözdizimine sahip olması
* Büyük bir geliştirici topluluğu tarafından desteklenmesi

Bu avantajlar sayesinde Python, veri analizi ve makine öğrenimi projeleri için ideal bir seçimdir.

---

## 3. Veri Ön İşleme Kütüphaneleri

### Pandas

**Pandas**, veri analizi ve veri işleme için kullanılan güçlü bir Python kütüphanesidir. Projede özellikle CSV formatındaki veri setlerini okumak, temizlemek ve düzenlemek için kullanılmaktadır.

Pandas'ın avantajları:

* Tablo formatındaki verileri kolay yönetme
* Veri temizleme ve dönüştürme işlemlerini hızlı yapabilme
* Büyük veri setleri üzerinde etkili analiz yapabilme

---

### NumPy

**NumPy**, bilimsel hesaplama ve sayısal işlemler için kullanılan temel bir Python kütüphanesidir. Büyük veri dizileri ve matrislerle çalışmayı kolaylaştırır.

NumPy'nin avantajları:

* Hızlı matematiksel işlemler
* Büyük veri dizileri ile yüksek performans
* Makine öğrenimi algoritmaları için temel veri yapıları sağlaması

---

## 4. Makine Öğrenimi Kütüphanesi: Scikit-learn

Projede makine öğrenimi algoritmalarını uygulamak için **Scikit-learn** kütüphanesi kullanılmaktadır.

Scikit-learn tercih edilmesinin nedenleri:

* Güvenilir ve stabil makine öğrenimi algoritmaları sunması
* Sınıflandırma, regresyon ve kümeleme algoritmalarını desteklemesi
* Python veri analizi araçları ile kolay entegrasyon sağlaması
* Veri ön işleme ve model değerlendirme araçlarını içermesi

Bu özellikler sayesinde Scikit-learn, makine öğrenimi projeleri için en popüler kütüphanelerden biridir.

---

## 5. Geliştirme Ortamı: Google Colab

Projenin geliştirme ortamı olarak **Google Colab** kullanılmaktadır.

Google Colab'ın avantajları:

* Bulut tabanlı olması
* Kurulum gerektirmemesi
* Python ve veri bilimi kütüphanelerinin hazır gelmesi
* Donanım gücü gerektiren işlemleri bilgisayarı yormadan çalıştırabilmesi
* Takım çalışması için kolay paylaşım imkanı sağlaması

Bu nedenle proje geliştirme sürecinde Google Colab uygun bir araç olarak seçilmiştir.

---

## 6. Proje İçin Uygun Makine Öğrenimi Algoritmaları

Projemizdeki veri seti **ikili sınıflandırma problemi** olduğu için aşağıdaki makine öğrenimi algoritmaları uygun görülmektedir.

### Logistic Regression

Logistic Regression, ikili sınıflandırma problemleri için en temel ve en yaygın kullanılan algoritmalardan biridir. Modelin yorumlanması kolaydır ve özellikle tıbbi veri analizlerinde sıkça kullanılmaktadır.

---

### Random Forest

Random Forest algoritması, birçok karar ağacının birleşmesiyle oluşturulan güçlü bir sınıflandırma yöntemidir. Gürültülü verilerde bile yüksek doğruluk sağlayabilir ve overfitting problemini azaltır.

---

### Decision Tree

Decision Tree algoritması veriyi karar kuralları ile sınıflandırır. Modelin anlaşılması ve görselleştirilmesi kolaydır. Bu nedenle veri analizinde açıklanabilirlik açısından önemli bir avantaj sağlar.

---

### Support Vector Machine (SVM)

SVM algoritması, sınıflar arasındaki en iyi ayrım çizgisini bulmaya çalışır. Karmaşık veri yapılarında yüksek doğruluk sağlayabilir ve özellikle sınıflandırma problemlerinde güçlü bir performans gösterir.

---

### K-Nearest Neighbors (KNN)

KNN algoritması, bir veri noktasını en yakın komşularına göre sınıflandırır. Basit bir algoritma olmasına rağmen küçük ve orta ölçekli veri setlerinde etkili sonuçlar verebilir.

---

## 7. Sonuç

Bu projede inme riskini tahmin etmek amacıyla Python tabanlı bir makine öğrenimi sistemi geliştirilmesi planlanmaktadır. Python, Pandas, NumPy ve Scikit-learn gibi güçlü araçlar sayesinde veri işleme ve model geliştirme süreçleri etkili bir şekilde gerçekleştirilebilir.

Ayrıca Logistic Regression, Random Forest, Decision Tree, SVM ve KNN gibi algoritmaların kullanılması, modelin doğruluğunu artırmak ve farklı yöntemlerin performansını karşılaştırmak açısından önemli bir avantaj sağlayacaktır.


* ---
### Proje Analizi ve Tanımlama

**1. Problem Tanımı (Neyi Çözüyoruz?)**
Dünya genelinde inme (felç), ölüm nedenleri arasında üst sıralarda yer almakta ve hayatta kalanlarda ciddi fiziksel kısıtlamalara yol açmaktadır. Mevcut sağlık sistemlerinde risk analizi genellikle bir semptom ortaya çıktıktan sonra yapılır.

Çözmeyi amaçladığımız temel problemler:
* **Veri Karmaşıklığı:** Yaş, BMI ve glikoz seviyesi gibi birbirinden bağımsız görünen değişkenlerin bir araya geldiğinde oluşturduğu riskin insan gözüyle analiz edilmesinin zorluğu.
* **Geç Teşhis:** Risk faktörlerinin semptomlar oluşmadan önce fark edilememesi.
* **Önleyici Sağlık Eksikliği:** Kişiye özel risk skorlamasının eksikliği nedeniyle yaşam tarzı değişikliklerine gidilmemesi.

**2. Projenin Genel Hedefleri**
Projenin ana hedefi, veriye dayalı bir erken uyarı mekanizması oluşturmaktır. Alt hedefler ise şunlardır:
* **Tahminleme Gücü:** Mevcut veri setini kullanarak %80 ve üzeri doğruluk oranına sahip bir makine öğrenimi modeli eğitmek.
* **Korelasyon Analizi:** Hangi faktörün (örneğin; sigara kullanımı mı yoksa yaş mı?) inme riski üzerinde daha baskın olduğunu istatistiksel olarak ortaya koymak.
* **Erişilebilirlik:** Hazırlanan modelin ve temizlenmiş veri setinin GitHub üzerinden diğer araştırmacıların kullanımına sunulması.

**3. Proje Kapsamı (Neleri Yapacağız?)**
Proje, verinin ham halinden çalışan bir modele kadar olan tüm yazılım yaşam döngüsünü kapsar:
* **Veri Madenciliği ve Temizliği:** Eksik verilerin (Missing Values) tespiti, aykırı değerlerin (Outliers) filtrelenmesi ve verinin normalize edilmesi.
* **Özellik Mühendisliği (Feature Engineering):** Kategorik verilerin (Cinsiyet, Sigara durumu vb.) modelin anlayabileceği sayısal değerlere dönüştürülmesi.
* **Model Seçimi ve Eğitimi:** Lojistik Regresyon, Rastgele Orman (Random Forest) veya Destek Vektör Makineleri (SVM) gibi algoritmaların performanslarının karşılaştırılması.
* **Dokümantasyon:** Proje analiz raporu ve kodların GitHub üzerinden profesyonel bir README dosyası ile sunulması.

**4. Nihai Çıktı (Sonuçta Elimizde Ne Olacak?)**
Projenin sonunda ortaya çıkacak somut çıktılar şunlardır:
* **Eğitilmiş Bir Model:** Yeni girilen bir hasta verisi (Örn: 55 yaş, 140 glikoz, sigara içiyor) için % olarak risk tahmini yapan bir yazılım modülü.
* **Analiz Raporu:** Hangi değişkenlerin inme riskini ne kadar artırdığını gösteren grafiksel raporlar.
* **Açık Kaynak Reposu:** Temizlenmiş veri seti ve modelleme kodlarını içeren, yazılım mühendisliği standartlarına uygun bir GitHub projesi.
---

