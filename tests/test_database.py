"""
Modül Adı: test_database.py
Açıklama : Veritabanı modüllerinin birim testleri.
           Her değişiklikten sonra çalıştırılmalıdır.
Sorumlu  : Nuh Dağ (Veritabanı)
Tarih    : 2026-05-08
Version  : 3.0
"""

import sys, os, unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.connection       import baglanti_olustur, baglanti_kapat
from database.hasta_islemleri  import (
    hasta_ekle, tibbi_bilgi_ekle, yasam_tarzi_guncelle,
    hasta_getir, hasta_ara, muayene_gecmisi, hasta_guncelle,
)
from database.risk_islemleri   import (
    risk_sonucu_kaydet, hasta_risk_gecmisi, risk_istatistikleri,
)
from database.doktor_islemleri import doktor_ekle, doktor_giris


# ════════════════════════════════════════════════════════════════
# YARDIMCI: Her testte temiz bir başlangıç
# ════════════════════════════════════════════════════════════════

def temizle(db, *koleksiyonlar):
    for k in koleksiyonlar:
        db[k].delete_many({})


# ════════════════════════════════════════════════════════════════
# TEST SINIFLARI
# ════════════════════════════════════════════════════════════════

class T01_Baglanti(unittest.TestCase):
    """MongoDB bağlantı testleri"""

    def test_01_baglanti_kuruluyor(self):
        db = baglanti_olustur()
        self.assertIsNotNone(db, "Bağlantı başarısız")
        self.assertEqual(db.name, "inme_risk_sistemi")

    def test_02_koleksiyonlar_var(self):
        db = baglanti_olustur()
        mevcut = db.list_collection_names()
        for k in ["hastalar", "tibbi_bilgiler",
                  "yasam_tarzi", "inme_risk_tahminleri", "doktorlar"]:
            self.assertIn(k, mevcut, f"'{k}' koleksiyonu eksik")


class T02_HastaEkleme(unittest.TestCase):
    """Hasta CRUD testleri"""

    def setUp(self):
        self.db = baglanti_olustur()
        temizle(self.db, "hastalar", "tibbi_bilgiler",
                "yasam_tarzi", "inme_risk_tahminleri")

    # ── Başarılı ekleme ────────────────────────────────────────
    def test_01_hasta_eklenir(self):
        r = hasta_ekle("Ali", "Veli", 55, "Erkek", "05551111111")
        self.assertTrue(r["basarili"])
        self.assertIn("HS-", r["hasta_id"])

    # ── Zorunlu alan eksik ─────────────────────────────────────
    def test_02_ad_bos_hata(self):
        r = hasta_ekle("", "Veli", 55, "Erkek")
        self.assertFalse(r["basarili"])

    def test_03_gecersiz_yas(self):
        r = hasta_ekle("Ali", "Veli", 200, "Erkek")
        self.assertFalse(r["basarili"])

    def test_04_gecersiz_cinsiyet(self):
        r = hasta_ekle("Ali", "Veli", 55, "Bilinmiyor")
        self.assertFalse(r["basarili"])

    # ── Getir ve ara ───────────────────────────────────────────
    def test_05_hasta_getirilir(self):
        r    = hasta_ekle("Zeynep", "Arslan", 42, "Kadın")
        hata = hasta_getir(r["hasta_id"])
        self.assertIsNotNone(hata)
        self.assertEqual(hata["ad"], "Zeynep")

    def test_06_isme_gore_arama(self):
        hasta_ekle("Mehmet", "Yıldız", 60, "Erkek")
        sonuc = hasta_ara(ad="Mehmet")
        self.assertGreater(len(sonuc), 0)

    # ── Güncelleme ─────────────────────────────────────────────
    def test_07_hasta_guncellenir(self):
        r    = hasta_ekle("Hasan", "Çelik", 50, "Erkek")
        hid  = r["hasta_id"]
        sonuc = hasta_guncelle(hid, {"telefon": "05559999999"})
        self.assertTrue(sonuc["basarili"])
        h = hasta_getir(hid)
        self.assertEqual(h["telefon"], "05559999999")


