"""
Modül Adı: doktor_islemleri.py
Açıklama : Doktor hesap yönetimi.

           ┌─────────────────────────────────────────────────────┐
           │  İLK KAYIT                                          │
           │  TC + Ad + Soyad + Uzmanlık + Şifre + Şifre Tekrar │
           │  + Güvenlik Sorusu Cevabı (şifre sıfırlama için)   │
           ├─────────────────────────────────────────────────────┤
           │  SONRAKI GİRİŞLER                                   │
           │  Sadece TC + Şifre                                  │
           ├─────────────────────────────────────────────────────┤
           │  PROFİL SAYFASI                                     │
           │  Ad, Soyad, Uzmanlık, TC, Kayıt Tarihi, Son Giriş  │
           ├─────────────────────────────────────────────────────┤
           │  ŞİFREMİ UNUTTUM                                    │
           │  TC + Güvenlik Sorusu Cevabı → Yeni şifre belirle  │
           └─────────────────────────────────────────────────────┘

Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 5.0
"""

import hashlib
import re
from datetime import datetime
from database.connection import baglanti_olustur


# ════════════════════════════════════════════════════════════════
# SABİTLER
# ════════════════════════════════════════════════════════════════

# Şifremi unuttum ekranında doktora sorulacak soru
GUVENLIK_SORUSU = "Annenizin kızlık soyadı nedir?"

GECERLI_UZMANLIKLAR = [
    "Nöroloji",
    "Kardiyoloji",
    "İç Hastalıkları",
    "Genel Cerrahi",
    "Ortopedi",
    "Göğüs Hastalıkları",
    "Endokrinoloji",
    "Psikiyatri",
    "Radyoloji",
    "Diğer",
]


# ════════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ════════════════════════════════════════════════════════════════

def _hashle(metin: str) -> str:
    """
    Verilen metni SHA-256 ile hashler.
    Şifre ve güvenlik sorusu cevabı için kullanılır.

    Args:
        metin: Hashlenecek ham metin

    Returns:
        str: 64 karakterlik SHA-256 hash
    """
    return hashlib.sha256(metin.strip().encode("utf-8")).hexdigest()


def _tc_dogrula(tc: str) -> bool:
    """
    TC kimlik numarasının formatını kontrol eder.
    - 11 haneli olmalı
    - Rakamlardan oluşmalı
    - 0 ile başlamamalı

    Args:
        tc: Kontrol edilecek TC numarası

    Returns:
        bool: Geçerliyse True, değilse False
    """
    tc = tc.strip()
    if not tc.isdigit():
        return False
    if len(tc) != 11:
        return False
    if tc[0] == "0":
        return False
    return True


def _doktor_id_olustur(db) -> str:
    """
    Sıradaki doktor ID'sini üretir.
    DR-00001, DR-00002, DR-00003 ...
    """
    toplam = db.doktorlar.count_documents({})
    return f"DR-{str(toplam + 1).zfill(5)}"


# ════════════════════════════════════════════════════════════════
# 1. İLK KAYIT
#    TC + Ad + Soyad + Uzmanlık + Şifre + Güvenlik Cevabı
# ════════════════════════════════════════════════════════════════

