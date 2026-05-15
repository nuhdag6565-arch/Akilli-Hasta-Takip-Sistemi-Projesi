"""
Modül Adı: app.py
Açıklama : Flask REST API — Hasta, Doktor ve Risk Tahmini endpoint'leri.
           Risk tahmini endpoint'i artık gerçek Random Forest modeline bağlı.
Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-05-11
Version  : 2.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from model.predict import hasta_risk_tahmini
from database.connection import baglanti_olustur
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Cross-Origin Resource Sharing aktivleştir

# ── MongoDB Veritabanı Bağlantısı ──
db = baglanti_olustur()
if db is None:
    print("❌ HATA: Veritabanına bağlanılamadı!")
else:
    print("✅ Veritabanı bağlantısı başarılı")


# ════════════════════════════════════════════════════════════════
# HASTA ENDPOINT'LERİ
# ════════════════════════════════════════════════════════════════

@app.route("/api/hastalar", methods=["GET"])
def hastalari_getir():
    """Tüm hastaları listeler."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        hastalar = list(db['hastalar'].find())
        for hasta in hastalar:
            hasta['_id'] = str(hasta['_id'])
        return jsonify({"hastalar": hastalar, "durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


@app.route("/api/hastalar", methods=["POST"])
def hasta_ekle():
    """Yeni hasta ekler."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        data = request.json
        
        if not data.get('tc'):
            return jsonify({"hata": "TC gerekli", "durum": "hata"}), 400
        
        # Aynı TC ile hasta var mı?
        if db['hastalar'].find_one({"tc": data['tc']}):
            return jsonify({"hata": "Bu TC ile hasta zaten kayıtlı", "durum": "hata"}), 409
        
        yeni_hasta = {
            "tc": data.get('tc', ''),
            "name": data.get('name', ''),
            "surname": data.get('surname', ''),
            "age": data.get('age', 0),
            "gender": data.get('gender', ''),
            "phone": data.get('phone', ''),
            "email": data.get('email', ''),
            "address": data.get('address', ''),
            "medical_history": data.get('medical_history', {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        sonuc = db['hastalar'].insert_one(yeni_hasta)
        yeni_hasta['_id'] = str(sonuc.inserted_id)
        
        return jsonify({"hasta": yeni_hasta, "durum": "basarili"}), 201
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


@app.route("/api/hastalar/<hasta_id>", methods=["GET"])
def hasta_getir(hasta_id):
    """Belirli bir hastayı getirir."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        hasta = db['hastalar'].find_one({"_id": ObjectId(hasta_id)})
        if not hasta:
            return jsonify({"hata": "Hasta bulunamadı", "durum": "hata"}), 404
        
        hasta['_id'] = str(hasta['_id'])
        return jsonify({"hasta": hasta, "durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


# ════════════════════════════════════════════════════════════════
# DOKTOR ENDPOINT'LERİ
# ════════════════════════════════════════════════════════════════

@app.route("/api/doktorlar", methods=["GET"])
def doktorlari_getir():
    """Tüm doktorları listeler."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        doktorlar = list(db['doktorlar'].find({}, {"password": 0}))
        for doc in doktorlar:
            doc['_id'] = str(doc['_id'])
        return jsonify({"doktorlar": doktorlar, "durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


@app.route("/api/doktorlar/login", methods=["POST"])
def doktor_login():
    """Doktor girişi - TC ve şifre ile."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        data = request.json
        tc = data.get('tc', '').strip()
        password = data.get('password', '').strip()
        
        if not tc or not password:
            return jsonify({"hata": "TC ve şifre gerekli", "durum": "hata"}), 400
        
        doktor = db['doktorlar'].find_one({"tc": tc})
        
        if not doktor:
            return jsonify({"hata": "Doktor bulunamadı", "durum": "hata"}), 404
        
        if doktor.get('password') != password:
            return jsonify({"hata": "Şifre hatalı", "durum": "hata"}), 401
        
        # Son giriş zamanını güncelle
        db['doktorlar'].update_one(
            {"_id": doktor['_id']},
            {"$set": {"last_login": datetime.now().isoformat()}}
        )
        
        doktor['_id'] = str(doktor['_id'])
        doktor.pop('password', None)
        
        return jsonify({"doktor": doktor, "durum": "basarili"}), 200
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


@app.route("/api/doktorlar", methods=["POST"])
def doktor_ekle():
    """Yeni doktor ekler."""
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        data = request.json
        
        # Gerekli alanlar kontrol
        if not data.get('tc') or not data.get('password') or not data.get('name'):
            return jsonify({"hata": "TC, ad ve şifre gerekli", "durum": "hata"}), 400
        
        # Aynı TC ile doktor var mı?
        if db['doktorlar'].find_one({"tc": data['tc']}):
            return jsonify({"hata": "Bu TC ile doktor zaten kayıtlı", "durum": "hata"}), 409
        
        yeni_doktor = {
            "tc": data['tc'],
            "name": data.get('name', ''),
            "surname": data.get('surname', ''),
            "email": data.get('email', ''),
            "password": data['password'],
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        sonuc = db['doktorlar'].insert_one(yeni_doktor)
        yeni_doktor['_id'] = str(sonuc.inserted_id)
        yeni_doktor.pop('password', None)
        
        return jsonify({"doktor": yeni_doktor, "durum": "basarili"}), 201
    except Exception as e:
        return jsonify({"hata": str(e), "durum": "hata"}), 500


# ════════════════════════════════════════════════════════════════
# RİSK TAHMİNİ ENDPOINT'İ — Gerçek Model Entegrasyonu
# ════════════════════════════════════════════════════════════════

@app.route("/api/risk-tahmini", methods=["POST"])
def risk_tahmini():
    """
    İnme riski tahmini yapar ve sonucu veritabanına kaydeder.

    Request Body:
        {
            "hasta_id": "...",
            "yas": 55,
            "cinsiyet": "Erkek",
            "hipertansiyon": 1,
            "kalp_hastaligi": 0,
            "evli_mi": "Evet",
            "calisma_tipi": "Çalışan",
            "ikamet_tipi": "Kentsel",
            "ortalama_seker": 140,
            "vucut_kitle_indeksi": 28.5,
            "sigara_durumu": "Halen İçiyor"
        }
    """
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500
    
    try:
        data = request.json

        if not data:
            return jsonify({
                "hata": "İstek gövdesi (JSON) boş olamaz.",
                "durum": "hata"
            }), 400

        sonuc = hasta_risk_tahmini(data)

        if not sonuc["basarili"]:
            return jsonify({
                "hata": sonuc["mesaj"],
                "durum": "hata"
            }), 400

        # Sonucu veritabanına kaydet
        tahmin_record = {
            "hasta_id": data.get('hasta_id'),
            "risk_skoru": sonuc["risk_skoru"],
            "risk_yuzdesi": sonuc["risk_yuzdesi"],
            "risk_seviyesi": sonuc["risk_seviyesi"],
            "oneri": sonuc["oneri"],
            "tahmin_tarihi": datetime.now().isoformat(),
            "input_data": data
        }
        
        db['risk_tahminleri'].insert_one(tahmin_record)

        return jsonify({
            "risk_skoru"            : sonuc["risk_skoru"],
            "risk_yuzdesi"          : sonuc["risk_yuzdesi"],
            "risk_seviyesi"         : sonuc["risk_seviyesi"],
            "oneri"                 : sonuc["oneri"],
            "doktor_onerileri"      : sonuc.get("doktor_onerileri", []),
            "yasam_tarzi_onerileri" : sonuc.get("yasam_tarzi_onerileri", []),
            "izleme_onerileri"      : sonuc.get("izleme_onerileri", []),
            "aciliyet"              : sonuc.get("aciliyet", ""),
            "tahmin_tarihi"         : tahmin_record["tahmin_tarihi"],
            "durum"                 : "basarili"
        }), 200

    except Exception as e:
        return jsonify({
            "hata": f"Sunucu hatası: {str(e)}",
            "durum": "hata"
        }), 500


# ════════════════════════════════════════════════════════════════
# ÇALIŞTIRMA
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)