from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import logging
import time
from datetime import datetime
import os

from app.rag import (
    generar_respuesta_natural,
    obtener_maxima_venta,
    obtener_promedio_ventas
)

from app.audit import (
    registrar_evento
)

# ===================================================
# CREACIÓN DE CARPETA DE LOGS
# ===================================================

os.makedirs("logs", exist_ok=True)

# ===================================================
# CONFIGURACIÓN DE LOGS
# ===================================================

logging.basicConfig(level=logging.INFO)

# --------------------------------------------
# LOG DE PREDICCIONES
# --------------------------------------------

pred_logger = logging.getLogger("predicciones")

pred_logger.setLevel(logging.INFO)

pred_handler = logging.FileHandler(
    "logs/predicciones.log"
)

pred_formatter = logging.Formatter(
    "%(message)s"
)

pred_handler.setFormatter(
    pred_formatter
)

if not pred_logger.handlers:
    pred_logger.addHandler(
        pred_handler
    )

# --------------------------------------------
# LOG DE DESPLIEGUES
# --------------------------------------------

deploy_logger = logging.getLogger(
    "deployment"
)

deploy_logger.setLevel(
    logging.INFO
)

deploy_handler = logging.FileHandler(
    "logs/deployment.log"
)

deploy_formatter = logging.Formatter(
    "%(message)s"
)

deploy_handler.setFormatter(
    deploy_formatter
)

if not deploy_logger.handlers:
    deploy_logger.addHandler(
        deploy_handler
    )

# ===================================================
# FASTAPI
# ===================================================

app = FastAPI()

# ===================================================
# CARGA DE MODELOS
# ===================================================

modelo_blue = joblib.load(
    "models/modelo.pkl"
)

modelo_green = joblib.load(
    "models/modelo_nuevo.pkl"
)

# ===================================================
# CONFIGURACIÓN
# ===================================================

ACTIVE_MODEL = "BLUE"

TOTAL_REQUESTS = 0

# ===================================================
# MODELO DE ENTRADA
# ===================================================

class Entrada(BaseModel):

    dia: int

# ===================================================
# ESTADO DE LA API
# ===================================================

@app.get("/")
def inicio():

    return {

        "estado":
        "activo",

        "modelo_activo":
        ACTIVE_MODEL

    }

# ===================================================
# MÉTRICAS
# ===================================================

@app.get("/metrics")
def metrics():

    return {

        "estado":
        "ok",

        "modelo_activo":
        ACTIVE_MODEL,

        "total_predicciones":
        TOTAL_REQUESTS

    }

# ===================================================
# RAG - CONSULTA DE VENTAS
# ===================================================

@app.get("/consulta/{dia}")
def consulta(dia: int):

    respuesta = generar_respuesta_natural(
        dia
    )

    registrar_evento(
        "CONSULTA_RAG",
        f"Dia={dia}"
    )

    return {

        "respuesta":
        respuesta

    }

# ===================================================
# RAG - MAYOR VENTA
# ===================================================

@app.get("/max-ventas")
def max_ventas():

    resultado = obtener_maxima_venta()

    registrar_evento(
        "CONSULTA_MAX_VENTAS",
        f"Resultado={resultado}"
    )

    return {

        "mensaje":
        f"El día con mayores ventas fue {resultado['dia']}",

        "ventas":
        resultado["ventas"]

    }

# ===================================================
# RAG - PROMEDIO DE VENTAS
# ===================================================

@app.get("/promedio-ventas")
def promedio_ventas():

    promedio = obtener_promedio_ventas()

    registrar_evento(
        "CONSULTA_PROMEDIO",
        f"Promedio={promedio}"
    )

    return {

        "promedio":
        promedio

    }

# ===================================================
# PREDICCIONES
# ===================================================

@app.post("/predict")
def predict(datos: Entrada):

    global TOTAL_REQUESTS

    TOTAL_REQUESTS += 1

    inicio = time.time()

    if ACTIVE_MODEL == "BLUE":

        resultado = modelo_blue.predict(
            [[datos.dia]]
        )

    else:

        resultado = modelo_green.predict(
            [[datos.dia]]
        )

    fin = time.time()

    latencia = fin - inicio

    prediccion_valor = float(
        resultado[0]
    )

    pred_logger.info(

        f"{datetime.now()} | "

        f"Modelo={ACTIVE_MODEL} | "

        f"Dia={datos.dia} | "

        f"Prediccion={prediccion_valor} | "

        f"Latencia={latencia}"

    )

    registrar_evento(

        "PREDICCION",

        f"Modelo={ACTIVE_MODEL}, "

        f"Dia={datos.dia}, "

        f"Prediccion={prediccion_valor}"

    )

    return {

        "modelo":
        ACTIVE_MODEL,

        "dia":
        datos.dia,

        "prediccion":
        prediccion_valor,

        "latencia":
        latencia

    }

# ===================================================
# BLUE-GREEN DEPLOYMENT
# ===================================================

@app.put("/switch/{color}")
def switch_model(color: str):

    global ACTIVE_MODEL

    color = color.upper()

    if color not in ["BLUE", "GREEN"]:

        return {

            "error":
            "Color inválido"

        }

    modelo_anterior = ACTIVE_MODEL

    ACTIVE_MODEL = color

    registrar_evento(

        "CAMBIO_MODELO",

        f"{modelo_anterior}->{ACTIVE_MODEL}"

    )

    deploy_logger.info(

        f"{datetime.now()} | "

        f"{modelo_anterior} -> "

        f"{ACTIVE_MODEL}"

    )

    return {

        "mensaje":
        f"Producción ahora usa {ACTIVE_MODEL}"

    }

# ===================================================
# RECARGA DE MODELOS
# ===================================================

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

    registrar_evento(
        "RELOAD_MODELOS",
        "Modelos recargados"
    )

    return {

        "mensaje":
        "Modelos recargados exitosamente"

    }

# ===================================================
# INFORMACIÓN DEL MODELO
# ===================================================

@app.get("/modelo-info")
def modelo_info():

    registrar_evento(

        "CONSULTA_MODELO",

        ACTIVE_MODEL

    )

    return {

        "modelo_activo":
        ACTIVE_MODEL,

        "version_blue":
        "LinearRegression",

        "version_green":
        "DecisionTreeRegressor"

    }

# ===================================================
# GOBERNANZA IA
# ===================================================

@app.get("/governance")
def governance():

    registrar_evento(

        "CONSULTA_GOVERNANCE",

        ACTIVE_MODEL

    )

    return {

        "cumple_auditoria":
        True,

        "logging":
        True,

        "trazabilidad":
        True,

        "modelo_activo":
        ACTIVE_MODEL

    }

# ===================================================
# RESET
# ===================================================

@app.delete("/reset")
def reset_service():

    global TOTAL_REQUESTS

    TOTAL_REQUESTS = 0

    registrar_evento(
        "RESET",
        "Contador reiniciado"
    )

    return {

        "mensaje":
        "Recursos reiniciados correctamente"

    }