def doktor_kayit(
    tc_no: str,
    ad: str,
    soyad: str,
    uzmanlik: str,
    sifre: str,
    sifre_tekrar: str,
    guvenlik_cevabi: str,
) -> dict:
    """
    Yeni doktor hesabı oluşturur.
    Bu fonksiyon sadece ilk kayıt sırasında çağrılır.
    Bir sonraki girişte sadece TC + şifre yeterlidir.

    Args:
        tc_no           : 11 haneli TC kimlik numarası
        ad              : Doktorun adı
        soyad           : Doktorun soyadı
        uzmanlik        : Uzmanlık alanı
        sifre           : Seçilen şifre (en az 6 karakter)
        sifre_tekrar    : Şifre doğrulama
        guvenlik_cevabi : Şifremi unuttum ekranında kullanılacak
                          güvenlik sorusunun cevabı
                          Soru: "Annenizin kızlık soyadı nedir?"

    Returns:
        dict: {
            "basarili" : True / False,
            "doktor_id": "DR-00001",
            "mesaj"    : "..."
        }
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False,
                "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # ── TC doğrulama ───────────────────────────────────────────
    if not _tc_dogrula(tc_no):
        return {
            "basarili": False,
            "mesaj": (
                "Geçersiz TC kimlik numarası. "
                "11 haneli, rakamlardan oluşan ve 0 ile başlamayan "
                "bir numara giriniz."
            ),
        }

    # ── Diğer alan doğrulamaları ───────────────────────────────
    if not ad or not ad.strip():
        return {"basarili": False, "mesaj": "Ad boş bırakılamaz."}

    if not soyad or not soyad.strip():
        return {"basarili": False, "mesaj": "Soyad boş bırakılamaz."}

    if not uzmanlik or not uzmanlik.strip():
        return {"basarili": False,
                "mesaj": "Uzmanlık alanı boş bırakılamaz."}

    if not sifre or len(sifre) < 6:
        return {"basarili": False,
                "mesaj": "Şifre en az 6 karakter olmalıdır."}

    if sifre != sifre_tekrar:
        return {"basarili": False,
                "mesaj": "Şifreler eşleşmiyor. Lütfen tekrar deneyin."}

    if not guvenlik_cevabi or not guvenlik_cevabi.strip():
        return {
            "basarili": False,
            "mesaj": (
                "Güvenlik sorusu cevabı boş bırakılamaz. "
                f"Soru: {GUVENLIK_SORUSU}"
            ),
        }

    # ── TC daha önce kayıtlı mı? ───────────────────────────────
    mevcut = db.doktorlar.find_one({"tc_no": tc_no.strip()})
    if mevcut:
        return {
            "basarili": False,
            "mesaj": (
                f"Bu TC numarası ({tc_no}) sisteme daha önce "
                f"kayıt edilmiş. Giriş yapmak için TC ve "
                f"şifrenizi kullanınız."
            ),
        }

    # ── Kayıt oluştur ──────────────────────────────────────────
    try:
        doktor_id = _doktor_id_olustur(db)

        belge = {
            "doktor_id":         doktor_id,
            "tc_no":             tc_no.strip(),

            # Profil bilgileri
            "ad":                ad.strip().title(),
            "soyad":             soyad.strip().upper(),
            "uzmanlik":          uzmanlik.strip(),

            # Güvenlik
            "sifre_hash":        _hashle(sifre),
            "guvenlik_sorusu":   GUVENLIK_SORUSU,
            "guvenlik_cevabi_hash": _hashle(guvenlik_cevabi),

            # Durum
            "aktif":             True,
            "kayit_tarihi":      datetime.now(),
            "son_giris":         None,
            "giris_sayisi":      0,
        }

        db.doktorlar.insert_one(belge)

        print(
            f"✅ Doktor kaydedildi → {doktor_id}  |  "
            f"Dr. {ad.strip().title()} {soyad.strip().upper()}  |  "
            f"TC: {tc_no.strip()}  |  {uzmanlik.strip()}"
        )

        return {
            "basarili":  True,
            "doktor_id": doktor_id,
            "mesaj": (
                f"Hesabınız oluşturuldu. "
                f"Bundan sonra sisteme TC numaranız "
                f"ve şifrenizle giriş yapabilirsiniz."
            ),
        }

    except Exception as e:
        return {"basarili": False, "mesaj": f"Beklenmeyen hata: {str(e)}"}


# ════════════════════════════════════════════════════════════════
# 2. SİSTEME GİRİŞ
#    Sadece TC + Şifre
# ════════════════════════════════════════════════════════════════

def doktor_giris(tc_no: str, sifre: str) -> dict:
    """
    Doktor TC kimlik numarası ve şifresiyle sisteme giriş yapar.
    Giriş başarılıysa profil bilgileri (ad, soyad, uzmanlık)
    döndürülür.

    Args:
        tc_no: 11 haneli TC kimlik numarası
        sifre: Kayıt sırasında belirlenen şifre

    Returns:
        dict: {
            "basarili": True / False,
            "doktor"  : { profil bilgileri },  ← başarılıysa
            "mesaj"   : "..."
        }

    Başarılı dönüş örneği:
        {
            "basarili": True,
            "doktor": {
                "doktor_id" : "DR-00001",
                "tc_no"     : "12345678901",
                "ad"        : "Fatma",
                "soyad"     : "KAYA",
                "uzmanlik"  : "Nöroloji",
                "kayit_tarihi": "...",
                "son_giris" : "...",
                "giris_sayisi": 5
            },
            "mesaj": "Hoş geldiniz Dr. Fatma KAYA (Nöroloji)"
        }
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False,
                "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # ── Boş alan kontrolü ──────────────────────────────────────
    if not tc_no or not tc_no.strip():
        return {"basarili": False,
                "mesaj": "TC kimlik numarası boş bırakılamaz."}

    if not sifre:
        return {"basarili": False,
                "mesaj": "Şifre boş bırakılamaz."}

    # ── Veritabanında ara ──────────────────────────────────────
    doktor = db.doktorlar.find_one(
        {"tc_no": tc_no.strip(), "aktif": True},
        {"_id": 0}
    )

    if doktor is None:
        return {
            "basarili": False,
            "mesaj": (
                f"Bu TC numarasına ({tc_no.strip()}) ait aktif "
                f"bir doktor hesabı bulunamadı. "
                f"Hesabınız yoksa kayıt olunuz."
            ),
        }

    # ── Şifre kontrolü ─────────────────────────────────────────
    if doktor.get("sifre_hash") != _hashle(sifre):
        return {"basarili": False,
                "mesaj": "Şifre hatalı. Lütfen tekrar deneyin."}

    # ── Giriş başarılı → kayıtları güncelle ───────────────────
    giris_zamani = datetime.now()
    db.doktorlar.update_one(
        {"tc_no": tc_no.strip()},
        {
            "$set": {"son_giris": giris_zamani},
            "$inc": {"giris_sayisi": 1},
        }
    )

    # Hassas alanları yanıttan çıkar
    doktor.pop("sifre_hash", None)
    doktor.pop("guvenlik_cevabi_hash", None)
    doktor["son_giris"]    = giris_zamani
    doktor["giris_sayisi"] = doktor.get("giris_sayisi", 0) + 1

    hosgeldin = (
        f"Hoş geldiniz Dr. {doktor['ad']} {doktor['soyad']}  "
        f"({doktor['uzmanlik']})"
    )

    print(f"✅ Giriş başarılı → {hosgeldin}")

    return {
        "basarili": True,
        "doktor":   doktor,
        "mesaj":    hosgeldin,
    }


