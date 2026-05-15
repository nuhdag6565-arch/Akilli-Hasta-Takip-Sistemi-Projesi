"""
Modül Adı: seed_data.py
Açıklama : temizlenmis_hasta_verisi.csv dosyasından veritabanını
           başlangıç verileriyle doldurur.
           insert_many() kullanarak hızlı toplu ekleme yapar.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0
"""

import pandas as pd
from datetime import datetime
import random
from database.connection import baglanti_olustur
from database.schema import sema_olustur

# ── Kodlama → Metin eşlemeleri ─────────────────────────────────
SIGARA  = {0: "Hiç İçmedi", 1: "Halen İçiyor", 2: "Eski İçici"}
CALISMA = {
    0: "Özel Sektör", 1: "Kamu",
    2: "Serbest Meslek", 3: "Çocuk", 4: "Emekli"
}
EVLILIK = {0: "Hayır", 1: "Evet"}
IKAMET  = {0: "Kırsal", 1: "Kentsel"}
CINSIYET = {0: "Kadın", 1: "Erkek"}

# ── Örnek doktorlar ────────────────────────────────────────────
DOKTOR_LISTESI = [
    {
        "doktor_id":    "DR-00001",
        "ad":           "Fatma",
        "soyad":        "KAYA",
        "uzmanlik":     "Nöroloji",
        "email":        "fatma.kaya@hastane.com",
        "sifre_hash":   "demo_hash_1",
        "aktif":        True,
        "kayit_tarihi": datetime.now(),
    },
    {
        "doktor_id":    "DR-00002",
        "ad":           "Mehmet",
        "soyad":        "DEMİR",
        "uzmanlik":     "Kardiyoloji",
        "email":        "mehmet.demir@hastane.com",
        "sifre_hash":   "demo_hash_2",
        "aktif":        True,
        "kayit_tarihi": datetime.now(),
    },
    {
        "doktor_id":    "DR-00003",
        "ad":           "Ayşe",
        "soyad":        "ŞAHİN",
        "uzmanlik":     "İç Hastalıkları",
        "email":        "ayse.sahin@hastane.com",
        "sifre_hash":   "demo_hash_3",
        "aktif":        True,
        "kayit_tarihi": datetime.now(),
    },
]


def doktorlari_yukle(db):
    """3 örnek doktor hesabı oluşturur."""
    print("\n[1/4] Doktor hesapları yükleniyor...")
    db.doktorlar.delete_many({})
    db.doktorlar.insert_many(DOKTOR_LISTESI)
    print(f"  ✅  {len(DOKTOR_LISTESI)} doktor eklendi.")


