from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB bağlantı adresi
MONGO_URL = "mongodb://localhost:27017/"
VERITABANI_ADI = "hasta_takip_sistemi"

def baglanti_olustur():
    """MongoDB'ye bağlanır ve veritabanı nesnesini döndürür."""
    try:
        client = MongoClient(MONGO_URL)
        client.admin.command("ping")
        print("MongoDB bağlantısı başarılı!")
        return client[VERITABANI_ADI]
    except ConnectionFailure:
        print("Hata: MongoDB'ye bağlanılamadı!")
        print("MongoDB servisinin çalıştığından emin ol.")
        return None

def baglanti_kapat(client):
    """MongoDB bağlantısını kapatır."""
    if client:
        client.close()
        print("Bağlantı kapatıldı.")

if __name__ == "__main__":
    db = baglanti_olustur()
    if db is not None:
        print("Veritabanı adı:", db.name)
        print("Mevcut koleksiyonlar:", db.list_collection_names())