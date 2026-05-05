"""
Modül Adı: Database Unit Tests
Açıklama: Veritabanı bağlantısı, şema ve veri işlemleri için unit testler
Sorumlu: Nuh Dağ (Veritabanı)
Tarih: 2026-05-05
Version: 1.0
"""

import unittest
from datetime import datetime, timedelta
from pymongo import MongoClient
import uuid
import sys
import os

# Parent dizini path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))

from connection import baglanti_olustur, baglanti_kapat
from schema import koleksiyonlari_olustur

# ============================================================================
# UNIT TEST SINIFLARI
# ============================================================================

class TestDatabaseConnection(unittest.TestCase):
    """Veritabanı bağlantı testleri"""
    
    def setUp(self):
        """Her test başında MongoDB'ye bağlan"""
        self.db = baglanti_olustur()
    
    def tearDown(self):
        """Her test sonunda temizle"""
        if self.db is not None:
            try:
                self.db.client.close()
            except:
                pass
    
    def test_baglanti_basarili(self):
        """MongoDB bağlantısı başarılı mı?"""
        self.assertIsNotNone(self.db, "Veritabanı bağlantısı başarısız")
        self.assertEqual(self.db.name, "akilli_hasta_takip_sistemi")
        print("OK: Connection test passed")
    
    def test_veritabani_adi_dogru(self):
        """Veritabanı adı doğru mu?"""
        self.assertEqual(self.db.name, "akilli_hasta_takip_sistemi")
        print("OK: Database name test passed")
    
    def test_koleksiyonlar_var(self):
        """Gerekli koleksiyonlar var mı?"""
        gerekli_koleksiyonlar = [
            "kullanicilar",
            "hastalar",
            "tibbi_kayitlar",
            "yasam_tarzi",
            "risk_tahminleri"
        ]
        mevcut = self.db.list_collection_names()
        for koleksiyon in gerekli_koleksiyonlar:
            self.assertIn(koleksiyon, mevcut, f"{koleksiyon} koleksiyonu bulunamadı")
        print("OK: Collection presence test passed")


