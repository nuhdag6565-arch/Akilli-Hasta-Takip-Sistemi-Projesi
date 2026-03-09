# Gereksinim Toplama ve Belgeleme
## Akıllı Hasta Takip Sistemi

## 1. Gereksinim Toplama Süreci

Gereksinim toplama süreci, geliştirilecek sistemin kullanıcı ihtiyaçlarını ve teknik beklentilerini belirlemek amacıyla yapılan analiz aşamasıdır. Bu aşamada proje paydaşlarının beklentileri değerlendirilir ve sistemin gerçekleştirmesi gereken işlevler belirlenir.

Akıllı Hasta Takip Sistemi projesi için gereksinimler aşağıdaki paydaşlar dikkate alınarak belirlenmiştir:

- Hastalar
- Doktorlar
- Hastane yönetimi
- Yazılım geliştirme ekibi
- Veri analizi ekibi

Paydaşlardan elde edilen bilgiler doğrultusunda sistemin fonksiyonel ve teknik gereksinimleri oluşturulmuştur.

---

# 2. Veri Kaynağı Gereksinimleri

Proje kapsamında sağlık risk tahmini yapabilmek için bir veri seti kullanılacaktır. Bu veri seti Kaggle platformundan elde edilmiştir.

Veri seti proje ekibi tarafından temizlenmiş ve **temizlenmis_hasta_verisi.csv** adıyla proje deposuna eklenmiştir.

Bu veri seti:

- **5110 hasta kaydı**
- **12 sağlık değişkeni**

içermektedir.

Veri setinde bulunan temel değişkenler şunlardır:

- hasta_id
- cinsiyet
- yas
- hipertansiyon
- kalp_hastaligi
- evli_mi
- calisma_tipi
- ikamet_tipi
- ortalama_seker
- vucut_kitle_indeksi (BMI)
- sigara_durumu
- inme_durumu (hedef değişken)

Bu değişkenler kullanılarak hastaların sağlık durumları analiz edilecek ve olası riskler tahmin edilecektir.

**GR-01:** Sistem `temizlenmis_hasta_verisi.csv` dosyasındaki verileri kullanarak sağlık risk tahmini gerçekleştirebilmelidir.

---

# 3. Fonksiyonel Gereksinimler

Fonksiyonel gereksinimler sistemin gerçekleştirmesi gereken işlemleri tanımlar.

**FR-01:** Sistem CSV formatındaki veri setini okuyabilmelidir.

**FR-02:** Sistem hastalara ait sağlık verilerini analiz edebilmelidir.

**FR-03:** Sistem makine öğrenimi algoritmaları kullanarak sağlık risk tahmini yapabilmelidir.

**FR-04:** Sistem hastaların sağlık verilerine göre kişiselleştirilmiş öneriler sunabilmelidir.

**FR-05:** Sistem doktorların hastaların sağlık verilerini görüntüleyebileceği bir arayüz sağlamalıdır.

**FR-06:** Sistem riskli durumlarda kullanıcıya uyarı veya bildirim gönderebilmelidir.

---

# 4. Teknik (Fonksiyonel Olmayan) Gereksinimler

## Performans
Sistem büyük miktarda sağlık verisini hızlı ve verimli bir şekilde analiz edebilmelidir.

## Doğruluk
Kullanılacak makine öğrenimi modeli sağlık risk tahmini için **en az %80 doğruluk oranını hedeflemelidir.**

## Güvenlik
- Hastaların sağlık verileri güvenli bir şekilde saklanmalıdır.
- Veri erişimi yalnızca yetkili kullanıcılar tarafından yapılabilmelidir.

## Ölçeklenebilirlik
Sistem ileride daha fazla hasta verisi ile çalışabilecek şekilde tasarlanmalıdır.

## Kullanılabilirlik
Sistem kullanıcı dostu bir arayüze sahip olmalı ve hem hastalar hem de doktorlar tarafından kolayca kullanılabilmelidir.

---

# 5. Sistem Kısıtlamaları

- Sistem veri analizi için CSV formatındaki veri setlerini kullanacaktır.
- Kullanılacak veri seti proje deposunda bulunan **temizlenmis_hasta_verisi.csv** dosyasıdır.
- Sistem geliştirme süresi proje takvimi ile sınırlıdır.

---

# 6. Paydaşlarla Paylaşım

Belirlenen gereksinimler bir **Gereksinim Belirtim Belgesi (SRS)** içerisinde toplanacaktır. Bu belge proje ekibi ve diğer paydaşlarla paylaşılacak ve sistem geliştirme sürecinde referans doküman olarak kullanılacaktır.
