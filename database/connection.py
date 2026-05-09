from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB bağlantı adresi
MONGO_URL = "mongodb://localhost:27017/"
VERITABANI_ADI = "akilli_hasta_takip_sistemi"

def baglanti_olustur():
    """Connect to MongoDB and return the database object."""
    try:
        client = MongoClient(MONGO_URL)
        client.admin.command("ping")
        print("MongoDB connection successful!")
        return client[VERITABANI_ADI]
    except ConnectionFailure:
        print("Error: Could not connect to MongoDB!")
        print("Ensure MongoDB service is running.")
        return None

def baglanti_kapat(client):
    """Close the MongoDB connection."""
    if client:
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    db = baglanti_olustur()
    if db is not None:
        print("Veritabanı adı:", db.name)
        print("Mevcut koleksiyonlar:", db.list_collection_names())
