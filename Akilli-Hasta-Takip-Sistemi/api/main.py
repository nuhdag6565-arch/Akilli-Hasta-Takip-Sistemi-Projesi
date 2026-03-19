from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI()

# modeli yükle
model = joblib.load("models/stroke_model.pkl")

@app.get("/")
def home():
    return {"message": "Akıllı Hasta Takip Sistemi API"}

@app.get("/veri")
def veri():
    df = pd.read_csv("data/temizlenmis_hasta_verisi.csv")
    return {"satir_sayisi": len(df)}

@app.post("/predict")
def predict(yas: int, bmi: float, seker: float):

    data = [[yas, bmi, seker]]

    pred = model.predict(data)

    return {"inme_riski": int(pred[0])}