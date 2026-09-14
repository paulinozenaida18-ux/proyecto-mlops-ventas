from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Cargar el modelo entrenado
modelo = joblib.load("models/modelo.pkl")

# Definir la estructura de entrada usando Pydantic
class Entrada(BaseModel):
    dia: int

# 1. GET: Consultar estado de la API
@app.get("/")
def inicio():
    return {"estado": "activo"}

# 2. POST: Hacer predicciones enviando JSON
@app.post("/predict")
def predict(datos: Entrada):
    resultado = modelo.predict([[datos.dia]])
    return {
        "dia": datos.dia,
        "prediccion": float(resultado[0])
    }

# 3. PUT: Actualizar o recargar el modelo en memoria
@app.put("/reload-model")
def reload_model():
    global modelo
    modelo = joblib.load("models/modelo.pkl")
    return {"mensaje": "Modelo recargado exitosamente en memoria"}

# 4. DELETE: Simular la deshabilitación del servicio o liberación de recursos
@app.delete("/reset")
def reset_service():
    return {"mensaje": "Recursos de la sesión reiniciados correctamente"}
