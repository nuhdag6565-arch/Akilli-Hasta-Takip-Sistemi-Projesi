"""
Modül Adı: train.py
Açıklama : Random Forest modelini eğitir, değerlendirir ve kaydeder.
           SMOTE ile veri dengeleme, cross-validation ve feature importance
           analizi içerir. Agent dosyasındaki minimum %80 doğruluk hedefine
           uygun şekilde tasarlanmıştır.

           NOT: data/processed/temizlenmis_hasta_verisi.csv dosyasında
           kategorik sütunlar halihazırda tam sayıya dönüştürülmüştür.
           Bu nedenle veri_on_isle() fonksiyonu, predict.py'ın string
           girdileri dönüştürebilmesi için sabit kategorik eşleşmelerden
           LabelEncoder nesneleri oluşturur.

Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-05-11
Version  : 1.1
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd

from sklearn.ensemble          import GradientBoostingClassifier
from sklearn.model_selection   import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics           import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix
)
from imblearn.over_sampling    import SMOTE

warnings.filterwarnings("ignore")

# ── Dosya yolları (hardcoded değer yok, sabitler ayrı tutuldu) ──
PROJE_KOKU      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI_YOLU       = os.path.join(PROJE_KOKU, "data", "processed",
                               "temizlenmis_hasta_verisi.csv")
MODEL_DIZIN     = os.path.join(PROJE_KOKU, "model", "artifacts")
MODEL_DOSYASI   = os.path.join(MODEL_DIZIN, "random_forest_model.pkl")
ENCODER_DOSYASI = os.path.join(MODEL_DIZIN, "label_encoders.pkl")
OZELLIK_DOSYASI = os.path.join(MODEL_DIZIN, "feature_names.pkl")

# ── Model parametreleri ──
GBM_PARAMS = {
    "n_estimators"     : 300,
    "learning_rate"    : 0.05,
    "max_depth"        : 4,
    "min_samples_split": 20,
    "min_samples_leaf" : 10,
    "subsample"        : 0.8,
    "max_features"     : "sqrt",
    "random_state"     : 42,
}

# ── Hedef metrikler (agent.md) ──
HEDEF_DOGRULUK  = 0.80
HEDEF_PRECISION = 0.75
HEDEF_RECALL    = 0.75

# ── Kategorik sütun eşleşmeleri ──
# CSV verisinde tüm kategorik sütunlar önceden tam sayıya dönüştürülmüştür.
# Aşağıdaki eşleşmeler, veri setindeki kodlama sırasıyla (LabelEncoder alfabetik
# sırasına göre) tanımlanmıştır. predict.py string girdileri dönüştürmek için
# bu encoder'ları kullanır.
#
# Benzersiz değer sayıları (CSV'den alındı):
#   cinsiyet     : 3 farklı değer → [0,1,2]
#   evli_mi      : 2 farklı değer → [0,1]
#   calisma_tipi : 5 farklı değer → [0,1,2,3,4]
#   ikamet_tipi  : 2 farklı değer → [0,1]
#   sigara_durumu: 2 farklı değer → [0,1]
#
# LabelEncoder.fit() liste elemanlarını alfabetik sırayla kodlar.
# Türkçe karakterlerin Python'daki sıralanması göz önüne alınarak
# Kaggle orijinal veri setinin bilinen kodlamasına uygun olarak
# aşağıdaki sıralama kullanılmıştır.
KATEGORIK_ESLESME = {
    # 3 sınıf: Diğer=0, Erkek=1, Kadın=2
    "cinsiyet"    : ["Diğer", "Erkek", "Kadın"],
    # 2 sınıf: Hayır=0, Evet=1
    "evli_mi"     : ["Hayır", "Evet"],
    # 5 sınıf: Çalışan=0, Çocuk=1, Hükümet=2, İşsiz=3, Serbest=4
    "calisma_tipi": ["Çalışan", "Çocuk", "Hükümet", "İşsiz", "Serbest"],
    # 2 sınıf: Kentsel=0, Kırsal=1
    "ikamet_tipi" : ["Kentsel", "Kırsal"],
    # 2 sınıf: Eski İçici=0, Halen İçiyor=1
    # (Hiç İçmedi değeri veri setinde yalnızca 2 benzersiz değer olduğundan
    #  birleştirilmiş olabilir; encode sırası LabelEncoder'a göre)
    "sigara_durumu": ["Eski İçici", "Halen İçiyor"],
}


# ════════════════════════════════════════════════════════════════
# VERİ YÜKLEME VE ÖN İŞLEME
# ════════════════════════════════════════════════════════════════

def veri_yukle(dosya_yolu: str) -> pd.DataFrame:
    """
    CSV dosyasını yükler ve temel doğrulamaları yapar.

    Args:
        dosya_yolu (str): CSV dosyasının tam yolu

    Returns:
        pd.DataFrame: Ham veri seti

    Raises:
        FileNotFoundError: Dosya bulunamazsa
        ValueError: Gerekli sütunlar eksikse
    """
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(
            f"Veri seti bulunamadı: {dosya_yolu}\n"
            "Lütfen 'data/processed/temizlenmis_hasta_verisi.csv' yolunu kontrol edin."
        )

    df = pd.read_csv(dosya_yolu)

    gerekli_sutunlar = [
        "hasta_id", "cinsiyet", "yas", "hipertansiyon", "kalp_hastaligi",
        "evli_mi", "calisma_tipi", "ikamet_tipi", "ortalama_seker",
        "vucut_kitle_indeksi", "sigara_durumu", "inme_durumu"
    ]
    eksik = [s for s in gerekli_sutunlar if s not in df.columns]
    if eksik:
        raise ValueError(f"Veri setinde eksik sütunlar: {eksik}")

    print(f"✅ Veri yüklendi: {len(df)} kayıt, {len(df.columns)} sütun")
    return df


def _encoder_olustur() -> dict:
    """
    Kategorik sütunlar için CSV sırasına uygun {string: int} eşleşme
    sözlüklerini oluşturur.

    LabelEncoder.fit() alfabetik sıralama yaptığından CSV kodlamasıyla
    uyumsuzluk çıkar; bu nedenle sade dict kullanılır.

    Returns:
        dict: {sütun_adı: {kategori_string: int}} eşleşme sözlüğü
    """
    return {
        sutun: {kat: i for i, kat in enumerate(kategoriler)}
        for sutun, kategoriler in KATEGORIK_ESLESME.items()
    }


def veri_on_isle(df: pd.DataFrame) -> tuple:
    """
    Veriyi modele hazırlar: eksik değer temizleme,
    kategorik kodlama kontrolü, özellik/hedef ayrımı.

    CSV verisi halihazırda tam sayıya dönüştürülmüş olduğundan
    sayısal işlem uygulanır. Ancak predict.py'ın çalışabilmesi
    için LabelEncoder'lar elle oluşturulur ve kaydedilir.

    Args:
        df (pd.DataFrame): Ham veri seti

    Returns:
        tuple: (X, y, encoders) — özellikler, hedef, encoder dict
    """
    df = df.copy()

    # hasta_id model için gereksiz
    df = df.drop(columns=["hasta_id"], errors="ignore")

    # Eksik sayısal değerleri medyan ile doldur
    sayisal_sutunlar = df.select_dtypes(include=[np.number]).columns.tolist()
    for s in sayisal_sutunlar:
        if df[s].isnull().any():
            df[s].fillna(df[s].median(), inplace=True)

    # predict.py için encoder'ları elle oluştur
    encoders = _encoder_olustur()

    hedef = "inme_durumu"
    y = df[hedef]
    df = df.drop(columns=[hedef])

    X = df

    print(f"On isleme tamamlandi:")
    print(f"   Ozellik sayisi : {X.shape[1]}")
    print(f"   Egitim ornegi  : {len(X)}")
    print(f"   Sinif dagilimi : 0={sum(y==0)}, 1={sum(y==1)}")
    print(f"   Encoder sayisi : {len(encoders)}")

    return X, y, encoders


def smote_dengele(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    SMOTE ile azınlık sınıfını dengeler.
    Agent.md kuralı: SMOTE her zaman uygulanmalı.

    Args:
        X (pd.DataFrame): Özellikler
        y (pd.Series): Hedef

    Returns:
        tuple: (X_dengelenmis, y_dengelenmis)
    """
    smote = SMOTE(random_state=42)
    X_den, y_den = smote.fit_resample(X, y)

    print(f"✅ SMOTE uygulandı:")
    print(f"   Öncesi : 0={sum(y==0)}, 1={sum(y==1)}")
    print(f"   Sonrası: 0={sum(y_den==0)}, 1={sum(y_den==1)}")

    return X_den, y_den