# ════════════════════════════════════════════════════════════════
# 3. PROFİL GÖRÜNTÜLEME
#    Ad, Soyad, Uzmanlık, TC, Kayıt Tarihi, Son Giriş
# ════════════════════════════════════════════════════════════════

def doktor_profil_getir(tc_no: str) -> dict | None:
    """
    Doktorun profil sayfasında gösterilecek bilgileri döndürür.
    Şifre ve güvenlik cevabı dahil edilmez.

    Args:
        tc_no: 11 haneli TC kimlik numarası

    Returns:
        dict: Profil bilgileri  |  None: Bulunamazsa

    Dönen bilgiler:
        doktor_id, tc_no, ad, soyad, uzmanlik,
        kayit_tarihi, son_giris, giris_sayisi
    """
    db = baglanti_olustur()
    if db is None:
        return None

    profil = db.doktorlar.find_one(
        {"tc_no": tc_no.strip(), "aktif": True},
        {
            "_id": 0,
            "sifre_hash": 0,
            "guvenlik_cevabi_hash": 0,
        }
    )
    return profil


# ════════════════════════════════════════════════════════════════
# 4. ŞİFREMİ UNUTTUM
#    TC + Güvenlik Sorusu Cevabı → Yeni şifre belirle
# ════════════════════════════════════════════════════════════════

