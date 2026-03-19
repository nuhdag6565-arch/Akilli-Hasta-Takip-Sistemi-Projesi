import pandas as pd

df = pd.read_csv("data/temizlenmis_hasta_verisi.csv")

print(df.columns)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("data/temizlenmis_hasta_verisi.csv")

label = LabelEncoder()

for col in df.select_dtypes(include='object').columns:
    df[col] = label.fit_transform(df[col])

X = df.drop("inme_durumu", axis=1)
y = df["inme_durumu"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

pred = model.predict(X_test)

acc = accuracy_score(y_test, pred)

print("Model Accuracy:", acc)

joblib.dump(model, "stroke_model.pkl")