def hastalari_yukle_csv(db, csv_yolu: str) -> bool:
    """
    CSV dosyasından hasta, tıbbi bilgi ve yaşam tarzı
    verilerini toplu olarak MongoDB'ye aktarır.
    """
    print("\n[2/4] Hasta verileri yükleniyor (CSV)...")

    try:
        df = pd.read_csv(csv_yolu)
        print(f"  CSV okundu: {len(df)} satır")
    except FileNotFoundError:
        print(f"  ⚠️   CSV bulunamadı: {csv_yolu}")
        print("       Örnek veri ile devam edilecek.")
        return False
    except Exception as e:
        print(f"  ❌  CSV okuma hatası: {e}")
        return False

    # Eski kayıtları temizle
    db.hastalar.delete_many({})
    db.tibbi_bilgiler.delete_many({})
    db.yasam_tarzi.delete_many({})

    hastalar_lst    = []
    tibbi_lst       = []
    yasam_tarzi_lst = []

    doktor_idleri = [d["doktor_id"] for d in DOKTOR_LISTESI]

    for idx, satir in df.iterrows():
        hasta_id = f"HS-{str(idx + 1).zfill(5)}"
        kayit_id = f"TK-{str(idx + 1).zfill(5)}"

        yas = int(satir.get("yas", 0))

        # ── hastalar koleksiyonu ────────────────────────────────
        hastalar_lst.append({
            "hasta_id":     hasta_id,
            "ad":           f"Hasta",
            "soyad":        f"{str(idx + 1).upper()}",
            "yas":          yas,
            "cinsiyet":     CINSIYET.get(int(satir.get("cinsiyet", 0)), "Erkek"),
            "telefon":      f"0555{str(idx).zfill(7)}",
            "email":        f"hasta{idx + 1}@ornek.com",
            "kayit_tarihi": datetime.now(),
            "aktif":        True,
        })

        # ── tibbi_bilgiler koleksiyonu ──────────────────────────
        tibbi_lst.append({
            "kayit_id":             kayit_id,
            "hasta_id":             hasta_id,
            "doktor_id":            random.choice(doktor_idleri),
            "muayene_tarihi":       datetime.now(),
            "hipertansiyon":        int(satir.get("hipertansiyon", 0)),
            "kalp_hastaligi":       int(satir.get("kalp_hastaligi", 0)),
            "ortalama_seker":       float(satir.get("ortalama_seker", 0.0)),
            "vucut_kitle_indeksi":  float(satir.get("vucut_kitle_indeksi", 0.0)),
            "sikayet":              "",
            "tani_notu":            "CSV verisinden aktarıldı.",
            "ilac_recetesi":        [],
            "olusturma_tarihi":     datetime.now(),
        })

        # ── yasam_tarzi koleksiyonu ─────────────────────────────
        yasam_tarzi_lst.append({
            "hasta_id":         hasta_id,
            "evli_mi":          EVLILIK.get(int(satir.get("evli_mi", 0)), "Hayır"),
            "calisma_tipi":     CALISMA.get(int(satir.get("calisma_tipi", 0)), "Özel Sektör"),
            "ikamet_tipi":      IKAMET.get(int(satir.get("ikamet_tipi", 0)), "Kentsel"),
            "sigara_durumu":    SIGARA.get(int(satir.get("sigara_durumu", 0)), "Hiç İçmedi"),
            "guncelleme_tarihi": datetime.now(),
        })

    # ── Toplu ekleme (insert_many ile çok daha hızlı) ──────────
    YIGIN = 1000   # Her seferinde 1000 kayıt ekle

    for i in range(0, len(hastalar_lst), YIGIN):
        db.hastalar.insert_many(hastalar_lst[i:i + YIGIN])

    for i in range(0, len(tibbi_lst), YIGIN):
        db.tibbi_bilgiler.insert_many(tibbi_lst[i:i + YIGIN])

    for i in range(0, len(yasam_tarzi_lst), YIGIN):
        db.yasam_tarzi.insert_many(yasam_tarzi_lst[i:i + YIGIN])

    h  = db.hastalar.count_documents({})
    tb = db.tibbi_bilgiler.count_documents({})
    yt = db.yasam_tarzi.count_documents({})

    print(f"  ✅  {h} hasta  |  {tb} tıbbi kayıt  |  {yt} yaşam tarzı eklendi.")
    return True


