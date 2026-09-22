from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# ==========================
# CARGA DE MODELOS
# ==========================

modelo_blue = joblib.load("models/modelo.pkl")

modelo_green = joblib.load("models/modelo_nuevo.pkl")

# Modelo activo en producción
ACTIVE_MODEL = "BLUE"


# ==========================
# CLASE DE ENTRADA
# ==========================

class Entrada(BaseModel):
    dia: int


# ==========================
# ESTADO DEL SERVICIO
# ==========================

@app.get("/")
def inicio():

    return {
        "estado": "activo",
        "modelo_activo": ACTIVE_MODEL
    }


# ==========================
# PREDICCION
# ==========================

@app.post("/predict")
def predict(datos: Entrada):

    if ACTIVE_MODEL == "BLUE":

        resultado = modelo_blue.predict([[datos.dia]])

    else:

        resultado = modelo_green.predict([[datos.dia]])

    return {
        "modelo_utilizado": ACTIVE_MODEL,
        "dia": datos.dia,
        "prediccion": float(resultado[0])
    }


# ==========================
# SWITCH BLUE-GREEN
# ==========================

@app.put("/switch/{color}")
def switch_model(color: str):

    global ACTIVE_MODEL

    color = color.upper()

    if color not in ["BLUE", "GREEN"\]:

        return {
            "error": "Debe elegir BLUE o GREEN"
        }

    ACTIVE_MODEL = color

    return {
        "mensaje": f"Producción ahora utiliza {ACTIVE_MODEL}"
    }


# ==========================
# RECARGAR MODELOS
# ==========================

@app.put("/reload-model")
def reload_model():

    global modelo_blue
    global modelo_green

    modelo_blue = joblib.load(
        "models/modelo.pkl"
    )

    modelo_green = joblib.load(
        "models/modelo_nuevo.pkl"
    )

    return {
        "mensaje":
        "Modelos recargados correctamente"
    }


# ==========================
# RESET
# ==========================

@app.delete("/reset")
def reset_service():

    return {
        "mensaje":
        "Recursos reiniciados"
    }