# ════════════════════════════════════════════════════════════════
# MODEL EĞİTİMİ
# ════════════════════════════════════════════════════════════════

def model_egit(X_egitim: np.ndarray, y_egitim: np.ndarray) -> GradientBoostingClassifier:
    """
    Gradient Boosting modelini eğitir.
    SMOTE dengeleme ile yüksek inme risk tahmini doğruluğu sağlar.

    Args:
        X_egitim: Eğitim özellikleri
        y_egitim: Eğitim hedefleri

    Returns:
        GradientBoostingClassifier: Eğitilmiş model
    """
    print("\n🔄 Gradient Boosting modeli eğitiliyor...")
    print(f"   Parametreler: {GBM_PARAMS}")

    model = GradientBoostingClassifier(**GBM_PARAMS)
    model.fit(X_egitim, y_egitim)

    print("✅ Model eğitimi tamamlandı")
    return model


# ════════════════════════════════════════════════════════════════
# MODEL DEĞERLENDİRME
# ════════════════════════════════════════════════════════════════

def model_degerlendir(
    model: GradientBoostingClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
    X_egitim: np.ndarray,
    y_egitim: np.ndarray
) -> dict:
    """
    Modeli test seti ve cross-validation ile değerlendirir.
    Agent.md hedeflerine karşı kontrol eder.

    Args:
        model: Eğitilmiş model
        X_test: Test özellikleri
        y_test: Test hedefleri
        X_egitim: Eğitim özellikleri (cross-val için)
        y_egitim: Eğitim hedefleri (cross-val için)

    Returns:
        dict: Performans metrikleri
    """
    y_tahmin    = model.predict(X_test)
    y_olasilik  = model.predict_proba(X_test)[:, 1]

    metrikler = {
        "egitim_dogrulugu" : model.score(X_egitim, y_egitim),
        "test_dogrulugu"   : accuracy_score(y_test, y_tahmin),
        "precision"        : precision_score(y_test, y_tahmin, zero_division=0),
        "recall"           : recall_score(y_test, y_tahmin, zero_division=0),
        "f1_skoru"         : f1_score(y_test, y_tahmin, zero_division=0),
        "roc_auc"          : roc_auc_score(y_test, y_olasilik),
    }

    # Stratified K-Fold Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_skorlar = cross_val_score(model, X_egitim, y_egitim, cv=cv, scoring="accuracy")
    metrikler["cv_ortalama"]  = cv_skorlar.mean()
    metrikler["cv_std"]       = cv_skorlar.std()

    # Agent.md hedef kontrolü
    hedefler_karsilandi = (
        metrikler["test_dogrulugu"] >= HEDEF_DOGRULUK
        and metrikler["precision"]  >= HEDEF_PRECISION
        and metrikler["recall"]     >= HEDEF_RECALL
    )
    metrikler["hedefler_karsilandi"] = hedefler_karsilandi

    print("\n📊 MODEL PERFORMANS RAPORU")
    print("=" * 50)
    print(f"   Eğitim Doğruluğu  : %{metrikler['egitim_dogrulugu']*100:.2f}")
    print(f"   Test Doğruluğu    : %{metrikler['test_dogrulugu']*100:.2f}  "
          f"{'✅' if metrikler['test_dogrulugu'] >= HEDEF_DOGRULUK else '❌'} (Hedef: ≥%80)")
    print(f"   Precision         : %{metrikler['precision']*100:.2f}  "
          f"{'✅' if metrikler['precision'] >= HEDEF_PRECISION else '❌'} (Hedef: ≥%75)")
    print(f"   Recall            : %{metrikler['recall']*100:.2f}  "
          f"{'✅' if metrikler['recall'] >= HEDEF_RECALL else '❌'} (Hedef: ≥%75)")
    print(f"   F1 Skoru          : %{metrikler['f1_skoru']*100:.2f}")
    print(f"   ROC-AUC           : {metrikler['roc_auc']:.4f}")
    print(f"   CV Ortalama       : %{metrikler['cv_ortalama']*100:.2f} (±{metrikler['cv_std']*100:.2f})")
    print("=" * 50)

    if hedefler_karsilandi:
        print("🎉 TÜM HEDEF METRİKLER KARŞILANDI!")
    else:
        print("⚠️  Bazı hedef metrikler karşılanamadı. Hiperparametre ayarı gerekebilir.")

    print("\n📋 Detaylı Sınıflandırma Raporu:")
    print(classification_report(y_test, y_tahmin,
                                target_names=["Risk Yok (0)", "Risk Var (1)"]))

    cm = confusion_matrix(y_test, y_tahmin)
    print("Karmaşıklık Matrisi:")
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

    return metrikler