def guvenlik_sorusu_getir(tc_no: str) -> dict:
    """
    Şifremi unuttum ekranının 1. adımı.
    TC numarasına karşılık gelen güvenlik sorusunu döndürür.

    Args:
        tc_no: Şifresini sıfırlamak isteyen doktorun TC'si

    Returns:
        dict: {
            "basarili": True / False,
            "soru"    : "Annenizin kızlık soyadı nedir?",
            "mesaj"   : "..."
        }
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False,
                "mesaj": "Veritabanı bağlantısı kurulamadı."}

    doktor = db.doktorlar.find_one(
        {"tc_no": tc_no.strip(), "aktif": True},
        {"guvenlik_sorusu": 1, "_id": 0}
    )

    if doktor is None:
        return {
            "basarili": False,
            "mesaj": (
                f"Bu TC numarasına ({tc_no.strip()}) ait "
                f"kayıt bulunamadı."
            ),
        }

    return {
        "basarili": True,
        "soru":     doktor.get("guvenlik_sorusu", GUVENLIK_SORUSU),
        "mesaj":    "Güvenlik sorusu bulundu.",
    }


def sifre_sifirla(
    tc_no: str,
    guvenlik_cevabi: str,
    yeni_sifre: str,
    yeni_sifre_tekrar: str,
) -> dict:
    """
    Şifremi unuttum ekranının 2. adımı.
    Güvenlik sorusu cevabı doğrulanırsa yeni şifre belirlenir.

    Args:
        tc_no              : Doktorun TC kimlik numarası
        guvenlik_cevabi    : Güvenlik sorusunun cevabı
        yeni_sifre         : Belirlenmek istenen yeni şifre
        yeni_sifre_tekrar  : Yeni şifre doğrulama

    Returns:
        dict: {"basarili": True/False, "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False,
                "mesaj": "Veritabanı bağlantısı kurulamadı."}

    # ── Yeni şifre kuralları ───────────────────────────────────
    if not yeni_sifre or len(yeni_sifre) < 6:
        return {"basarili": False,
                "mesaj": "Yeni şifre en az 6 karakter olmalıdır."}

    if yeni_sifre != yeni_sifre_tekrar:
        return {"basarili": False,
                "mesaj": "Yeni şifreler eşleşmiyor."}

    if not guvenlik_cevabi or not guvenlik_cevabi.strip():
        return {"basarili": False,
                "mesaj": "Güvenlik sorusu cevabı boş bırakılamaz."}

    # ── Doktoru bul ────────────────────────────────────────────
    doktor = db.doktorlar.find_one(
        {"tc_no": tc_no.strip(), "aktif": True}
    )

    if doktor is None:
        return {
            "basarili": False,
            "mesaj": f"TC numarası ({tc_no.strip()}) bulunamadı.",
        }

    # ── Güvenlik cevabını doğrula ──────────────────────────────
    if doktor.get("guvenlik_cevabi_hash") != _hashle(guvenlik_cevabi):
        return {
            "basarili": False,
            "mesaj": (
                "Güvenlik sorusu cevabı yanlış. "
                "Lütfen kayıt sırasında girdiğiniz cevabı yazınız."
            ),
        }

    # ── Şifreyi güncelle ───────────────────────────────────────
    db.doktorlar.update_one(
        {"tc_no": tc_no.strip()},
        {"$set": {"sifre_hash": _hashle(yeni_sifre)}}
    )

    print(f"✅ Şifre sıfırlandı → TC: {tc_no.strip()}")

    return {
        "basarili": True,
        "mesaj": (
            "Şifreniz başarıyla sıfırlandı. "
            "Yeni şifrenizle giriş yapabilirsiniz."
        ),
    }


# ════════════════════════════════════════════════════════════════
# 5. ŞİFRE GÜNCELLEME  (Giriş yapılmışken)
#    Eski şifre + Yeni şifre
# ════════════════════════════════════════════════════════════════

def sifre_guncelle(
    tc_no: str,
    eski_sifre: str,
    yeni_sifre: str,
    yeni_sifre_tekrar: str,
) -> dict:
    """
    Giriş yapmış doktorun şifresini değiştirir.
    Eski şifre doğrulanmadan yeni şifre kabul edilmez.

    Args:
        tc_no             : Doktorun TC kimlik numarası
        eski_sifre        : Mevcut şifre (doğrulama için)
        yeni_sifre        : Yeni şifre
        yeni_sifre_tekrar : Yeni şifre tekrarı

    Returns:
        dict: {"basarili": True/False, "mesaj": "..."}
    """
    db = baglanti_olustur()
    if db is None:
        return {"basarili": False,
                "mesaj": "Veritabanı bağlantısı kurulamadı."}

    if yeni_sifre != yeni_sifre_tekrar:
        return {"basarili": False,
                "mesaj": "Yeni şifreler eşleşmiyor."}

    if len(yeni_sifre) < 6:
        return {"basarili": False,
                "mesaj": "Yeni şifre en az 6 karakter olmalıdır."}

    doktor = db.doktorlar.find_one({"tc_no": tc_no.strip()})

    if doktor is None:
        return {"basarili": False, "mesaj": "Doktor bulunamadı."}

    if doktor.get("sifre_hash") != _hashle(eski_sifre):
        return {"basarili": False,
                "mesaj": "Mevcut şifre hatalı."}

    db.doktorlar.update_one(
        {"tc_no": tc_no.strip()},
        {"$set": {"sifre_hash": _hashle(yeni_sifre)}}
    )

    print(f"✅ Şifre güncellendi → TC: {tc_no.strip()}")
    return {"basarili": True,
            "mesaj": "Şifreniz başarıyla güncellendi."}


