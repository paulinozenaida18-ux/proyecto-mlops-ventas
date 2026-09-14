from fastapi import FastAPI
import joblib

app = FastAPI()

# Cargamos el modelo entrenado
modelo = joblib.load("models/modelo.pkl")

#@app.get("/")
#def inicio():
    #return {"estado": "activo"}

@app.get("/predict")
def predict(dia: int):
    resultado = modelo.predict([[dia]])
    return {
        "dia": dia,
        "prediccion": float(resultado[0])
    }
