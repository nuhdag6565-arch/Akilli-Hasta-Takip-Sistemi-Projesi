import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/temizlenmis_hasta_verisi.csv")

print(df.head())
print(df.describe())

sns.countplot(x="stroke", data=df)
plt.title("Stroke Distribution")
plt.show()

sns.heatmap(df.corr(), annot=True)
plt.title("Feature Correlation")
plt.show()