class T03_TibbiKayit(unittest.TestCase):
    """Tıbbi bilgi kayıt testleri"""

    def setUp(self):
        self.db = baglanti_olustur()
        temizle(self.db, "hastalar", "tibbi_bilgiler", "yasam_tarzi")
        r = hasta_ekle("Test", "Hasta", 65, "Erkek")
        self.hasta_id = r["hasta_id"]

    def test_01_tibbi_bilgi_kaydedilir(self):
        r = tibbi_bilgi_ekle(
            hasta_id            = self.hasta_id,
            doktor_id           = "DR-00001",
            hipertansiyon       = 1,
            kalp_hastaligi      = 0,
            ortalama_seker      = 145.0,
            vucut_kitle_indeksi = 28.5,
            sikayet             = "Baş dönmesi",
        )
        self.assertTrue(r["basarili"])
        self.assertIn("TK-", r["kayit_id"])

    def test_02_gecersiz_hasta_hata(self):
        r = tibbi_bilgi_ekle(
            hasta_id="HS-OLMAYAN", doktor_id="DR-00001",
            hipertansiyon=0, kalp_hastaligi=0,
            ortalama_seker=100, vucut_kitle_indeksi=25
        )
        self.assertFalse(r["basarili"])

    def test_03_muayene_gecmisi_getirilir(self):
        tibbi_bilgi_ekle(
            hasta_id=self.hasta_id, doktor_id="DR-00001",
            hipertansiyon=0, kalp_hastaligi=0,
            ortalama_seker=110, vucut_kitle_indeksi=24
        )
        kayitlar = muayene_gecmisi(self.hasta_id)
        self.assertGreater(len(kayitlar), 0)


class T04_YasamTarzi(unittest.TestCase):
    """Yaşam tarzı testleri"""

    def setUp(self):
        self.db = baglanti_olustur()
        temizle(self.db, "hastalar", "yasam_tarzi")
        r = hasta_ekle("Yaşam", "Tarzi", 50, "Kadın")
        self.hasta_id = r["hasta_id"]

    def test_01_yasam_tarzi_kaydedilir(self):
        r = yasam_tarzi_guncelle(
            hasta_id      = self.hasta_id,
            evli_mi       = "Evet",
            calisma_tipi  = "Kamu",
            ikamet_tipi   = "Kentsel",
            sigara_durumu = "Hiç İçmedi",
        )
        self.assertTrue(r["basarili"])

    def test_02_gecersiz_sigara_hata(self):
        r = yasam_tarzi_guncelle(
            hasta_id=self.hasta_id, sigara_durumu="Bazen İçiyor"
        )
        self.assertFalse(r["basarili"])

    def test_03_upsert_calisiyor(self):
        # İki kez çağrılınca kayıt 2 olmamalı, güncellenmeli
        yasam_tarzi_guncelle(self.hasta_id, sigara_durumu="Halen İçiyor")
        yasam_tarzi_guncelle(self.hasta_id, sigara_durumu="Eski İçici")
        sayi = self.db.yasam_tarzi.count_documents({"hasta_id": self.hasta_id})
        self.assertEqual(sayi, 1, "Upsert çalışmıyor, 2 kayıt oluştu")


