"""
Modül Adı: setup_db.py
Açıklama : Veritabanını sıfırdan kurar.
           - MongoDB koleksiyonları ve indeksler oluşturulur.
           - 3 örnek doktor hesabı (frontend SEED ile aynı TC/şifre) eklenir.
           - CSV varsa hasta verileri aktarılır, yoksa 50 örnek hasta üretilir.

Kullanım :
    python -m database.setup_db
    veya
    python database/setup_db.py

Doktor Giriş Bilgileri:
    TC            | Şifre     | Uzmanlık
    --------------|-----------|------------------
    12345678901   | sifre123  | Nöroloji
    98765432109   | sifre123  | Kardiyoloji
    11122233344   | sifre123  | İç Hastalıkları

Güvenlik sorusu cevapları (şifremi unuttum):
    DR-00001 → yılmaz
    DR-00002 → kaya
    DR-00003 → demir

Sorumlu : Nuh Dağ (Veritabanı)
Tarih   : 2026-05-15
Version : 1.0
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.seed_data import veritabanini_hazirla


if __name__ == "__main__":
    csv_yolu = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "processed", "temizlenmis_hasta_verisi.csv"
    )
    basarili = veritabanini_hazirla(csv_yolu=csv_yolu)
    sys.exit(0 if basarili else 1)