# ════════════════════════════════════════════════════════════════
# 6. YARDIMCI OKUMA FONKSİYONLARI
# ════════════════════════════════════════════════════════════════

def doktorlari_listele() -> list:
    """
    Sistemdeki tüm aktif doktorları listeler.
    Şifre ve güvenlik bilgileri dahil edilmez.

    Returns:
        list: Doktor profil listesi
    """
    db = baglanti_olustur()
    if db is None:
        return []

    return list(
        db.doktorlar.find(
            {"aktif": True},
            {
                "_id": 0,
                "sifre_hash": 0,
                "guvenlik_cevabi_hash": 0,
            }
        ).sort("kayit_tarihi", -1)
    )


def uzmanliga_gore_doktorlar(uzmanlik: str) -> list:
    """
    Belirli uzmanlık alanındaki doktorları getirir.

    Args:
        uzmanlik: Örn. "Nöroloji"

    Returns:
        list: Eşleşen doktorlar
    """
    db = baglanti_olustur()
    if db is None:
        return []

    return list(
        db.doktorlar.find(
            {
                "uzmanlik": {"$regex": uzmanlik.strip(), "$options": "i"},
                "aktif": True,
            },
            {
                "_id": 0,
                "sifre_hash": 0,
                "guvenlik_cevabi_hash": 0,
            }
        )
    )


# ════════════════════════════════════════════════════════════════
# HIZLI TEST
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    def yazdir(baslik, veri):
        print(f"\n{'─'*50}")
        print(f"  {baslik}")
        print(f"{'─'*50}")
        print(json.dumps(veri, default=str, ensure_ascii=False, indent=2))

    print("\n" + "═"*50)
    print("  DOKTOR SİSTEM TESTİ")
    print("═"*50)

    # 1. Kayıt
    yazdir("1. İLK KAYIT", doktor_kayit(
        tc_no           = "12345678901",
        ad              = "Fatma",
        soyad           = "Kaya",
        uzmanlik        = "Nöroloji",
        sifre           = "sifre123",
        sifre_tekrar    = "sifre123",
        guvenlik_cevabi = "Yılmaz",
    ))

    # 2. Aynı TC tekrar kayıt → hata
    yazdir("2. AYNI TC TEKRAR KAYIT (hata bekleniyor)", doktor_kayit(
        tc_no="12345678901", ad="X", soyad="Y",
        uzmanlik="Kardiyoloji",
        sifre="abc123", sifre_tekrar="abc123",
        guvenlik_cevabi="test"
    ))

    # 3. Giriş (sadece TC + şifre)
    yazdir("3. GİRİŞ (TC + şifre)", doktor_giris(
        tc_no="12345678901",
        sifre="sifre123"
    ))

    # 4. Yanlış şifre
    yazdir("4. YANLIŞ ŞİFRE (hata bekleniyor)", doktor_giris(
        tc_no="12345678901",
        sifre="yanlis"
    ))

    # 5. Profil görüntüleme
    yazdir("5. PROFİL", doktor_profil_getir("12345678901"))

    # 6. Şifremi unuttum → güvenlik sorusunu getir
    yazdir("6. ŞİFREMİ UNUTTUM - Adım 1 (soru getir)",
           guvenlik_sorusu_getir("12345678901"))

    # 7. Güvenlik cevabıyla şifre sıfırla
    yazdir("7. ŞİFREMİ UNUTTUM - Adım 2 (şifre sıfırla)",
           sifre_sifirla(
               tc_no              = "12345678901",
               guvenlik_cevabi    = "Yılmaz",
               yeni_sifre         = "yenisifre456",
               yeni_sifre_tekrar  = "yenisifre456",
           ))

    # 8. Yeni şifre ile giriş
    yazdir("8. YENİ ŞİFRE İLE GİRİŞ", doktor_giris(
        tc_no="12345678901",
        sifre="yenisifre456"
    ))