class TestHastaVeriIsleri(unittest.TestCase):
    """Hasta veri işlemleri testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
        if self.db is not None:
            self.db.hastalar.delete_many({})  # Testi temiz başlat
    
    def tearDown(self):
        if self.db is not None:
            self.db.hastalar.delete_many({})
            self.db.client.close()
    
    def test_hasta_ekleme(self):
        """Hasta kaydı başarıyla eklenebilir mi?"""
        test_hasta = {
            "hasta_no": "HS-0001",
            "tc_no": "12345678901",
            "ad": "Test",
            "soyad": "Hastası",
            "yas": 50,
            "cinsiyet": "Erkek"
        }
        
        sonuc = self.db.hastalar.insert_one(test_hasta)
        self.assertIsNotNone(sonuc.inserted_id, "Hasta kaydı başarısız")
        print("OK: Patient insert test passed")
    
    def test_hasta_benzersizlik(self):
        """TC numarası benzersiz mi (unique)?"""
        test_hasta = {
            "hasta_no": "HS-0001",
            "tc_no": "11111111111",
            "ad": "Birinci",
            "soyad": "Hasta",
            "yas": 50,
            "cinsiyet": "Erkek"
        }
        
        self.db.hastalar.insert_one(test_hasta)
        
        # Aynı TC ile tekrar eklemeye çalış
        with self.assertRaises(Exception):
            test_hasta["hasta_no"] = "HS-0002"
            self.db.hastalar.insert_one(test_hasta)
        
        print("OK: Uniqueness test passed")
    
    def test_hasta_arama_tc_ile(self):
        """TC numarasıyla hasta bulunabilir mi?"""
        test_hasta = {
            "hasta_no": "HS-0001",
            "tc_no": "99999999999",
            "ad": "Aranacak",
            "soyad": "Hasta",
            "yas": 45,
            "cinsiyet": "Kadın"
        }
        
        self.db.hastalar.insert_one(test_hasta)
        bulunan = self.db.hastalar.find_one({"tc_no": "99999999999"})
        
        self.assertIsNotNone(bulunan, "Hasta bulunamadı")
        self.assertEqual(bulunan["ad"], "Aranacak")
        print("OK: Patient search test passed")
    
    def test_hasta_guncelleme(self):
        """Hasta kaydı güncellenebilir mi?"""
        test_hasta = {
            "hasta_no": "HS-0001",
            "tc_no": "88888888888",
            "ad": "Eski",
            "soyad": "Ad",
            "yas": 40,
            "cinsiyet": "Erkek"
        }
        
        self.db.hastalar.insert_one(test_hasta)
        
        # Güncelle
        self.db.hastalar.update_one(
            {"tc_no": "88888888888"},
            {"$set": {"ad": "Yeni", "yas": 41}}
        )
        
        guncellenmi = self.db.hastalar.find_one({"tc_no": "88888888888"})
        self.assertEqual(guncellenmi["ad"], "Yeni")
        self.assertEqual(guncellenmi["yas"], 41)
        print("OK: Patient update test passed")
    
    def test_hasta_silme(self):
        """Hasta kaydı silinebilir mi?"""
        test_hasta = {
            "hasta_no": "HS-0001",
            "tc_no": "77777777777",
            "ad": "Silinecek",
            "soyad": "Hasta",
            "yas": 35,
            "cinsiyet": "Kadın"
        }
        
        self.db.hastalar.insert_one(test_hasta)
        self.db.hastalar.delete_one({"tc_no": "77777777777"})
        
        bulunan = self.db.hastalar.find_one({"tc_no": "77777777777"})
        self.assertIsNone(bulunan, "Hasta silinemedi")
        print("OK: Patient delete test passed")


class TestTibbiKayitlar(unittest.TestCase):
    """Tıbbi kayıt işlemleri testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
        if self.db is not None:
            self.db.tibbi_kayitlar.delete_many({})
            self.db.hastalar.delete_many({})
            
            # Test hastası oluştur
            test_hasta = {
                "hasta_no": "HS-TEST",
                "tc_no": "55555555555",
                "ad": "Test",
                "soyad": "Hastası",
                "yas": 50,
                "cinsiyet": "Erkek"
            }
            self.db.hastalar.insert_one(test_hasta)
    
    def tearDown(self):
        if self.db is not None:
            self.db.tibbi_kayitlar.delete_many({})
            self.db.hastalar.delete_many({})
            self.db.client.close()
    
    def test_tibbi_kayit_ekleme(self):
        """Tıbbi kayıt eklenebilir mi?"""
        tibbi_kayit = {
            "kayit_no": "TK-00001",
            "hasta_id": "HS-TEST",
            "doktor_id": "KL-0001",
            "kayit_tarihi": datetime.now(),
            "ziyaret_tipi": "Rutin Kontrol",
            "sikayet": "Baş ağrısı",
            "tanı": "Migrenli baş ağrısı"
        }
        
        sonuc = self.db.tibbi_kayitlar.insert_one(tibbi_kayit)
        self.assertIsNotNone(sonuc.inserted_id)
        print("OK: Medical record insert test passed")
    
    def test_tibbi_kayit_embedded_verisi(self):
        """Embedded ilaç verileri saklanabilir mi?"""
        tibbi_kayit = {
            "kayit_no": "TK-00002",
            "hasta_id": "HS-TEST",
            "doktor_id": "KL-0001",
            "kayit_tarihi": datetime.now(),
            "ziyaret_tipi": "Rutin Kontrol",
            "sikayet": "Göğüste ağrı",
            "ilaç_reçetesi": [
                {
                    "ilaç_adi": "Aspirin",
                    "doz": "100mg",
                    "sıklık": "Günde 1",
                    "süre": 30
                }
            ]
        }
        
        self.db.tibbi_kayitlar.insert_one(tibbi_kayit)
        bulunan = self.db.tibbi_kayitlar.find_one({"kayit_no": "TK-00002"})
        
        self.assertGreater(len(bulunan["ilaç_reçetesi"]), 0)
        print("OK: Embedded record test passed")


