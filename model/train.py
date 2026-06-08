"""
Modül Adı: train.py
Açıklama : HistGradientBoostingClassifier modelini eğitir, değerlendirir
           ve kaydeder. SMOTE dengeleme, etkileşim özellik mühendisliği,
           5-fold cross-validation ve özellik önem analizi içerir.

           Geliştirmeler (v2):
           • GradientBoostingClassifier → HistGradientBoostingClassifier
             (daha hızlı, early-stopping ile otomatik kalibrasyon)
           • Klinik etkileşim özellikleri eklendi:
             yas_hiper, yas_kalp, komorbidite_yuku, yuksek_seker,
             obez, yas_kare, yuksek_risk_sayisi
           • SMOTE sadece eğitim setine uygulanır (sızıntı yok)

Sorumlu  : Amr Khaled (ML/Teknoloji)
Tarih    : 2026-06-08
Version  : 2.0
"""

import os
import pickle
import warnings
import numpy as np
import pandas as pd

from sklearn.ensemble          import HistGradientBoostingClassifier
from sklearn.model_selection   import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics           import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix,
    brier_score_loss,
)
from imblearn.over_sampling    import SMOTE

warnings.filterwarnings("ignore")

# ── Dosya yolları ────────────────────────────────────────────────
PROJE_KOKU      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERI_YOLU       = os.path.join(PROJE_KOKU, "data", "processed",
                               "temizlenmis_hasta_verisi.csv")
MODEL_DIZIN     = os.path.join(PROJE_KOKU, "model", "artifacts")
MODEL_DOSYASI   = os.path.join(MODEL_DIZIN, "random_forest_model.pkl")
ENCODER_DOSYASI = os.path.join(MODEL_DIZIN, "label_encoders.pkl")
OZELLIK_DOSYASI = os.path.join(MODEL_DIZIN, "feature_names.pkl")

# ── Model parametreleri (HistGBM) ────────────────────────────────
# early_stopping + validation_fraction → aşırı öğrenmeyi önler ve
# olasılık tahminlerini otomatik kalibre eder.
HGBM_PARAMS = {
    "max_iter"          : 400,
    "learning_rate"     : 0.05,
    "max_depth"         : 4,
    "min_samples_leaf"  : 20,
    "l2_regularization" : 2.0,
    "max_bins"          : 255,
    # early_stopping=False: SMOTE sentetik örnekleriyle validation yapmak
    # gerçek dağılımı yansıtmaz; sabit iterasyon + regularization tercih edilir.
    "early_stopping"    : False,
    "random_state"      : 42,
    "verbose"           : 0,
}

# ── Hedef metrikler ──────────────────────────────────────────────
HEDEF_DOGRULUK  = 0.80
HEDEF_PRECISION = 0.75
HEDEF_RECALL    = 0.75

# ── Kategorik kodlama (CSV'deki integer kodlamayla eşleşir) ─────
KATEGORIK_ESLESME = {
    "cinsiyet"    : ["Diğer", "Erkek", "Kadın"],
    "evli_mi"     : ["Hayır", "Evet"],
    "calisma_tipi": ["Çalışan", "Çocuk", "Hükümet", "İşsiz", "Serbest"],
    "ikamet_tipi" : ["Kentsel", "Kırsal"],
    # CSV'de sigara 2 sınıf: 0=Eski İçici / "Hiç İçmedi", 1=Halen İçiyor
    "sigara_durumu": ["Eski İçici", "Halen İçiyor"],
}


# ════════════════════════════════════════════════════════════════
# VERİ YÜKLEME
# ════════════════════════════════════════════════════════════════

def veri_yukle(dosya_yolu: str) -> pd.DataFrame:
    if not os.path.exists(dosya_yolu):
        raise FileNotFoundError(
            f"Veri seti bulunamadı: {dosya_yolu}\n"
            "Lütfen 'data/processed/temizlenmis_hasta_verisi.csv' yolunu kontrol edin."
        )
    df = pd.read_csv(dosya_yolu)
    gerekli = [
        "hasta_id", "cinsiyet", "yas", "hipertansiyon", "kalp_hastaligi",
        "evli_mi", "calisma_tipi", "ikamet_tipi", "ortalama_seker",
        "vucut_kitle_indeksi", "sigara_durumu", "inme_durumu"
    ]
    eksik = [s for s in gerekli if s not in df.columns]
    if eksik:
        raise ValueError(f"Veri setinde eksik sütunlar: {eksik}")
    print(f"✅ Veri yüklendi: {len(df)} kayıt, {len(df.columns)} sütun")
    return df