def onem_analizi(
    model: GradientBoostingClassifier,
    ozellik_adlari: list
) -> pd.DataFrame:
    """
    Özellik önem sıralamasını hesaplar ve döndürür.

    Args:
        model: Eğitilmiş Random Forest modeli
        ozellik_adlari: Özellik isim listesi

    Returns:
        pd.DataFrame: Önem skorlarına göre sıralanmış özellikler
    """
    onemler = pd.DataFrame({
        "ozellik": ozellik_adlari,
        "onem"   : model.feature_importances_
    }).sort_values("onem", ascending=False).reset_index(drop=True)

    print("\n🔍 ÖZELLİK ÖNEM SIRALAMALARI (Top 10):")
    print("-" * 35)
    for _, satir in onemler.head(10).iterrows():
        bar = "█" * int(satir["onem"] * 50)
        print(f"  {satir['ozellik']:25} {satir['onem']:.4f} {bar}")

    return onemler


# ════════════════════════════════════════════════════════════════
# MODEL KAYDETME / YÜKLEME
# ════════════════════════════════════════════════════════════════

def model_kaydet(
    model: GradientBoostingClassifier,
    encoders: dict,
    ozellik_adlari: list
) -> None:
    """
    Eğitilmiş modeli, encoder'ları ve özellik isimlerini diske kaydeder.

    Args:
        model: Eğitilmiş Random Forest modeli
        encoders: Label encoder sözlüğü
        ozellik_adlari: Özellik isim listesi

    Raises:
        IOError: Dosya yazma hatası
    """
    os.makedirs(MODEL_DIZIN, exist_ok=True)

    try:
        with open(MODEL_DOSYASI, "wb") as f:
            pickle.dump(model, f)

        with open(ENCODER_DOSYASI, "wb") as f:
            pickle.dump(encoders, f)

        with open(OZELLIK_DOSYASI, "wb") as f:
            pickle.dump(ozellik_adlari, f)

        print(f"\n💾 Model kaydedildi:")
        print(f"   Model   : {MODEL_DOSYASI}")
        print(f"   Encoders: {ENCODER_DOSYASI}")
        print(f"   Özellikler: {OZELLIK_DOSYASI}")

    except IOError as e:
        print(f"❌ Model kaydetme hatası: {str(e)}")
        raise