class TestRiskTahminleri(unittest.TestCase):
    """Risk tahmin işlemleri testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
        if self.db is not None:
            self.db.risk_tahminleri.delete_many({})
    
    def tearDown(self):
        if self.db is not None:
            self.db.risk_tahminleri.delete_many({})
            self.db.client.close()
    
    def test_risk_skoru_dogrulama(self):
        """Risk skoru 0-1 aralığında mı?"""
        tahmin = {
            "tahmin_no": "TP-00001",
            "hasta_id": "HS-TEST",
            "risk_skoru": 0.75,
            "risk_seviyesi": "Yüksek",
            "tahmin_tarihi": datetime.now()
        }
        
        self.db.risk_tahminleri.insert_one(tahmin)
        bulunan = self.db.risk_tahminleri.find_one({"tahmin_no": "TP-00001"})
        
        self.assertGreaterEqual(bulunan["risk_skoru"], 0)
        self.assertLessEqual(bulunan["risk_skoru"], 1)
        print("OK: Risk score validation test passed")
    
    def test_risk_seviyesi_kategorisi(self):
        """Risk seviyesi geçerli mi?"""
        geçerli_seviyeler = ["Düşük", "Orta", "Yüksek"]
        
        tahmin = {
            "tahmin_no": "TP-00002",
            "hasta_id": "HS-TEST",
            "risk_skoru": 0.5,
            "risk_seviyesi": "Orta",
            "tahmin_tarihi": datetime.now()
        }
        
        self.db.risk_tahminleri.insert_one(tahmin)
        bulunan = self.db.risk_tahminleri.find_one({"tahmin_no": "TP-00002"})
        
        self.assertIn(bulunan["risk_seviyesi"], geçerli_seviyeler)
        print("OK: Risk level category test passed")
    
    def test_yuksek_riskli_hastalar_sorgusu(self):
        """Yüksek riskli hastalar bulunabilir mi?"""
        # 3 tahmin ekle
        tahminler = [
            {"tahmin_no": "TP-01", "hasta_id": "HS-1", "risk_skoru": 0.2, "risk_seviyesi": "Düşük"},
            {"tahmin_no": "TP-02", "hasta_id": "HS-2", "risk_skoru": 0.8, "risk_seviyesi": "Yüksek"},
            {"tahmin_no": "TP-03", "hasta_id": "HS-3", "risk_skoru": 0.85, "risk_seviyesi": "Yüksek"},
        ]
        
        for tahmin in tahminler:
            tahmin["tahmin_tarihi"] = datetime.now()
            self.db.risk_tahminleri.insert_one(tahmin)
        
        # Yüksek riskli hastaları bul
        yuksek_riskli = list(self.db.risk_tahminleri.find({"risk_seviyesi": "Yüksek"}))
        
        self.assertEqual(len(yuksek_riskli), 2)
        print("OK: High-risk patient query test passed")


class TestYasamTarzi(unittest.TestCase):
    """Yaşam tarzı veri testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
        if self.db is not None:
            self.db.yasam_tarzi.delete_many({})
    
    def tearDown(self):
        if self.db is not None:
            self.db.yasam_tarzi.delete_many({})
            self.db.client.close()
    
    def test_yasam_tarzi_ekleme(self):
        """Yaşam tarzı verisi eklenebilir mi?"""
        yasam_tarzi = {
            "hasta_id": "HS-TEST",
            "sigara_durumu": "Halen İçiyor",
            "alkol_durumu": "Nadiren",
            "egzersiz_durumu": "Haftada 1-2",
            "beslenme_tipi": "Yüksek Tuz"
        }
        
        self.db.yasam_tarzi.insert_one(yasam_tarzi)
        bulunan = self.db.yasam_tarzi.find_one({"hasta_id": "HS-TEST"})
        
        self.assertIsNotNone(bulunan)
        self.assertEqual(bulunan["sigara_durumu"], "Halen İçiyor")
        print("OK: Lifestyle insert test passed")
    
    def test_sigara_kullananlari_bul(self):
        """Sigara kullananlar bulunabilir mi?"""
        yasam_tarzilari = [
            {"hasta_id": "HS-1", "sigara_durumu": "Hiç İçmedi"},
            {"hasta_id": "HS-2", "sigara_durumu": "Halen İçiyor"},
            {"hasta_id": "HS-3", "sigara_durumu": "Halen İçiyor"},
        ]
        
        self.db.yasam_tarzi.insert_many(yasam_tarzilari)
        
        sigara_kullananlar = list(self.db.yasam_tarzi.find({"sigara_durumu": "Halen İçiyor"}))
        
        self.assertEqual(len(sigara_kullananlar), 2)
        print("OK: Smoking users query test passed")


