from pymongo import ASCENDING
from connection import baglanti_olustur

def koleksiyonlari_olustur():
    """Veritabanı koleksiyonlarını ve indekslerini oluşturur."""
    db = baglanti_olustur()
    if db is None:
        return

    mevcut = db.list_collection_names()

    # Koleksiyonları oluştur
    koleksiyonlar = [
        "kullanicilar",
        "hastalar", 
        "tibbi_kayitlar",
        "yasam_tarzi",
        "risk_tahminleri"
    ]

    for koleksiyon in koleksiyonlar:
        if koleksiyon not in mevcut:
            db.create_collection(koleksiyon)
            print(f"{koleksiyon} koleksiyonu oluşturuldu.")
        else:
            print(f"{koleksiyon} zaten mevcut, atlandı.")

    # İndeksler (hızlı arama için)
    db.hastalar.create_index([("kullanici_id", ASCENDING)])
    db.tibbi_kayitlar.create_index([("hasta_id", ASCENDING)])
    db.yasam_tarzi.create_index([("hasta_id", ASCENDING)])
    db.risk_tahminleri.create_index([("hasta_id", ASCENDING)])

    print("\nTüm koleksiyonlar hazır:")
    for k in db.list_collection_names():
        print(" -", k)

if __name__ == "__main__":
    koleksiyonlari_olustur()