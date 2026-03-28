from connection import baglanti_olustur
from datetime import datetime
import hashlib

def sifre_hashle(sifre):
    """Şifreyi güvenli hale getirir."""
    return hashlib.sha256(sifre.encode()).hexdigest()

def doktor_no_olustur(db):
    """Otomatik artan doktor numarası üretir. DR-0001, DR-0002..."""
    toplam = db.doktorlar.count_documents({})
    return f"DR-{str(toplam + 1).zfill(4)}"

def tc_dogrula(tc):
    """TC kimlik numarasının geçerli olup olmadığını kontrol eder."""
    if len(str(tc)) != 11:
        return False
    if str(tc)[0] == "0":
        return False
    return True

def doktor_ekle(ad, soyad, tc_no, uzmanlik, telefon, sifre):
    """Yeni doktor kaydı ekler."""
    db = baglanti_olustur()
    if db is None:
        return

    # TC doğrulama
    if not tc_dogrula(tc_no):
        print(f"Hata: Geçersiz TC kimlik numarası!")
        return None

    # Aynı TC ile kayıt var mı?
    mevcut = db.doktorlar.find_one({"tc_no": str(tc_no)})
    if mevcut:
        print(f"Hata: {tc_no} TC numarası zaten kayıtlı!")
        print(f"  Kayıtlı kişi: Dr. {mevcut['ad']} {mevcut['soyad']} [{mevcut['doktor_no']}]")
        return None

    doktor_no = doktor_no_olustur(db)

    doktor = {
        "doktor_no": doktor_no,
        "tc_no": str(tc_no),
        "ad": ad,
        "soyad": soyad,
        "uzmanlik": uzmanlik,
        "telefon": telefon,
        "sifre_hash": sifre_hashle(sifre),
        "kayit_tarihi": datetime.now(),
        "aktif": True
    }

    sonuc = db.doktorlar.insert_one(doktor)
    print(f"Doktor eklendi!")
    print(f"  Doktor No: {doktor_no}")
    print(f"  TC No    : {tc_no}")
    print(f"  Ad       : Dr. {ad} {soyad}")
    print(f"  Uzmanlik : {uzmanlik}")
    print(f"  ID       : {sonuc.inserted_id}")
    return doktor_no

def doktorlari_listele():
    """Tüm doktorları listeler."""
    db = baglanti_olustur()
    if db is None:
        return

    doktorlar = list(db.doktorlar.find())
    if not doktorlar:
        print("Henüz kayıtlı doktor yok.")
        return

    print(f"\nKayıtlı doktorlar ({len(doktorlar)} kişi):")
    for d in doktorlar:
        print(f"  [{d['doktor_no']}] Dr. {d['ad']} {d['soyad']} | TC: {d['tc_no']} | {d['uzmanlik']} | {d['telefon']}")

if __name__ == "__main__":
    # Eski doktorları temizle
    from connection import baglanti_olustur
    db = baglanti_olustur()
    db.doktorlar.delete_many({})
    print("Eski doktor kayıtları temizlendi.\n")

    # İki Ayşe Kaya — farklı TC ile
    doktor_ekle("Ayse", "Kaya", 12345678901, "Kardiyoloji", "0532-111-2233", "sifre123")
    doktor_ekle("Ayse", "Kaya", 98765432109, "Kardiyoloji", "0533-222-3344", "sifre456")
    doktor_ekle("Mehmet", "Demir", 11122233344, "Noroloji", "0533-444-5566", "sifre789")

    # Aynı TC ile tekrar eklemeye çalış — engellenmeli
    doktor_ekle("Ayse", "Kaya", 12345678901, "Kardiyoloji", "0532-111-2233", "sifre123")

    doktorlari_listele()