class T05_RiskTahmini(unittest.TestCase):
    """Risk tahmini kayıt testleri"""

    def setUp(self):
        self.db = baglanti_olustur()
        temizle(self.db, "hastalar", "tibbi_bilgiler",
                "yasam_tarzi", "inme_risk_tahminleri")
        r = hasta_ekle("Risk", "Test", 70, "Erkek")
        self.hasta_id = r["hasta_id"]

    def test_01_risk_kaydedilir(self):
        r = risk_sonucu_kaydet(
            hasta_id        = self.hasta_id,
            doktor_id       = "DR-00001",
            risk_skoru      = 0.75,
            model_girdileri = {"yas": 70, "hipertansiyon": 1},
        )
        self.assertTrue(r["basarili"])
        self.assertEqual(r["risk_seviyesi"], "Yüksek")
        self.assertEqual(r["risk_yuzdesi"],  75.0)
        self.assertGreater(len(r["oneriler"]), 0)

    def test_02_dusuk_risk(self):
        r = risk_sonucu_kaydet(
            hasta_id=self.hasta_id, doktor_id="DR-00001",
            risk_skoru=0.15, model_girdileri={}
        )
        self.assertEqual(r["risk_seviyesi"], "Düşük")

    def test_03_orta_risk(self):
        r = risk_sonucu_kaydet(
            hasta_id=self.hasta_id, doktor_id="DR-00001",
            risk_skoru=0.50, model_girdileri={}
        )
        self.assertEqual(r["risk_seviyesi"], "Orta")

    def test_04_gecersiz_skor_hata(self):
        r = risk_sonucu_kaydet(
            hasta_id=self.hasta_id, doktor_id="DR-00001",
            risk_skoru=1.5, model_girdileri={}
        )
        self.assertFalse(r["basarili"])

    def test_05_risk_gecmisi_getirilir(self):
        risk_sonucu_kaydet(
            hasta_id=self.hasta_id, doktor_id="DR-00001",
            risk_skoru=0.8, model_girdileri={}
        )
        gecmis = hasta_risk_gecmisi(self.hasta_id)
        self.assertGreater(len(gecmis), 0)


class T06_Doktor(unittest.TestCase):
    """Doktor hesap testleri"""

    def setUp(self):
        self.db = baglanti_olustur()
        temizle(self.db, "doktorlar")

    def test_01_doktor_eklenir(self):
        r = doktor_ekle(
            "Deneme", "Doktor", "Nöroloji",
            "deneme@test.com", "sifre123"
        )
        self.assertTrue(r["basarili"])

    def test_02_ayni_email_hata(self):
        doktor_ekle("A", "B", "Nöroloji", "ayni@test.com", "123")
        r = doktor_ekle("C", "D", "Kardiyoloji", "ayni@test.com", "456")
        self.assertFalse(r["basarili"])

    def test_03_giris_basarili(self):
        doktor_ekle("Giris", "Test", "Nöroloji", "giris@test.com", "sifre")
        d = doktor_giris("giris@test.com", "sifre")
        self.assertIsNotNone(d)
        self.assertNotIn("sifre_hash", d)

    def test_04_yanlis_sifre(self):
        doktor_ekle("Yanlis", "Sifre", "Nöroloji", "yanlis@test.com", "dogru")
        d = doktor_giris("yanlis@test.com", "yanlis")
        self.assertIsNone(d)


# ════════════════════════════════════════════════════════════════
# TEST RUNNER
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "═" * 60)
    print("  İNME RİSK SİSTEMİ  –  VERİTABANI BİRİM TESTLERİ")
    print("═" * 60 + "\n")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    for sinif in [T01_Baglanti, T02_HastaEkleme, T03_TibbiKayit,
                  T04_YasamTarzi, T05_RiskTahmini, T06_Doktor]:
        suite.addTests(loader.loadTestsFromTestCase(sinif))

    runner = unittest.TextTestRunner(verbosity=2)
    sonuc  = runner.run(suite)

    gecen  = sonuc.testsRun - len(sonuc.failures) - len(sonuc.errors)
    print("\n" + "═" * 60)
    print(f"  ✅  Geçen   : {gecen}")
    print(f"  ❌  Başarısız: {len(sonuc.failures)}")
    print(f"  ⚠️   Hata    : {len(sonuc.errors)}")
    print(f"  📊  Toplam  : {sonuc.testsRun}")
    print("═" * 60 + "\n")

    sys.exit(0 if sonuc.wasSuccessful() else 1)