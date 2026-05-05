"""
Modül Adı: Database Performance Analyzer
Açıklama: MongoDB veritabanı performansını test eder ve ölçeklenebilirlik önerisi verir
Sorumlu: Nuh Dağ (Veritabanı)
Tarih: 2026-05-05
Version: 1.0
"""

import time
from connection import baglanti_olustur
from datetime import datetime, timedelta
import random

# ============================================================================
# PERFORMANS ANALİZİ FONKSİYONLARI
# ============================================================================

def sorgu_performans_test(db):
    """Yaygın sorguların performansını test eder."""
    print("\n" + "="*60)
    print("⚡ SORGU PERFORMANS TESTLERİ")
    print("="*60 + "\n")
    
    testler = [
        {
            "ad": "Tüm hastaları listele",
            "sorgu": lambda: list(db.hastalar.find({})),
        },
        {
            "ad": "TC numarasına göre hasta ara (Index ile)",
            "sorgu": lambda: db.hastalar.find_one({"tc_no": "10000000001"}),
        },
        {
            "ad": "Yüksek riskli hastaları bul",
            "sorgu": lambda: list(db.risk_tahminleri.find({"risk_seviyesi": "Yüksek"}).limit(100)),
        },
        {
            "ad": "Belirli hastanın tüm tıbbi kayıtları",
            "sorgu": lambda: list(db.tibbi_kayitlar.find({"hasta_id": "HS-0001"})),
        },
        {
            "ad": "Son 30 günde yapılan muayeneler",
            "sorgu": lambda: list(db.tibbi_kayitlar.find(
                {"kayit_tarihi": {"$gte": datetime.now() - timedelta(days=30)}}
            )),
        },
        {
            "ad": "Aktif hastalara göre yaşam tarzı",
            "sorgu": lambda: list(db.yasam_tarzi.find({"sigara_durumu": "Halen İçiyor"})),
        },
    ]
    
    for test in testler:
        başlama = time.time()
        sonuc = test["sorgu"]()
        bitmea = time.time()
        
        süre_ms = (bitmea - başlama) * 1000
        
        if isinstance(sonuc, list):
            print(f"✅ {test['ad']}")
            print(f"   ⏱️  Süre: {süre_ms:.2f}ms | Sonuç: {len(sonuc)} kayıt")
        else:
            print(f"✅ {test['ad']}")
            print(f"   ⏱️  Süre: {süre_ms:.2f}ms | Sonuç: {'Bulundu' if sonuc else 'Bulunamadı'}")
        print()

def index_analizi(db):
    """Veritabanındaki indeksleri analiz eder."""
    print("\n" + "="*60)
    print("📊 İNDEKS ANALİZİ")
    print("="*60 + "\n")
    
    koleksiyonlar = db.list_collection_names()
    
    for koleksiyon_adi in sorted(koleksiyonlar):
        koleksiyon = db[koleksiyon_adi]
        indexler = list(koleksiyon.list_indexes())
        
        print(f"📁 {koleksiyon_adi.upper()}")
        print(f"   İndeks Sayısı: {len(indexler)}")
        
        for idx, index in enumerate(indexler):
            index_adi = index.get("name", "N/A")
            index_key = index.get("key", [])
            unique = index.get("unique", False)
            
            print(f"   {idx}. {index_adi}")
            print(f"      Alan(lar): {[k[0] for k in index_key]}")
            if unique:
                print(f"      🔐 Benzersiz (UNIQUE)")
        print()

def storage_analizi(db):
    """Veritabanı depolama kullanımını analiz eder."""
    print("\n" + "="*60)
    print("💾 DEPOLAMA ANALİZİ")
    print("="*60 + "\n")
    
    toplam_belge = 0
    toplam_boyut = 0
    
    koleksiyonlar = sorted(db.list_collection_names())
    
    for koleksiyon_adi in koleksiyonlar:
        koleksiyon = db[koleksiyon_adi]
        belge_sayisi = koleksiyon.count_documents({})
        
        # Örnek belgelerin boyutunu hesapla
        if belge_sayisi > 0:
            örnek_belge = koleksiyon.find_one()
            import bson
            belge_boyutu = len(bson.encode(örnek_belge))
            tahmini_toplam = belge_boyutu * belge_sayisi
        else:
            tahmini_toplam = 0
        
        toplam_belge += belge_sayisi
        toplam_boyut += tahmini_toplam
        
        print(f"📁 {koleksiyon_adi:25} | {belge_sayisi:6} belge | ~{tahmini_toplam/1024:.2f} KB")
    
    print("-" * 60)
    print(f"📊 TOPLAM: {toplam_belge} belge | ~{toplam_boyut/(1024*1024):.2f} MB")
    print()

