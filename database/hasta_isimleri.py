"""
Modül Adı: hasta_islemleri.py
Açıklama : Hasta kayıtları için tam CRUD işlemleri.
           Doktor muayene formundan gelen verileri veritabanına yazar.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0

İçindeki fonksiyonlar
──────────────────────
  hasta_ekle()          → Yeni hasta kaydı aç
  tibbi_bilgi_ekle()    → Muayene verisini kaydet
  yasam_tarzi_guncelle()→ Yaşam tarzı bilgilerini kaydet/güncelle
  hasta_getir()         → Tek hastanın tüm kaydını getir
  hasta_ara()           → Ad/soyad ile hasta arama
  hastalari_listele()   → Tüm hastaları listele
  hasta_guncelle()      → Hasta bilgilerini güncelle
  muayene_gecmisi()     → Hastanın geçmiş muayeneleri
"""

from datetime import datetime
from database.connection import baglanti_olustur


# ════════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ════════════════════════════════════════════════════════════════

def _hasta_id_olustur(db) -> str:
    """
    Sıradaki hasta ID'sini üretir.  HS-00001, HS-00002, …

    Args:
        db: MongoDB veritabanı nesnesi
    Returns:
        str: HS-XXXXX formatında benzersiz ID
    """
    toplam = db.hastalar.count_documents({})
    return f"HS-{str(toplam + 1).zfill(5)}"


def _kayit_id_olustur(db) -> str:
    """
    Sıradaki tıbbi kayıt ID'sini üretir.  TK-00001, TK-00002, …
    """
    toplam = db.tibbi_bilgiler.count_documents({})
    return f"TK-{str(toplam + 1).zfill(5)}"


# ════════════════════════════════════════════════════════════════
# HASTA EKLEME
# ════════════════════════════════════════════════════════════════

