from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def database_baglantisi_kur():
    # MongoDB varsayılan olarak localhost:27017 portunda calisir
    uri = "mongodb://localhost:27017/"
    
    try:
        # Baglanti istemcisini olusturuyoruz
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Baglantiyi test ediyoruz
        client.admin.command('ping')
        print("✅ MongoDB Veri Tabanina Basariyla Baglanildi!")
        
        # 'HastaTakipDB' adinda bir veri tabani olusturuyoruz (veya varsa baglaniyoruz)
        db = client["HastaTakipDB"]
        return db

    except ConnectionFailure:
        print("❌ HATA: MongoDB sunucusuna ulasilamadi. Lutfen MongoDB'nin calistiginden emin olun.")
        return None

if __name__ == "__main__":
    database_baglantisi_kur()