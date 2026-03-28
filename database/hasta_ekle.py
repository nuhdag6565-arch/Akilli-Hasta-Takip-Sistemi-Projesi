from connection import baglanti_olustur
from datetime import datetime

def hasta_no_olustur(db):
    """Otomatik artan hasta numarası üretir. HS-0001, HS-0002..."""
    toplam = db.hastalar.count_documents({})
    return f"HS-{str(toplam + 1).zfill(4)}"

def tc_dogrula(tc):
    """TC kimlik numarasının geçerli olup olmadığını kontrol eder."""
    if len(str(tc)) != 11:
        return False
    if str(tc)[0] == "0":
        return False
    return True

def hasta_ekle(ad, soyad, tc_no, dogum_yili, cinsiyet, telefon):
    """Yeni hasta kaydı ekler."""
    db = baglanti_olustur()
    if db is None:
        return

    # TC doğrulama
    if not tc_dogrula(tc_no):
        print(f"Hata: Geçersiz TC kimlik numarası!")
        return None

    # Aynı TC ile kayıt var mı?
    mevcut = db.hastalar.find_one({"tc_no": str(tc_no)})
    if mevcut:
        print(f"Hata: {tc_no} TC numarası zaten kayıtlı!")
        print(f"  Kayıtlı kişi: {mevcut['ad']} {mevcut['soyad']} [{mevcut['hasta_no']}]")
        return None

    hasta_no = hasta_no_olustur(db)

    hasta = {
        "hasta_no": hasta_no,
        "tc_no": str(tc_no),
        "ad": ad,
        "soyad": soyad,
        "dogum_yili": dogum_yili,
        "cinsiyet": cinsiyet,
        "telefon": telefon,
        "kayit_tarihi": datetime.now(),
        "aktif": True
    }

    sonuc = db.hastalar.insert_one(hasta)
    print(f"Hasta eklendi!")
    print(f"  Hasta No : {hasta_no}")
    print(f"  TC No    : {tc_no}")
    print(f"  Ad       : {ad} {soyad}")
    print(f"  Cinsiyet : {cinsiyet}")
    print(f"  ID       : {sonuc.inserted_id}")
    return hasta_no

def hastalari_listele():
    """Tüm hastaları listeler."""
    db = baglanti_olustur()
    if db is None:
        return

    hastalar = list(db.hastalar.find({"tc_no": {"$exists": True}}))
    if not hastalar:
        print("Henüz kayıtlı hasta yok.")
        return

    print(f"\nKayıtlı hastalar ({len(hastalar)} kişi):")
    for h in hastalar:
        print(f"  [{h['hasta_no']}] {h['ad']} {h['soyad']} | TC: {h['tc_no']} | {h['cinsiyet']} | {h['telefon']}")

if __name__ == "__main__":
    # İki Ahmet Yılmaz — farklı TC ile
    hasta_ekle("Ahmet", "Yilmaz", 12345678901, 1975, "Erkek", "0532-111-0001")
    hasta_ekle("Ahmet", "Yilmaz", 98765432109, 1983, "Erkek", "0533-222-0002")
    hasta_ekle("Zeynep", "Celik", 11122233344, 1990, "Kadin", "0535-333-0003")
    # Aynı TC ile tekrar eklemeye çalış — engellenmeli
    hasta_ekle("Ahmet", "Yilmaz", 12345678901, 1975, "Erkek", "0532-111-0001")
    hastalari_listele()