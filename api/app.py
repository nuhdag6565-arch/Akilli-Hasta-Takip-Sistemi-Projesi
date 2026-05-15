"""
Modül Adı: app.py
Açıklama : Flask REST API — tüm veri erişimi database/ modülleri
           üzerinden yapılır; ham MongoDB çağrısı yoktur.
Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-05-15
Version  : 3.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

from model.predict            import hasta_risk_tahmini
from database.doktor_isimleri import (
    doktor_giris, doktor_kayit,
    doktorlari_listele, doktor_profil_getir,
)
from database.hasta_isimleri  import (
    hasta_ekle, hastalari_listele, hasta_getir, hasta_ara,
)
from database.risk_islemleri  import (
    hasta_risk_gecmisi, risk_istatistikleri,
)
from database.connection import baglanti_olustur

app = Flask(__name__)
CORS(app)

db = baglanti_olustur()
if db is None:
    print("❌ HATA: Veritabanına bağlanılamadı!")
else:
    print("✅ Veritabanı bağlantısı başarılı")


# ── Yardımcı: datetime → ISO string ────────────────────────────
def _ser(obj):
    if isinstance(obj, dict):
        return {k: _ser(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ser(i) for i in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


# ════════════════════════════════════════════════════════════════
# HASTA ENDPOINT'LERİ
# ════════════════════════════════════════════════════════════════

@app.route("/api/hastalar", methods=["GET"])
def hastalar_getir():
    """Tüm hastaları listeler. ?limit=N ile sınırlandırılabilir."""
    limit = int(request.args.get("limit", 100))
    hastalar = hastalari_listele(limit=limit)
    return jsonify({"hastalar": _ser(hastalar), "durum": "basarili"}), 200


@app.route("/api/hastalar", methods=["POST"])
def hasta_ekle_endpoint():
    """Yeni hasta kaydı açar."""
    data  = request.json or {}
    sonuc = hasta_ekle(
        ad       = data.get("ad", ""),
        soyad    = data.get("soyad", ""),
        yas      = int(data.get("yas", 0)),
        cinsiyet = data.get("cinsiyet", ""),
        telefon  = data.get("telefon", ""),
        email    = data.get("email", ""),
    )
    if sonuc["basarili"]:
        return jsonify({**sonuc, "durum": "basarili"}), 201
    return jsonify({"hata": sonuc["mesaj"], "durum": "hata"}), 400


@app.route("/api/hastalar/ara", methods=["GET"])
def hasta_ara_endpoint():
    """?ad=... ve/veya ?soyad=... ile hasta arar."""
    ad    = request.args.get("ad", "")
    soyad = request.args.get("soyad", "")
    sonuclar = hasta_ara(ad=ad, soyad=soyad)
    return jsonify({"hastalar": _ser(sonuclar), "durum": "basarili"}), 200


@app.route("/api/hastalar/<hasta_id>", methods=["GET"])
def hasta_getir_endpoint(hasta_id):
    """HS-XXXXX formatındaki ID ile tek hastayı getirir."""
    hasta = hasta_getir(hasta_id)
    if hasta is None:
        return jsonify({"hata": "Hasta bulunamadı", "durum": "hata"}), 404
    return jsonify({"hasta": _ser(hasta), "durum": "basarili"}), 200


@app.route("/api/hastalar/<hasta_id>/risk-gecmisi", methods=["GET"])
def risk_gecmisi_endpoint(hasta_id):
    """Hastanın geçmiş risk tahminlerini döndürür."""
    limit  = int(request.args.get("limit", 10))
    gecmis = hasta_risk_gecmisi(hasta_id, limit=limit)
    return jsonify({"gecmis": _ser(gecmis), "durum": "basarili"}), 200


# ════════════════════════════════════════════════════════════════
# DOKTOR ENDPOINT'LERİ
# ════════════════════════════════════════════════════════════════

@app.route("/api/doktorlar", methods=["GET"])
def doktorlar_getir():
    """Tüm aktif doktorları listeler (şifre hariç)."""
    doktorlar = doktorlari_listele()
    return jsonify({"doktorlar": _ser(doktorlar), "durum": "basarili"}), 200


@app.route("/api/doktorlar/login", methods=["POST"])
def doktor_login():
    """
    Doktor girişi — TC ve şifre ile.
    Body: { "tc_no": "...", "password": "..." }
    """
    data     = request.json or {}
    tc       = data.get("tc_no", data.get("tc", "")).strip()
    password = data.get("password", "").strip()

    if not tc or not password:
        return jsonify({"hata": "TC ve şifre gerekli", "durum": "hata"}), 400

    sonuc = doktor_giris(tc_no=tc, sifre=password)
    if sonuc["basarili"]:
        return jsonify({"doktor": _ser(sonuc["doktor"]), "durum": "basarili"}), 200

    mesaj = sonuc["mesaj"]
    kod   = 401 if "Şifre" in mesaj else 404
    return jsonify({"hata": mesaj, "durum": "hata"}), kod


@app.route("/api/doktorlar", methods=["POST"])
def doktor_ekle_endpoint():
    """
    Yeni doktor kaydı açar.
    Body: { "tc_no", "ad", "soyad", "uzmanlik", "password",
            "guvenlik_cevabi" (opsiyonel) }
    """
    data = request.json or {}
    tc   = data.get("tc_no",    data.get("tc",       "")).strip()
    ad   = data.get("ad",       data.get("name",     "")).strip()
    soy  = data.get("soyad",    data.get("surname",  "")).strip()
    uzm  = data.get("uzmanlik", data.get("specialty","")).strip()
    pw   = data.get("password", "")
    guv  = data.get("guvenlik_cevabi", "—").strip() or "—"

    sonuc = doktor_kayit(
        tc_no           = tc,
        ad              = ad,
        soyad           = soy,
        uzmanlik        = uzm,
        sifre           = pw,
        sifre_tekrar    = pw,
        guvenlik_cevabi = guv,
    )

    if sonuc["basarili"]:
        return jsonify({
            "doktor_id": sonuc["doktor_id"],
            "mesaj":     sonuc["mesaj"],
            "durum":     "basarili",
        }), 201

    mesaj = sonuc["mesaj"]
    kod   = 409 if ("kayıt edilmiş" in mesaj or "daha önce" in mesaj) else 400
    return jsonify({"hata": mesaj, "durum": "hata"}), kod


@app.route("/api/doktorlar/<tc_no>/profil", methods=["GET"])
def doktor_profil_endpoint(tc_no):
    """TC numarasıyla doktor profil bilgilerini getirir."""
    profil = doktor_profil_getir(tc_no)
    if not profil:
        return jsonify({"hata": "Doktor bulunamadı", "durum": "hata"}), 404
    return jsonify({"doktor": _ser(profil), "durum": "basarili"}), 200


# ════════════════════════════════════════════════════════════════
# RİSK TAHMİNİ ENDPOINT'İ
# ════════════════════════════════════════════════════════════════

@app.route("/api/risk-tahmini", methods=["POST"])
def risk_tahmini():
    """
    İnme riski tahmini yapar ve sonucu veritabanına kaydeder.

    Request Body:
        {
            "hasta_id"          : "HS-00001",   (opsiyonel)
            "yas"               : 55,
            "cinsiyet"          : "Erkek",
            "hipertansiyon"     : 1,
            "kalp_hastaligi"    : 0,
            "evli_mi"           : "Evet",
            "calisma_tipi"      : "Çalışan",
            "ikamet_tipi"       : "Kentsel",
            "ortalama_seker"    : 140,
            "vucut_kitle_indeksi": 28.5,
            "sigara_durumu"     : "Halen İçiyor"
        }
    """
    if db is None:
        return jsonify({"hata": "Veritabanı bağlantısı başarısız", "durum": "hata"}), 500

    try:
        data = request.json
        if not data:
            return jsonify({"hata": "İstek gövdesi boş olamaz.", "durum": "hata"}), 400

        sonuc = hasta_risk_tahmini(data)
        if not sonuc["basarili"]:
            return jsonify({"hata": sonuc["mesaj"], "durum": "hata"}), 400

        tahmin_tarihi = datetime.now().isoformat()
        tahmin_record = {
            "hasta_id":     data.get("hasta_id"),
            "risk_skoru":   sonuc["risk_skoru"],
            "risk_yuzdesi": sonuc["risk_yuzdesi"],
            "risk_seviyesi":sonuc["risk_seviyesi"],
            "oneri":        sonuc["oneri"],
            "tahmin_tarihi":tahmin_tarihi,
            "input_data":   data,
        }
        db["inme_risk_tahminleri"].insert_one(tahmin_record)

        return jsonify({
            "risk_skoru"            : sonuc["risk_skoru"],
            "risk_yuzdesi"          : sonuc["risk_yuzdesi"],
            "risk_seviyesi"         : sonuc["risk_seviyesi"],
            "oneri"                 : sonuc["oneri"],
            "doktor_onerileri"      : sonuc.get("doktor_onerileri",      []),
            "yasam_tarzi_onerileri" : sonuc.get("yasam_tarzi_onerileri", []),
            "izleme_onerileri"      : sonuc.get("izleme_onerileri",      []),
            "aciliyet"              : sonuc.get("aciliyet",              ""),
            "tahmin_tarihi"         : tahmin_tarihi,
            "durum"                 : "basarili",
        }), 200

    except Exception as e:
        return jsonify({"hata": f"Sunucu hatası: {str(e)}", "durum": "hata"}), 500


# ════════════════════════════════════════════════════════════════
# İSTATİSTİK ENDPOINT'İ
# ════════════════════════════════════════════════════════════════

@app.route("/api/istatistikler", methods=["GET"])
def istatistikler():
    """Risk tahminlerinin özet istatistiklerini döndürür."""
    stats = risk_istatistikleri()
    return jsonify({"istatistikler": _ser(stats), "durum": "basarili"}), 200


# ════════════════════════════════════════════════════════════════
# ÇALIŞTIRMA
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)