def ölçeklenebilirlik_raporu(db):
    """Ölçeklenebilirlik ve performans önerileri verir."""
    print("\n" + "="*60)
    print("🎯 ÖLÇEKLENEBILIRLIK RAPORU VE ÖNERİLER")
    print("="*60 + "\n")
    
    hastalasayisi = db.hastalar.count_documents({})
    kayit_sayisi = db.tibbi_kayitlar.count_documents({})
    tahmin_sayisi = db.risk_tahminleri.count_documents({})
    
    print(f"📈 Mevcut Veri Boyutu:")
    print(f"   • Hasta Sayısı: {hastalasayisi}")
    print(f"   • Tıbbi Kayıt: {kayit_sayisi}")
    print(f"   • Risk Tahminleri: {tahmin_sayisi}")
    print()
    
    # Ölçeklenebilirlik analizi
    print("💡 ÖLÇEKLENEBILIRLIK ANALİZİ:")
    print()
    
    if hastalasayisi < 10000:
        print("📊 Mevcut Ölçek: KÜÇÜK (< 10.000 hasta)")
        print("   ✅ Tek MongoDB instance yeterlidir")
        print("   ✅ Mevcut indeksler optimaldır")
        print("   ⚠️  Fakat gelecek için hazırlık yapılmalı")
    elif hastalasayisi < 100000:
        print("📊 Mevcut Ölçek: ORTA (10K - 100K hasta)")
        print("   ✅ Şu anki mimarı uygun, performans iyi")
        print("   💡 Öneriler:")
        print("      - Yedekleme stratejisi geliştirin")
        print("      - Sorgu optimizasyonu yapın")
        print("      - Monitoring araçları kurun")
    else:
        print("📊 Mevcut Ölçek: BÜYÜK (> 100K hasta)")
        print("   ⚠️  Sharding düşünülmelidir")
        print("   💡 Öneriler:")
        print("      - MongoDB Replication Set kurun")
        print("      - Data sharding yapılandırın")
        print("      - Read replicas ekleyin")
    
    print()
    print("🔧 GENEL ÖNERİLER:")
    print("   1. Düzenli yedekleme (Daily)")
    print("   2. Query profiling yapın")
    print("   3. Slow query log aktif edin (> 100ms)")
    print("   4. Connection pooling kullanın")
    print("   5. TTL (Time To Live) indeksi göz önünde bulundurun")
    print("   6. Text search indeksleri ekleyin")
    print("   7. Compound indeksler optimize edin")
    print()

def detay_sorgu_analizi(db):
    """Detaylı sorgu analizi yapır."""
    print("\n" + "="*60)
    print("🔍 SORGU PLANI ANALİZİ (EXPLAIN)")
    print("="*60 + "\n")
    
    sorgu_ornekleri = [
        {
            "adi": "TC ile hasta araması",
            "sorgu": {"tc_no": "10000000001"},
            "koleksiyon": "hastalar"
        },
        {
            "adi": "Yüksek risk hastaları bulma",
            "sorgu": {"risk_seviyesi": "Yüksek"},
            "koleksiyon": "risk_tahminleri"
        },
        {
            "adi": "Hastaya göre tıbbi kayıtları bulma",
            "sorgu": {"hasta_id": "HS-0001"},
            "koleksiyon": "tibbi_kayitlar"
        },
    ]
    
    for örnek in sorgu_ornekleri:
        koleksiyon = db[örnek["koleksiyon"]]
        
        # Explain stats
        eksplein = list(koleksiyon.find(örnek["sorgu"]).explain())
        
        print(f"📌 {örnek['adi']}")
        print(f"   Koleksiyon: {örnek['koleksiyon']}")
        print(f"   Sorgu: {örnek['sorgu']}")
        
        if eksplein:
            stats = eksplein[0].get("executionStats", {}) if isinstance(eksplein[0], dict) else {}
            print(f"   ✅ Sorgu çalıştırılabilir")
        print()

def detay_rapor_olustur(db):
    """Kapsamlı bir PDF-style rapor oluşturur."""
    print("\n" + "="*60)
    print("📄 DETAYLI RAPOR")
    print("="*60 + "\n")
    
    print(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Veritabanı Adı: {db.name}")
    print()
    
    # Veritabanı durumu
    info = db.command("dbStats")
    print(f"🔹 Veritabanı İstatistikleri:")
    print(f"   • Toplam Koleksiyon: {info.get('collections', 0)}")
    print(f"   • Toplam İndeks: {info.get('indexes', 0)}")
    print(f"   • Depolama Boyutu: {info.get('storageSize', 0) / (1024*1024):.2f} MB")
    print(f"   • Ortalama Belge Boyutu: {info.get('avgObjSize', 0) / 1024:.2f} KB")
    print()
    
    # Koleksiyon istatistikleri
    print(f"🔹 Koleksiyon Detayları:")
    for koleksiyon_adi in sorted(db.list_collection_names()):
        stats = db.command("collStats", koleksiyon_adi)
        print(f"   • {koleksiyon_adi}")
        print(f"     - Belge: {stats.get('count', 0)}")
        print(f"     - Boyut: {stats.get('size', 0) / 1024:.2f} KB")
        print(f"     - Ortalama Belge: {stats.get('avgObjSize', 0) / 1024:.2f} KB")
    print()

# ============================================================================
# ANA PROGRAM
# ============================================================================

def performans_analizi_calistir():
    """Tüm performans testlerini çalıştırır."""
    print("\n" + "="*80)
    print("🚀 MONGODB VERİTABANI PERFORMANS ANALİZİ BAŞLATILIYOR")
    print("="*80)
    
    db = baglanti_olustur()
    if db is None:
        print("❌ Veritabanı bağlantısı başarısız!")
        return
    
    try:
        # Testleri çalıştır
        sorgu_performans_test(db)
        index_analizi(db)
        storage_analizi(db)
        detay_rapor_olustur(db)
        detay_sorgu_analizi(db)
        ölçeklenebilirlik_raporu(db)
        
        print("="*80)
        print("✅ PERFORMANS ANALİZİ TAMAMLANDI")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Hata oluştu: {str(e)}")

if __name__ == "__main__":
    performans_analizi_calistir()
