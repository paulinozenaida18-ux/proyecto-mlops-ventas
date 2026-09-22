import os
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# 1. Asegurar que la carpeta models exista
os.makedirs("models", exist_ok=True)

# 2. Cargar los datos de entrenamiento
datos = pd.read_csv("data/ventas.csv")

X = datos[["dia"]]
y = datos["ventas"]

# 3. Entrenar el modelo
modelo = LinearRegression()
modelo.fit(X, y)

# 4. Guardar ambas versiones (o la que corresponda para tus entornos Blue y Green)
joblib.dump(modelo, "models/modelo.pkl")
print("Modelo principal (Blue) guardado en models/modelo.pkl")

joblib.dump(modelo, "models/modelo_nuevo.pkl")
print("Nuevo modelo (Green) guardado en models/modelo_nuevo.pkl")
