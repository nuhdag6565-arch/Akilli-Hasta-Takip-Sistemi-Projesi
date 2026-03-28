import pandas as pd
from datetime import datetime
from connection import baglanti_olustur
from schema import koleksiyonlari_olustur

def veri_yukle():
    db = baglanti_olustur()
    if db is None:
        return

    koleksiyonlari_olustur()

    try:
        df = pd.read_csv("data/processed/temizlenmis_hasta_verisi.csv")
        print(f"CSV okundu: {len(df)} hasta kaydi bulundu.")
    except FileNotFoundError:
        print("Hata: CSV dosyasi bulunamadi!")
        return

    db.hastalar.delete_many({})
    db.tibbi_kayitlar.delete_many({})
    print("Eski veriler temizlendi.")

    eklenen = 0
    for _, satir in df.iterrows():
        hasta = {
            "hasta_id": int(satir.get("hasta_id", 0)),
            "cinsiyet": str(satir.get("cinsiyet", "")),
            "yas": float(satir.get("yas", 0)),
            "hipertansiyon": int(satir.get("hipertansiyon", 0)),
            "kalp_hastaligi": int(satir.get("kalp_hastaligi", 0)),
            "evli_mi": str(satir.get("evli_mi", "")),
            "calisma_tipi": str(satir.get("calisma_tipi", "")),
            "ikamet_tipi": str(satir.get("ikamet_tipi", "")),
            "ortalama_seker": float(satir.get("ortalama_seker", 0)),
            "vucut_kitle_indeksi": float(satir.get("vucut_kitle_indeksi", 0)),
            "sigara_durumu": str(satir.get("sigara_durumu", "")),
            "inme_durumu": int(satir.get("inme_durumu", 0)),
            "yuklenme_tarihi": datetime.now()
        }
        db.hastalar.insert_one(hasta)
        eklenen += 1

    print(f"Toplam {eklenen} hasta kaydi aktarildi!")
    print(f"Veritabani kayit sayisi: {db.hastalar.count_documents({})}")

if __name__ == "__main__":
    veri_yukle()