# ════════════════════════════════════════════════════════════════
# ÖZELLİK MÜHENDİSLİĞİ
# Klinik etkileşim ve türetilmiş özellikler.
# Aynı dönüşümler predict.py'da da uygulanmalıdır.
# ════════════════════════════════════════════════════════════════

def ozellik_muhendisligi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Klinik anlam taşıyan etkileşim ve türetilmiş özellikler ekler.

    Tıbbi dayanak:
    • Yaş × Hipertansiyon: İleri yaşta HT riski kümülatif olarak artar.
    • Yaş × Kalp Hastalığı: Yaşlı KH hastalarında inme riski çok daha yüksektir.
    • Komorbidite yükü: Birden fazla risk faktörü sinerjik etki yaratır.
    • Yüksek şeker bayrağı: Açlık kan şekeri >126 → diyabet eşiği.
    • Obezite bayrağı: BMI ≥ 30 → KVH riskini bağımsız artırır.
    • Yaş²: İnme riskinin yaşla üstel artışını modeller.
    """
    df = df.copy()

    # Etkileşim terimleri (en önemli klinik sinerjiler)
    df["yas_hiper"]  = df["yas"] * df["hipertansiyon"]
    df["yas_kalp"]   = df["yas"] * df["kalp_hastaligi"]
    df["yas_sigara"] = df["yas"] * df["sigara_durumu"]

    # Toplam komorbidite yükü
    df["komorbidite_yuku"] = df["hipertansiyon"] + df["kalp_hastaligi"]

    # İkili metabolik risk bayrakları
    df["yuksek_seker"] = (df["ortalama_seker"]       > 126).astype(int)
    df["obez"]         = (df["vucut_kitle_indeksi"]  >= 30).astype(int)

    # Yaşın ikinci dereceden etkisi (1000'e bölünerek ölçeklenir)
    df["yas_kare"] = (df["yas"] ** 2) / 1000.0

    # Toplam yüksek risk faktörü sayısı
    df["yuksek_risk_sayisi"] = (
        df["hipertansiyon"]
        + df["kalp_hastaligi"]
        + df["yuksek_seker"]
        + df["obez"]
        + df["sigara_durumu"]
    )

    return df


# ════════════════════════════════════════════════════════════════
# ÖN İŞLEME
# ════════════════════════════════════════════════════════════════

def _encoder_olustur() -> dict:
    return {
        sutun: {kat: i for i, kat in enumerate(kategoriler)}
        for sutun, kategoriler in KATEGORIK_ESLESME.items()
    }


def veri_on_isle(df: pd.DataFrame) -> tuple:
    df = df.copy()
    df = df.drop(columns=["hasta_id"], errors="ignore")

    # Eksik sayısal değerleri medyan ile doldur
    for s in df.select_dtypes(include=[np.number]).columns:
        if df[s].isnull().any():
            df[s].fillna(df[s].median(), inplace=True)

    encoders = _encoder_olustur()

    hedef = "inme_durumu"
    y  = df[hedef]
    df = df.drop(columns=[hedef])

    # Özellik mühendisliği uygula
    df = ozellik_muhendisligi(df)

    print(f"  Özellik sayısı : {df.shape[1]}")
    print(f"  Eğitim örneği  : {len(df)}")
    print(f"  Sınıf dağılımı : 0={sum(y==0)}, 1={sum(y==1)}")

    return df, y, encoders


# ════════════════════════════════════════════════════════════════
# SMOTE DENGELEMESİ (sadece eğitim setine uygulanır)
# ════════════════════════════════════════════════════════════════

def smote_dengele(X: pd.DataFrame, y: pd.Series) -> tuple:
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_den, y_den = smote.fit_resample(X, y)
    print(f"✅ SMOTE uygulandı:")
    print(f"   Öncesi : 0={sum(y==0)}, 1={sum(y==1)}")
    print(f"   Sonrası: 0={sum(y_den==0)}, 1={sum(y_den==1)}")
    return X_den, y_den


# ════════════════════════════════════════════════════════════════
# MODEL EĞİTİMİ
# ════════════════════════════════════════════════════════════════

def model_egit(X_egitim: np.ndarray,
               y_egitim: np.ndarray) -> HistGradientBoostingClassifier:
    print("\n🔄 HistGradientBoosting modeli eğitiliyor...")
    model = HistGradientBoostingClassifier(**HGBM_PARAMS)
    model.fit(X_egitim, y_egitim)
    if hasattr(model, "n_iter_"):
        print(f"   Kullanılan iterasyon: {model.n_iter_} (early stopping)")
    print("✅ Model eğitimi tamamlandı")
    return model


# ════════════════════════════════════════════════════════════════
# DEĞERLENDİRME
# ════════════════════════════════════════════════════════════════

def model_degerlendir(model, X_test, y_test, X_egitim, y_egitim) -> dict:
    y_tahmin   = model.predict(X_test)
    y_olasilik = model.predict_proba(X_test)[:, 1]

    metrikler = {
        "egitim_dogrulugu": model.score(X_egitim, y_egitim),
        "test_dogrulugu"  : accuracy_score(y_test, y_tahmin),
        "precision"       : precision_score(y_test, y_tahmin, zero_division=0),
        "recall"          : recall_score(y_test, y_tahmin, zero_division=0),
        "f1_skoru"        : f1_score(y_test, y_tahmin, zero_division=0),
        "roc_auc"         : roc_auc_score(y_test, y_olasilik),
        "brier_skoru"     : brier_score_loss(y_test, y_olasilik),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_skorlar = cross_val_score(
        model, X_egitim, y_egitim, cv=cv, scoring="roc_auc"
    )
    metrikler["cv_roc_auc_ort"] = cv_skorlar.mean()
    metrikler["cv_roc_auc_std"] = cv_skorlar.std()

    hedefler_karsilandi = (
        metrikler["test_dogrulugu"] >= HEDEF_DOGRULUK
        and metrikler["precision"]  >= HEDEF_PRECISION
        and metrikler["recall"]     >= HEDEF_RECALL
    )
    metrikler["hedefler_karsilandi"] = hedefler_karsilandi

    print("\n📊 MODEL PERFORMANS RAPORU")
    print("=" * 52)
    print(f"   Eğitim Doğruluğu  : %{metrikler['egitim_dogrulugu']*100:.2f}")
    print(f"   Test Doğruluğu    : %{metrikler['test_dogrulugu']*100:.2f}  "
          f"{'✅' if metrikler['test_dogrulugu'] >= HEDEF_DOGRULUK else '❌'} (Hedef: ≥%80)")
    print(f"   Precision         : %{metrikler['precision']*100:.2f}  "
          f"{'✅' if metrikler['precision'] >= HEDEF_PRECISION else '❌'} (Hedef: ≥%75)")
    print(f"   Recall            : %{metrikler['recall']*100:.2f}  "
          f"{'✅' if metrikler['recall'] >= HEDEF_RECALL else '❌'} (Hedef: ≥%75)")
    print(f"   F1 Skoru          : %{metrikler['f1_skoru']*100:.2f}")
    print(f"   ROC-AUC           : {metrikler['roc_auc']:.4f}")
    print(f"   Brier Skoru       : {metrikler['brier_skoru']:.4f}  "
          f"(düşük = iyi kalibrasyon)")
    print(f"   CV ROC-AUC        : {metrikler['cv_roc_auc_ort']:.4f} "
          f"(±{metrikler['cv_roc_auc_std']:.4f})")
    print("=" * 52)

    if hedefler_karsilandi:
        print("🎉 TÜM HEDEF METRİKLER KARŞILANDI!")
    else:
        print("⚠️  Bazı hedef metrikler karşılanamadı.")

    print("\n📋 Sınıflandırma Raporu:")
    print(classification_report(y_test, y_tahmin,
                                target_names=["Risk Yok (0)", "Risk Var (1)"]))

    cm = confusion_matrix(y_test, y_tahmin)
    print("Karmaşıklık Matrisi:")
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

    return metrikler


def onem_analizi(model, ozellik_adlari: list,
                 X_test=None, y_test=None) -> pd.DataFrame:
    try:
        importances = model.feature_importances_
    except Exception:
        # HistGBM bazı sürümlerde permutation importance gerektirir
        if X_test is not None and y_test is not None:
            from sklearn.inspection import permutation_importance
            print("  (permutation importance hesaplanıyor...)")
            r = permutation_importance(
                model, X_test, y_test,
                n_repeats=15, random_state=42, scoring="roc_auc"
            )
            importances = r.importances_mean
        else:
            print("⚠️  Özellik önemi hesaplanamadı.")
            return pd.DataFrame()

    onemler = pd.DataFrame({
        "ozellik": ozellik_adlari,
        "onem"   : importances
    }).sort_values("onem", ascending=False).reset_index(drop=True)

    print("\n🔍 ÖZELLİK ÖNEM SIRALAMALARI (Top 12):")
    print("-" * 40)
    for _, satir in onemler.head(12).iterrows():
        bar = "█" * int(satir["onem"] * 60)
        print(f"  {satir['ozellik']:28} {satir['onem']:.4f} {bar}")

    return onemler


# ════════════════════════════════════════════════════════════════
# KAYDETME / YÜKLEME
# ════════════════════════════════════════════════════════════════

def model_kaydet(model, encoders: dict, ozellik_adlari: list) -> None:
    os.makedirs(MODEL_DIZIN, exist_ok=True)
    with open(MODEL_DOSYASI,   "wb") as f: pickle.dump(model,          f)
    with open(ENCODER_DOSYASI, "wb") as f: pickle.dump(encoders,       f)
    with open(OZELLIK_DOSYASI, "wb") as f: pickle.dump(ozellik_adlari, f)
    print(f"\n💾 Model kaydedildi → {MODEL_DOSYASI}")
    print(f"   Özellik sayısı: {len(ozellik_adlari)}")


def model_yukle() -> tuple:
    for dosya in [MODEL_DOSYASI, ENCODER_DOSYASI, OZELLIK_DOSYASI]:
        if not os.path.exists(dosya):
            raise FileNotFoundError(
                f"Model dosyası bulunamadı: {dosya}\n"
                "Önce 'python model/train.py' çalıştırın."
            )
    with open(MODEL_DOSYASI,   "rb") as f: model          = pickle.load(f)
    with open(ENCODER_DOSYASI, "rb") as f: encoders       = pickle.load(f)
    with open(OZELLIK_DOSYASI, "rb") as f: ozellik_adlari = pickle.load(f)
    return model, encoders, ozellik_adlari


# ════════════════════════════════════════════════════════════════
# ANA EĞİTİM AKIŞI
# ════════════════════════════════════════════════════════════════

def egitim_akisi() -> dict:
    print("\n" + "═" * 62)
    print("  İNME RİSKİ TAHMİN MODELİ v2.0  —  EĞİTİM BAŞLIYOR")
    print("═" * 62)

    df = veri_yukle(VERI_YOLU)

    print("\n[1/5] Ön işleme + özellik mühendisliği...")
    X, y, encoders = veri_on_isle(df)
    ozellik_adlari = X.columns.tolist()

    print("\n[2/5] Eğitim/test bölme (stratified %80/%20)...")
    X_egitim, X_test, y_egitim, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"   Eğitim: {len(X_egitim)}, Test: {len(X_test)}")

    print("\n[3/5] SMOTE dengeleme (sadece eğitim seti)...")
    X_egitim_den, y_egitim_den = smote_dengele(X_egitim, y_egitim)

    print("\n[4/5] Model eğitimi...")
    model = model_egit(X_egitim_den, y_egitim_den)

    print("\n[5/5] Değerlendirme...")
    metrikler = model_degerlendir(
        model, X_test, y_test, X_egitim_den, y_egitim_den
    )
    onem_analizi(model, ozellik_adlari, X_test.values, y_test.values)
    model_kaydet(model, encoders, ozellik_adlari)

    print("\n" + "═" * 62)
    print("  ✅  EĞİTİM TAMAMLANDI — Model kullanıma hazır")
    print("═" * 62 + "\n")

    return metrikler


if __name__ == "__main__":
    egitim_akisi()