class TestIndeksler(unittest.TestCase):
    """İndeks testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
    
    def tearDown(self):
        if self.db is not None:
            self.db.client.close()
    
    def test_benzersiz_indeksler(self):
        """UNIQUE indeksler var mı?"""
        # Hastalar koleksiyonundaki indeksleri kontrol et
        indeksler = list(self.db.hastalar.list_indexes())
        unique_indeksler = [i for i in indeksler if i.get("unique", False)]
        
        self.assertGreater(len(unique_indeksler), 0, "UNIQUE indeks bulunamadı")
        print(f"OK: {len(unique_indeksler)} unique indexes found")
    
    def test_index_performance(self):
        """İndeksler performans sağlıyor mu?"""
        import time
        
        # Index yardımıyla sorgu
        başlama = time.time()
        sonuc = self.db.hastalar.find_one({"hasta_no": "HS-0001"})
        index_süresi = time.time() - başlama
        
        self.assertLess(index_süresi, 0.1, "İndeks performansı zayıf")
        print(f"OK: Index performance {index_süresi*1000:.2f}ms")


class TestDataIntegrity(unittest.TestCase):
    """Veri bütünlüğü testleri"""
    
    def setUp(self):
        self.db = baglanti_olustur()
    
    def tearDown(self):
        if self.db is not None:
            self.db.client.close()
    
    def test_tarih_alanları_gecerli(self):
        """Tarih alanları geçerli DateTime mi?"""
        hasta_no = f"HS-TARIH-{uuid.uuid4().hex[:8]}"
        tc_no = f"33333{uuid.uuid4().int % 90000 + 10000:05d}"
        # Örnek bir hasta ekle
        test_hasta = {
            "hasta_no": hasta_no,
            "tc_no": tc_no,
            "ad": "Tarih",
            "soyad": "Testi",
            "yas": 50,
            "cinsiyet": "Erkek",
            "olusturma_tarihi": datetime.now()
        }
        
        self.db.hastalar.delete_one({"hasta_no": hasta_no})
        self.db.hastalar.insert_one(test_hasta)
        bulunan = self.db.hastalar.find_one({"hasta_no": hasta_no})
        
        self.assertIsInstance(bulunan["olusturma_tarihi"], datetime)
        self.db.hastalar.delete_one({"hasta_no": hasta_no})
        print("OK: Date field validity test passed")


# ============================================================================
# TEST SUITE
# ============================================================================

def suite():
    """Tüm testleri bir suite içinde topla"""
    test_suite = unittest.TestSuite()
    
    # Sırasıyla testleri ekle
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConnection))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHastaVeriIsleri))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTibbiKayitlar))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRiskTahminleri))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestYasamTarzi))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIndeksler))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDataIntegrity))
    
    return test_suite


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MONGODB DATABASE UNIT TEST SUITE STARTING")
    print("="*80 + "\n")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"OK: Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"FAIL: {len(result.failures)}")
    print(f"ERROR: {len(result.errors)}")
    print(f"TOTAL TESTS: {result.testsRun}")
    print("="*80 + "\n")
    
    # Exit kodu
    exit(0 if result.wasSuccessful() else 1)