def hasta_ekle(
    ad: str,
    soyad: str,
    yas: int,
    cinsiyet: str,
    telefon: str = "",
    email: str = "",
    dogum_tarihi: str = "",
) -> dict:
    """
    Yeni hasta kaydı oluşturur.

    Args:
        ad          : Hastanın adı
        soyad       : Hastanın soyadı
        yas         : Hastanın yaşı (tam sayı)
        cinsiyet    : "Erkek" veya "Kadın"
        telefon     : (opsiyonel) Telefon numarası
        email       : (opsiyonel) E-posta adresi
        dogum_tarihi: (opsiyonel) "YYYY-MM-DD" formatında

    Returns:
        dict: {"basarili": True/False, "hasta_id": "...", "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False, "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # ── Girdi doğrulama ────────────────────────────────────────
    if not ad or not ad.strip():
        return {"basarili": False, "mesaj": "Ad boş bırakılamaz."}
    if not soyad or not soyad.strip():
        return {"basarili": False, "mesaj": "Soyad boş bırakılamaz."}
    if not isinstance(yas, int) or not (0 <= yas <= 130):
        return {"basarili": False, "mesaj": "Yaş 0-130 arasında tam sayı olmalıdır."}
    if cinsiyet not in ("Erkek", "Kadın"):
        return {"basarili": False, "mesaj": "Cinsiyet 'Erkek' veya 'Kadın' olmalıdır."}

    try:
        hasta_id = _hasta_id_olustur(db)

        belge = {
            "hasta_id":     hasta_id,
            "ad":           ad.strip().title(),
            "soyad":        soyad.strip().upper(),
            "yas":          yas,
            "cinsiyet":     cinsiyet,
            "telefon":      telefon.strip(),
            "email":        email.strip().lower(),
            "dogum_tarihi": dogum_tarihi,
            "kayit_tarihi": datetime.now(),
            "aktif":        True,
        }

        db.hastalar.insert_one(belge)

        print(f"✅ Hasta eklendi → {hasta_id}  |  {ad.strip().title()} {soyad.strip().upper()}")
        return {"basarili": True, "hasta_id": hasta_id,
                "mesaj": f"Hasta başarıyla eklendi. ID: {hasta_id}"}

    except Exception as e:
        return {"basarili": False, "mesaj": f"Hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# TIBBİ BİLGİ EKLEME  (Muayene Formu)
# ════════════════════════════════════════════════════════════════

def tibbi_bilgi_ekle(
    hasta_id: str,
    doktor_id: str,
    hipertansiyon: int,
    kalp_hastaligi: int,
    ortalama_seker: float,
    vucut_kitle_indeksi: float,
    sikayet: str = "",
    tani_notu: str = "",
    ilac_recetesi: list = None,
) -> dict:
    """
    Doktorun muayene formundan girdiği klinik verileri kaydeder.
    Bu veriler ML modeline gönderilecek.

    Args:
        hasta_id            : Hangi hastanın kaydı  (HS-XXXXX)
        doktor_id           : Muayeneyi yapan doktor (DR-XXXXX)
        hipertansiyon       : 0=Yok  1=Var
        kalp_hastaligi      : 0=Yok  1=Var
        ortalama_seker      : mg/dL cinsinden ortalama kan şekeri
        vucut_kitle_indeksi : BMI (kg/m²)
        sikayet             : Hastanın şikayeti (serbest metin)
        tani_notu           : Doktorun tanı notu  (serbest metin)
        ilac_recetesi       : İlaç listesi  [{"ilaç": "...", "doz": "..."}, …]

    Returns:
        dict: {"basarili": True/False, "kayit_id": "...", "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False, "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # ── Hasta var mı? ──────────────────────────────────────────
    hasta = db.hastalar.find_one({"hasta_id": hasta_id})
    if hasta is None:
        return {"basarili": False,
                "mesaj": f"'{hasta_id}' ID'li hasta bulunamadı."}

    # ── Değer doğrulama ────────────────────────────────────────
    if hipertansiyon not in (0, 1):
        return {"basarili": False, "mesaj": "hipertansiyon 0 veya 1 olmalıdır."}
    if kalp_hastaligi not in (0, 1):
        return {"basarili": False, "mesaj": "kalp_hastaligi 0 veya 1 olmalıdır."}
    if ortalama_seker < 0:
        return {"basarili": False, "mesaj": "Kan şekeri negatif olamaz."}
    if vucut_kitle_indeksi < 0:
        return {"basarili": False, "mesaj": "BMI negatif olamaz."}

    try:
        kayit_id = _kayit_id_olustur(db)

        belge = {
            "kayit_id":             kayit_id,
            "hasta_id":             hasta_id,
            "doktor_id":            doktor_id,
            "muayene_tarihi":       datetime.now(),

            # ML modeline gidecek klinik değerler
            "hipertansiyon":        hipertansiyon,
            "kalp_hastaligi":       kalp_hastaligi,
            "ortalama_seker":       float(ortalama_seker),
            "vucut_kitle_indeksi":  float(vucut_kitle_indeksi),

            # Doktor notları
            "sikayet":              sikayet.strip(),
            "tani_notu":            tani_notu.strip(),
            "ilac_recetesi":        ilac_recetesi or [],

            "olusturma_tarihi":     datetime.now(),
        }

        db.tibbi_bilgiler.insert_one(belge)

        print(f"✅ Tıbbi kayıt eklendi → {kayit_id}  |  Hasta: {hasta_id}")
        return {"basarili": True, "kayit_id": kayit_id,
                "mesaj": f"Tıbbi bilgi başarıyla kaydedildi. Kayıt ID: {kayit_id}"}

    except Exception as e:
        return {"basarili": False, "mesaj": f"Hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# YAŞAM TARZI KAYDETME / GÜNCELLEME
# ════════════════════════════════════════════════════════════════

def yasam_tarzi_guncelle(
    hasta_id: str,
    evli_mi: str = "Hayır",
    calisma_tipi: str = "Çalışan",
    ikamet_tipi: str = "Kentsel",
    sigara_durumu: str = "Eski İçici",
) -> dict:
    """
    Hastanın yaşam tarzı bilgilerini kaydeder veya günceller.
    Her hastanın en fazla 1 yaşam tarzı kaydı olur (upsert).

    Args:
        hasta_id       : HS-XXXXX formatında hasta ID
        evli_mi        : "Evet" | "Hayır" | "Eski" | "Hiç"
        calisma_tipi   : "Özel Sektör" | "Kamu" | "Serbest Meslek" |
                         "Emekli" | "Öğrenci" | "İşsiz" | "Çocuk"
        ikamet_tipi    : "Kentsel" | "Kırsal"
        sigara_durumu  : "Hiç İçmedi" | "Eski İçici" | "Halen İçiyor"

    Returns:
        dict: {"basarili": True/False, "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False, "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # Geçerli değerler model/train.py KATEGORIK_ESLESME ile aynı
    gecerli_evlilik = {"Evet", "Hayır"}
    gecerli_calisma = {"Çalışan", "Çocuk", "Hükümet", "İşsiz", "Serbest"}
    gecerli_ikamet  = {"Kentsel", "Kırsal"}
    gecerli_sigara  = {"Eski İçici", "Halen İçiyor"}

    if evli_mi not in gecerli_evlilik:
        return {"basarili": False, "mesaj": f"Geçersiz evlilik durumu: {evli_mi}. Geçerli: {gecerli_evlilik}"}
    if calisma_tipi not in gecerli_calisma:
        return {"basarili": False, "mesaj": f"Geçersiz çalışma tipi: {calisma_tipi}. Geçerli: {gecerli_calisma}"}
    if ikamet_tipi not in gecerli_ikamet:
        return {"basarili": False, "mesaj": f"Geçersiz ikamet tipi: {ikamet_tipi}. Geçerli: {gecerli_ikamet}"}
    if sigara_durumu not in gecerli_sigara:
        return {"basarili": False, "mesaj": f"Geçersiz sigara durumu: {sigara_durumu}. Geçerli: {gecerli_sigara}"}

    try:
        db.yasam_tarzi.update_one(
            {"hasta_id": hasta_id},
            {"$set": {
                "hasta_id":         hasta_id,
                "evli_mi":          evli_mi,
                "calisma_tipi":     calisma_tipi,
                "ikamet_tipi":      ikamet_tipi,
                "sigara_durumu":    sigara_durumu,
                "guncelleme_tarihi": datetime.now(),
            }},
            upsert=True   # Yoksa oluştur, varsa güncelle
        )

        print(f"✅ Yaşam tarzı güncellendi → Hasta: {hasta_id}")
        return {"basarili": True, "mesaj": "Yaşam tarzı bilgileri kaydedildi."}

    except Exception as e:
        return {"basarili": False, "mesaj": f"Hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# VERİ OKUMA FONKSİYONLARI
# ════════════════════════════════════════════════════════════════

def hasta_getir(hasta_id: str) -> dict | None:
    """
    Tek bir hastanın tüm bilgilerini getirir.
    (demografik + yaşam tarzı + son tıbbi kayıt)

    Args:
        hasta_id: HS-XXXXX formatında hasta ID

    Returns:
        dict: Hasta bilgileri  |  None: Bulunamazsa
    """
    db = baglanti_olustur()
    if db is None:
        return None

    hasta = db.hastalar.find_one({"hasta_id": hasta_id}, {"_id": 0})
    if hasta is None:
        return None

    # Yaşam tarzı bilgisini ekle
    yt = db.yasam_tarzi.find_one({"hasta_id": hasta_id}, {"_id": 0})
    hasta["yasam_tarzi"] = yt or {}

    # Son tıbbi kaydı ekle
    son_kayit = db.tibbi_bilgiler.find_one(
        {"hasta_id": hasta_id},
        {"_id": 0},
        sort=[("muayene_tarihi", -1)]
    )
    hasta["son_tibbi_kayit"] = son_kayit or {}

    # Son risk tahminini ekle
    son_tahmin = db.inme_risk_tahminleri.find_one(
        {"hasta_id": hasta_id},
        {"_id": 0},
        sort=[("tahmin_tarihi", -1)]
    )
    hasta["son_risk_tahmini"] = son_tahmin or {}

    return hasta


def hasta_ara(ad: str = "", soyad: str = "") -> list:
    """
    Ad veya soyad ile hasta arar (büyük/küçük harf duyarsız).

    Args:
        ad   : Aranacak ad (kısmi eşleşme desteklenir)
        soyad: Aranacak soyad (kısmi eşleşme desteklenir)

    Returns:
        list: Eşleşen hasta listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    filtre = {}
    if ad.strip():
        # i = case-insensitive
        filtre["ad"] = {"$regex": ad.strip(), "$options": "i"}
    if soyad.strip():
        filtre["soyad"] = {"$regex": soyad.strip(), "$options": "i"}

    if not filtre:
        return []

    sonuclar = list(db.hastalar.find(filtre, {"_id": 0}))
    return sonuclar


def hastalari_listele(limit: int = 50, sadece_aktif: bool = True) -> list:
    """
    Kayıtlı hastaları listeler.

    Args:
        limit       : Maksimum kaç hasta dönsün (varsayılan 50)
        sadece_aktif: True ise sadece aktif hastalar

    Returns:
        list: Hasta listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    filtre = {"aktif": True} if sadece_aktif else {}
    return list(
        db.hastalar
        .find(filtre, {"_id": 0})
        .sort("kayit_tarihi", -1)
        .limit(limit)
    )


def muayene_gecmisi(hasta_id: str, limit: int = 10) -> list:
    """
    Hastanın geçmiş muayenelerini en yeniden eskiye sıralar.

    Args:
        hasta_id: HS-XXXXX formatında hasta ID
        limit   : Kaç kayıt dönsün (varsayılan 10)

    Returns:
        list: Muayene kayıtları listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    return list(
        db.tibbi_bilgiler
        .find({"hasta_id": hasta_id}, {"_id": 0})
        .sort("muayene_tarihi", -1)
        .limit(limit)
    )


def hasta_guncelle(hasta_id: str, guncellemeler: dict) -> dict:
    """
    Hastanın temel bilgilerini günceller.

    Args:
        hasta_id     : Güncellenecek hastanın ID'si
        guncellemeler: Güncellenecek alan-değer çiftleri
                       Örn: {"telefon": "05551234567", "email": "..."}

    Returns:
        dict: {"basarili": True/False, "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False, "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # Kritik alanların üzerine yazılmasını engelle
    korunan = {"hasta_id", "_id", "kayit_tarihi"}
    temiz   = {k: v for k, v in guncellemeler.items() if k not in korunan}

    if not temiz:
        return {"basarili": False, "mesaj": "Güncellenecek geçerli alan bulunamadı."}

    try:
        sonuc = db.hastalar.update_one(
            {"hasta_id": hasta_id},
            {"$set": temiz}
        )
        if sonuc.matched_count == 0:
            return {"basarili": False, "mesaj": f"'{hasta_id}' bulunamadı."}

        return {"basarili": True, "mesaj": "Hasta bilgileri güncellendi."}

    except Exception as e:
        return {"basarili": False, "mesaj": f"Hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# HIZLI TEST
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("── Hasta işlemleri testi ──")

    # 1. Hasta ekle
    sonuc = hasta_ekle(
        ad="Ahmet", soyad="Yılmaz",
        yas=58, cinsiyet="Erkek",
        telefon="05551234567"
    )
    print(sonuc)
    hasta_id = sonuc.get("hasta_id")

    if hasta_id:
        # 2. Yaşam tarzı ekle
        print(yasam_tarzi_guncelle(
            hasta_id=hasta_id,
            evli_mi="Evet",
            calisma_tipi="Özel Sektör",
            ikamet_tipi="Kentsel",
            sigara_durumu="Halen İçiyor"
        ))

        # 3. Tıbbi bilgi ekle
        print(tibbi_bilgi_ekle(
            hasta_id=hasta_id,
            doktor_id="DR-00001",
            hipertansiyon=1,
            kalp_hastaligi=0,
            ortalama_seker=148.5,
            vucut_kitle_indeksi=29.3,
            sikayet="Sık baş dönmesi",
        ))

        # 4. Hastayı getir
        import json
        h = hasta_getir(hasta_id)
        print(json.dumps(h, default=str, ensure_ascii=False, indent=2))