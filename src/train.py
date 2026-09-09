import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

os.makedirs("models", exist_ok=True)

datos = pd.read_csv("data/ventas.csv")

X = datos[["dia"]]
y = datos["ventas"]

modelo = LinearRegression()
modelo.fit(X, y)

joblib.dump(modelo, "models/modelo.pkl")

print("Modelo guardado")