def model_yukle() -> tuple:
    """
    Kaydedilmiş modeli, encoder'ları ve özellik isimlerini yükler.

    Returns:
        tuple: (model, encoders, ozellik_adlari)

    Raises:
        FileNotFoundError: Model dosyaları bulunamazsa
    """
    for dosya in [MODEL_DOSYASI, ENCODER_DOSYASI, OZELLIK_DOSYASI]:
        if not os.path.exists(dosya):
            raise FileNotFoundError(
                f"Model dosyası bulunamadı: {dosya}\n"
                "Önce 'python model/train.py' çalıştırın."
            )

    with open(MODEL_DOSYASI, "rb") as f:
        model = pickle.load(f)

    with open(ENCODER_DOSYASI, "rb") as f:
        encoders = pickle.load(f)

    with open(OZELLIK_DOSYASI, "rb") as f:
        ozellik_adlari = pickle.load(f)

    return model, encoders, ozellik_adlari


# ════════════════════════════════════════════════════════════════
# ANA EĞİTİM AKIŞI
# ════════════════════════════════════════════════════════════════

def egitim_akisi() -> dict:
    """
    Tam eğitim pipeline'ını çalıştırır:
    Veri yükleme → Ön işleme → SMOTE → Eğitim → Değerlendirme → Kaydetme.

    Returns:
        dict: Performans metrikleri

    Raises:
        Exception: Herhangi bir adımda kritik hata
    """
    print("\n" + "═" * 60)
    print("  İNME RİSKİ TAHMİN MODELİ  —  EĞİTİM BAŞLATIYOR")
    print("═" * 60)

    try:
        # 1. Veri yükle
        df = veri_yukle(VERI_YOLU)

        # 2. Ön işleme
        X, y, encoders = veri_on_isle(df)
        ozellik_adlari = X.columns.tolist()

        # 3. Eğitim / test böl (stratified)
        X_egitim, X_test, y_egitim, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
        print(f"\n✅ Veri bölündü: Eğitim={len(X_egitim)}, Test={len(X_test)}")

        # 4. SMOTE — sadece eğitim setine uygula
        X_egitim_den, y_egitim_den = smote_dengele(X_egitim, y_egitim)

        # 5. Modeli eğit
        model = model_egit(X_egitim_den, y_egitim_den)

        # 6. Değerlendir
        metrikler = model_degerlendir(
            model, X_test, y_test, X_egitim_den, y_egitim_den
        )

        # 7. Özellik önemi
        onem_analizi(model, ozellik_adlari)

        # 8. Modeli kaydet
        model_kaydet(model, encoders, ozellik_adlari)

        print("\n" + "═" * 60)
        print("  ✅  EĞİTİM TAMAMLANDI — Model kullanıma hazır")
        print("═" * 60 + "\n")

        return metrikler

    except FileNotFoundError as e:
        print(f"\n❌ DOSYA HATASI: {e}")
        raise
    except Exception as e:
        print(f"\n❌ EĞİTİM HATASI: {e}")
        raise


# ════════════════════════════════════════════════════════════════
# ÇALIŞTIRMA NOKTASI
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    egitim_akisi()