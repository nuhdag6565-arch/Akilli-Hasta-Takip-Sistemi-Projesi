"""
Modül Adı: connection.py
Açıklama : MongoDB bağlantısını yönetir. Tüm veritabanı modülleri
           bu dosyadan bağlantı alır.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os

# ── Ayarlar (ortam değişkeninden al, yoksa varsayılanı kullan) ──────────────
MONGO_URL       = os.getenv("MONGO_URL",      "mongodb://localhost:27017/")
VERITABANI_ADI  = os.getenv("VERITABANI_ADI", "inme_risk_sistemi")


# ── Tek bir global client nesnesi (bağlantı havuzu) ─────────────────────────
_client = None


def baglanti_olustur():
    """
    MongoDB'ye bağlanır ve veritabanı nesnesini döndürür.
    Bağlantı havuzu sayesinde aynı client tekrar kullanılır.

    Returns:
        db (Database): MongoDB veritabanı nesnesi.
        None          : Bağlantı kurulamazsa None döner.
    """
    global _client
    try:
        if _client is None:
            _client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)

        # Sunucu canlı mı?
        _client.admin.command("ping")
        return _client[VERITABANI_ADI]

    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("=" * 55)
        print("HATA: MongoDB'ye bağlanılamadı!")
        print("  → 'mongod' komutunu çalıştırdığınızdan emin olun.")
        print("  → Bağlantı adresi:", MONGO_URL)
        print("=" * 55)
        return None

    except Exception as e:
        print(f"Beklenmeyen bağlantı hatası: {e}")
        return None


def baglanti_kapat():
    """Global MongoDB client bağlantısını kapatır."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("MongoDB bağlantısı kapatıldı.")


# ── Bağımsız test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db = baglanti_olustur()
    if db is not None:
        print("Bağlantı başarılı!")
        print("Veritabanı adı  :", db.name)
        print("Mevcut koleksiyonlar:", db.list_collection_names())
    baglanti_kapat()