def ornek_veri_yukle(db, sayi: int = 50):
    """CSV yoksa elle yazılmış 50 örnek hasta üretir."""
    print(f"\n[2/4] {sayi} örnek hasta oluşturuluyor...")

    if db.hastalar.count_documents({}) > 0:
        print("  ℹ️   Zaten veri var, atlanıyor.")
        return

    isimler  = ["Ahmet", "Mehmet", "Ali", "Fatma", "Ayşe",
                "Zeynep", "Mustafa", "Hasan", "Hüseyin", "Emine"]
    soyisimler = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin",
                  "Arslan", "Doğan", "Aydın", "Yıldız", "Güneş"]

    doktor_idleri = [d["doktor_id"] for d in DOKTOR_LISTESI]

    hastalar_lst    = []
    tibbi_lst       = []
    yasam_tarzi_lst = []

    for i in range(sayi):
        hasta_id = f"HS-{str(i + 1).zfill(5)}"
        kayit_id = f"TK-{str(i + 1).zfill(5)}"
        yas      = random.randint(30, 82)

        hastalar_lst.append({
            "hasta_id":     hasta_id,
            "ad":           random.choice(isimler),
            "soyad":        random.choice(soyisimler).upper(),
            "yas":          yas,
            "cinsiyet":     random.choice(["Erkek", "Kadın"]),
            "telefon":      f"0555{str(i).zfill(7)}",
            "email":        f"hasta{i+1}@ornek.com",
            "kayit_tarihi": datetime.now(),
            "aktif":        True,
        })

        tibbi_lst.append({
            "kayit_id":             kayit_id,
            "hasta_id":             hasta_id,
            "doktor_id":            random.choice(doktor_idleri),
            "muayene_tarihi":       datetime.now(),
            "hipertansiyon":        random.choice([0, 1]),
            "kalp_hastaligi":       random.choice([0, 0, 0, 1]),
            "ortalama_seker":       round(random.uniform(60, 280), 2),
            "vucut_kitle_indeksi":  round(random.uniform(18, 50), 1),
            "sikayet":              random.choice([
                "Baş dönmesi", "Göğüs ağrısı",
                "Nefes darlığı", "Halsizlik", ""
            ]),
            "tani_notu":            "Rutin kontrol.",
            "ilac_recetesi":        [],
            "olusturma_tarihi":     datetime.now(),
        })

        yasam_tarzi_lst.append({
            "hasta_id":         hasta_id,
            "evli_mi":          random.choice(["Evet", "Hayır", "Eski"]),
            "calisma_tipi":     random.choice(["Özel Sektör", "Kamu", "Emekli"]),
            "ikamet_tipi":      random.choice(["Kentsel", "Kırsal"]),
            "sigara_durumu":    random.choice(["Hiç İçmedi", "Eski İçici", "Halen İçiyor"]),
            "guncelleme_tarihi": datetime.now(),
        })

    db.hastalar.insert_many(hastalar_lst)
    db.tibbi_bilgiler.insert_many(tibbi_lst)
    db.yasam_tarzi.insert_many(yasam_tarzi_lst)

    print(f"  ✅  {sayi} örnek hasta, tıbbi kayıt ve yaşam tarzı verisi eklendi.")


def veritabanini_hazirla(
    csv_yolu: str = "data/processed/temizlenmis_hasta_verisi.csv"
):
    """
    Veritabanını sıfırdan kurar ve örnek verilerle doldurur.
    Çalıştırma sırası: şema → doktorlar → hastalar → özet
    """
    print("\n" + "═" * 55)
    print("  VERİTABANI HAZIRLANMAYA BAŞLIYOR")
    print("═" * 55)

    db = baglanti_olustur()
    if db is None:
        print("❌ Veritabanına bağlanılamadı. MongoDB çalışıyor mu?")
        return False

    # 1. Şema ve indeksler
    print("\n[0/4] Şema ve indeksler kontrol ediliyor...")
    sema_olustur()

    # 2. Doktorlar
    doktorlari_yukle(db)

    # 3. Hastalar (CSV varsa oradan, yoksa örnekle)
    if not hastalari_yukle_csv(db, csv_yolu):
        ornek_veri_yukle(db, sayi=50)

    # 4. Özet tablo
    print("\n" + "─" * 55)
    print("[4/4] YÜKLEME ÖZETI")
    print("─" * 55)
    koleksiyonlar = [
        "doktorlar", "hastalar",
        "tibbi_bilgiler", "yasam_tarzi", "inme_risk_tahminleri"
    ]
    for ad in koleksiyonlar:
        sayi = db[ad].count_documents({})
        print(f"  {ad:<30}  →  {sayi:>6} kayıt")
    print("─" * 55)
    print("✅ Veritabanı hazır.\n")
    return True


if __name__ == "__main__":
    veritabanini_hazirla()