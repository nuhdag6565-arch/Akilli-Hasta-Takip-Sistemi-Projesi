# Akıllı Hasta Takip Sistemi - Proje Akışı ve Haftalık İlerleme

Bu dosya, takımımızın haftalık proje ilerlemesini, alınan teknik kararları ve üyelerin görev dağılımlarını içermektedir.

---

## 1. Hafta Geliştirmeleri ve Görev Dağılımı

* **Nuh Dağ (Scrum Master):** GitHub reposu oluşturuldu, branch koruma kuralları ayarlandı. Kaggle'dan "İnme (Stroke) Riski" veri seti temin edilerek ön işleme tamamlandı ve (`temizlenmis_hasta_verisi.csv`) repoya eklendi.
* **Necmihan Aksu:** [Bu hafta ne yaptığı buraya yazılacak]
* **Aslıhan İlhan:** [Bu hafta ne yaptığı buraya yazılacak]

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

#### 6. Sonuç
Proje kapsamında Python tabanlı, lokal ortamda çalışan, SMOTE ile veri dengesizliği giderilmiş ve Random Forest ile %94 bandında doğruluk oranına ulaşan bir makine öğrenimi sistemi geliştirilmiştir. Bu sistemin Streamlit aracılığıyla modern bir web arayüzüne entegre edilmesi, projenin kullanılabilir bir yazılım ürününe dönüşmesini sağlamıştır.
