from database.connection import baglanti_olustur
from datetime import datetime
import hashlib

def sifre_hashle(sifre):
    """Şifreyi güvenli hale getirir."""
    return hashlib.sha256(sifre.encode()).hexdigest()

def kullanici_no_olustur(db):
    """Otomatik artan kullanıcı numarası üretir. KL-0001, KL-0002..."""
    toplam = db.kullanicilar.count_documents({})
    return f"KL-{str(toplam + 1).zfill(4)}"

def tc_dogrula(tc):
    """TC kimlik numarasının geçerli olup olmadığını kontrol eder."""
    if len(str(tc)) != 11:
        return False
    if str(tc)[0] == "0":
        return False
    return True

def doktor_ekle(ad, soyad, tc_no, uzmanlik, telefon, sifre, email=None, departman=None):
    """Yeni doktor kaydı ekler."""
    db = baglanti_olustur()
    if db is None:
        return

    # TC doğrulama
    if not tc_dogrula(tc_no):
        print(f"Hata: Geçersiz TC kimlik numarası!")
        return None

    # Aynı TC ile kayıt var mı?
    mevcut = db.kullanicilar.find_one({"tc_no": str(tc_no)})
    if mevcut:
        print(f"Hata: {tc_no} TC numarası zaten kayıtlı!")
        print(f"  Kayıtlı kişi: Dr. {mevcut['ad']} {mevcut['soyad']} [{mevcut['kullanici_no']}]")
        return None

    if email is None:
        email = f"{ad.lower()}.{soyad.lower()}@hospital.com"
    
    if departman is None:
        departman = f"{uzmanlik} Kliniği"

    kullanici_no = kullanici_no_olustur(db)

    doktor = {
        "kullanici_no": kullanici_no,
        "tc_no": str(tc_no),
        "ad": ad,
        "soyad": soyad,
        "email": email,
        "uzmanlık_alani": uzmanlik,
        "departman": departman,
        "telefon": telefon,
        "rol": "doktor",
        "sifre_hash": sifre_hashle(sifre),
        "kayit_tarihi": datetime.now(),
        "olusturma_tarihi": datetime.now(),
        "aktif": True
    }

    sonuc = db.kullanicilar.insert_one(doktor)
    print(f"Doktor eklendi!")
    print(f"  Kullanıcı No: {kullanici_no}")
    print(f"  TC No      : {tc_no}")
    print(f"  Ad         : Dr. {ad} {soyad}")
    print(f"  Uzmanlık   : {uzmanlik}")
    print(f"  ID         : {sonuc.inserted_id}")
    return kullanici_no

def doktorlari_listele():
    """Tüm doktorları listeler."""
    db = baglanti_olustur()
    if db is None:
        return

    doktorlar = list(db.kullanicilar.find({"rol": "doktor"}))
    if not doktorlar:
        print("Henüz kayıtlı doktor yok.")
        return

    print(f"\nKayıtlı doktorlar ({len(doktorlar)} kişi):")
    for d in doktorlar:
        print(f"  [{d['kullanici_no']}] Dr. {d['ad']} {d['soyad']} | TC: {d['tc_no']} | {d['uzmanlık_alani']} | {d['telefon']}")

if __name__ == "__main__":
    # Eski kullanıcı kayıtlarını temizle
    db = baglanti_olustur()
    if db is not None:
        db.kullanicilar.delete_many({})
        print("Eski kullanıcı kayıtları temizlendi.\n")

    # Örnek doktor kayıtları
    doktor_ekle("Ayse", "Kaya", 12345678901, "Kardiyoloji", "0532-111-2233", "sifre123")
    doktor_ekle("Ayse", "Kaya", 98765432109, "Kardiyoloji", "0533-222-3344", "sifre456")
    doktor_ekle("Mehmet", "Demir", 11122233344, "Nöroloji", "0533-444-5566", "sifre789")

    # Aynı TC ile tekrar eklemeye çalış — engellenmeli
    doktor_ekle("Ayse", "Kaya", 12345678901, "Kardiyoloji", "0532-111-2233", "sifre123")

    doktorlari_listele()
