from datetime import datetime
import logging
import os
from fastapi import Depends, FastAPI
import joblib
import logging
import os
import time  # <-- Asegúrate de agregar esta línea
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field

from app.audit import registrar_evento
from app.rag import (
    generar_respuesta_natural,
    obtener_maxima_venta,
    obtener_promedio_ventas,
)
from app.security import validar_api_key

# ===================================================
# CREACIÓN Y CONFIGURACIÓN DE LOGS
# ===================================================

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO)

# Log de Predicciones
pred_logger = logging.getLogger("predicciones")
pred_logger.setLevel(logging.INFO)
pred_handler = logging.FileHandler("logs/predicciones.log")
pred_handler.setFormatter(logging.Formatter("%(message)s"))
if not pred_logger.handlers:
    pred_logger.addHandler(pred_handler)

# Log de Despliegues
deploy_logger = logging.getLogger("deployment")
deploy_logger.setLevel(logging.INFO)
deploy_handler = logging.FileHandler("logs/deployment.log")
deploy_handler.setFormatter(logging.Formatter("%(message)s"))
if not deploy_logger.handlers:  # Corregido: antes evaluaba pred_logger
    deploy_logger.addHandler(deploy_handler)

# ===================================================
# FASTAPI Y ESTADO GLOBAL
# ===================================================

app = FastAPI()

ACTIVE_MODEL = "BLUE"
TOTAL_REQUESTS = 0

# ===================================================
# CARGA DE MODELOS
# ===================================================

modelo_blue = joblib.load("models/modelo.pkl")
modelo_green = joblib.load("models/modelo_nuevo.pkl")


# ===================================================
# MODELO DE ENTRADA
# ===================================================


class Entrada(BaseModel):
    dia: int = Field(gt=0, le=365, description="Día válido")


# ===================================================
# ESTADO DE LA API Y MÉTRICAS
# ===================================================


@app.get("/")
def inicio():
    return {"estado": "activo", "modelo_activo": ACTIVE_MODEL}


@app.get("/metrics")
def metrics():
    return {
        "estado": "ok",
        "modelo_activo": ACTIVE_MODEL,
        "total_predicciones": TOTAL_REQUESTS,
    }


# ===================================================
# RAG - CONSULTAS DE VENTAS
# ===================================================


@app.get("/consulta/{dia}")
def consulta(dia: int, autorizado: bool = Depends(validar_api_key)):
    respuesta = generar_respuesta_natural(dia)
    registrar_evento("CONSULTA_RAG", f"Dia={dia}")
    return {"respuesta": respuesta}


@app.get("/max-ventas")
def max_ventas(autorizado: bool = Depends(validar_api_key)):
    resultado = obtener_maxima_venta()
    registrar_evento("CONSULTA_MAX_VENTAS", str(resultado))
    return {
        "mensaje": f"El día con mayores ventas fue {resultado['dia']}",
        "ventas": resultado["ventas"],
    }


@app.get("/promedio-ventas")
def promedio_ventas(autorizado: bool = Depends(validar_api_key)):
    promedio = obtener_promedio_ventas()
    registrar_evento("CONSULTA_PROMEDIO", f"Promedio={promedio}")
    return {"promedio": promedio}


# ===================================================
# PREDICCIONES
# ===================================================


@app.post("/predict")
def predict(datos: Entrada, autorizado: bool = Depends(validar_api_key)):
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1

    inicio = time_inicio = time.time()

    if ACTIVE_MODEL == "BLUE":
        resultado = modelo_blue.predict([[datos.dia]])
    else:
        resultado = modelo_green.predict([[datos.dia]])

    fin = time.time()
    latencia = fin - time_inicio
    prediccion_valor = float(resultado[0])

    pred_logger.info(
        f"{datetime.now()} | Modelo={ACTIVE_MODEL} | Dia={datos.dia} | Prediccion={prediccion_valor} | Latencia={latencia}"
    )

    registrar_evento(
        "PREDICCION",
        f"Modelo={ACTIVE_MODEL}, Dia={datos.dia}, Prediccion={prediccion_valor}",
    )

    return {
        "modelo": ACTIVE_MODEL,
        "dia": datos.dia,
        "prediccion": prediccion_valor,
        "latencia": latencia,
    }


# ===================================================
# GESTIÓN DE MODELOS (DEPLOYMENT Y RECARGA)
# ===================================================


@app.put("/switch/{color}")
def switch_model(color: str):
    global ACTIVE_MODEL
    color = color.upper()

    if color not in ["BLUE", "GREEN"]:
        return {"error": "Color inválido"}

    modelo_anterior = ACTIVE_MODEL
    ACTIVE_MODEL = color

    registrar_evento("CAMBIO_MODELO", f"{modelo_anterior}->{ACTIVE_MODEL}")
    deploy_logger.info(f"{datetime.now()} | {modelo_anterior} -> {ACTIVE_MODEL}")

    return {"mensaje": f"Producción ahora usa {ACTIVE_MODEL}"}


@app.put("/reload-model")
def reload_model():
    global modelo_blue, modelo_green
    modelo_blue = joblib.load("models/modelo.pkl")
    modelo_green = joblib.load("models/modelo_nuevo.pkl")

    registrar_evento("RELOAD_MODELOS", "Modelos recargados")
    return {"mensaje": "Modelos recargados exitosamente"}


# ===================================================
# INFORMACIÓN, GOBERNANZA Y SEGURIDAD
# ===================================================


@app.get("/modelo-info")
def modelo_info():
    registrar_evento("CONSULTA_MODELO", ACTIVE_MODEL)
    return {
        "modelo_activo": ACTIVE_MODEL,
        "version_blue": "LinearRegression",
        "version_green": "DecisionTreeRegressor",
    }


@app.get("/governance")
def governance():
    registrar_evento("CONSULTA_GOVERNANCE", ACTIVE_MODEL)
    return {
        "cumple_auditoria": True,
        "logging": True,
        "trazabilidad": True,
        "modelo_activo": ACTIVE_MODEL,
    }


@app.get("/security-status")
def security_status():
    registrar_evento("CONSULTA_SEGURIDAD", ACTIVE_MODEL)
    return {
        "api_key": True,
        "input_validation": True,
        "audit": True,
        "monitoring": True,
        "modelo_activo": ACTIVE_MODEL,
    }


# ===================================================
# RESET
# ===================================================


@app.delete("/reset")
def reset_service():
    global TOTAL_REQUESTS
    TOTAL_REQUESTS = 0
    registrar_evento("RESET", "Contador reiniciado")
    return {"mensaje": "Recursos reiniciados correctamente"}
