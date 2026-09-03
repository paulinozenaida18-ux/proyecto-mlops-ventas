import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

datos = pd.read_csv("data/ventas.csv")

X = datos[["dia"]]

y = datos["ventas"]

modelo = LinearRegression()

modelo.fit(X, y)

joblib.dump(modelo, "models/modelo.pkl")

print("Modelo guardado")
