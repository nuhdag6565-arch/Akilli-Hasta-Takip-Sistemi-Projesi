from flask import Flask, jsonify, request

app = Flask(__name__)

# --- HASTA ---
@app.route('/api/hastalar', methods=['GET'])
def hastalari_getir():
    return jsonify({"mesaj": "Tüm hastalar listelendi"})

@app.route('/api/hastalar', methods=['POST'])
def hasta_ekle():
    data = request.json
    return jsonify({"mesaj": "Hasta eklendi", "data": data}), 201

@app.route('/api/hastalar/<hasta_id>', methods=['GET'])
def hasta_getir(hasta_id):
    return jsonify({"mesaj": f"{hasta_id} numaralı hasta"})

# --- DOKTOR ---
@app.route('/api/doktorlar', methods=['GET'])
def doktorlari_getir():
    return jsonify({"mesaj": "Tüm doktorlar listelendi"})

@app.route('/api/doktorlar', methods=['POST'])
def doktor_ekle():
    data = request.json
    return jsonify({"mesaj": "Doktor eklendi", "data": data}), 201

# --- RİSK TAHMİNİ ---
@app.route('/api/risk-tahmini', methods=['POST'])
def risk_tahmini():
    data = request.json
    return jsonify({
        "risk_skoru": 0.75,
        "risk_seviyesi": "Yüksek",
        "oneri": "Doktora başvurun"
    })

if __name__ == '__main__':
    app.run(debug=True)
