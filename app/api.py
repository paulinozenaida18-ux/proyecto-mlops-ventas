from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import logging
import time
from datetime import datetime
import os

#.....
from app.rag import (
generar_respuesta_natural,
obtener_maxima_venta,
obtener_promedio_ventas
)



# ===================================================
# CREACIÓN DE CARPETA DE LOGS
# ===================================================

os.makedirs("logs", exist_ok=True)

# ===================================================
# CONFIGURACIÓN DE LOGS
# ===================================================

pred_logger = logging.getLogger("predicciones")
pred_logger.setLevel(logging.INFO)

pred_handler = logging.FileHandler(
"logs/predicciones.log"
)
pred_formatter = logging.Formatter(
"%(message)s"
)
pred_handler.setFormatter(pred_formatter)

if not pred_logger.handlers:
pred_logger.addHandler(pred_handler)

# --------------------------------------------

deploy_logger = logging.getLogger("deployment")
deploy_logger.setLevel(logging.INFO)

deploy_handler = logging.FileHandler(
"logs/deployment.log"
)
deploy_formatter = logging.Formatter(
"%(message)s"
)
deploy_handler.setFormatter(deploy_formatter)

if not deploy_logger.handlers:
deploy_logger.addHandler(deploy_handler)

# ===================================================
# FASTAPI
# ===================================================

app = FastAPI()

# endpoints cambios por partes
logging.basicConfig(level=logging.INFO)
pred_logger = logging.getLogger(
"predicciones"
)
pred_handler = logging.FileHandler(
"logs/predicciones.log"
)
 pred_logger.addHandler(
pred_handler
)
deploy_logger = logging.getLogger(
"deployment"
)
 
deploy_handler = logging.FileHandler(
"logs/deployment.log"
)
deploy_logger.addHandler(
deploy_handler
)


# ===================================================
# CARGAR MODELOS
# ===================================================

modelo_blue = joblib.load(
"models/modelo.pkl"
)

modelo_green = joblib.load(
"models/modelo_nuevo.pkl"
)

# Modelo que está atendiendo actualmente

ACTIVE_MODEL = "BLUE"

# Contador básico de solicitudes

TOTAL_REQUESTS = 0

# ===================================================
# CLASE DE ENTRADA
# ===================================================

class Entrada(BaseModel):
dia: int

# ===================================================
# ESTADO DE LA API
# ===================================================

@app.get("/")
def inicio():

return {
"estado": "activo",
"modelo_activo": ACTIVE_MODEL
}

# ===================================================
# MÉTRICAS BÁSICAS
# ===================================================

@app.get("/metrics")
def metrics():

    return {

        "estado": "ok",

        "modelo_activo": ACTIVE_MODEL,

        "total_predicciones":
        TOTAL_REQUESTS

    }
  # ===================================================
# ===================================================
# RAG - CONSULTA DE VENTAS
# ===================================================

@app.get("/consulta/{dia}")
def consulta(dia: int):

    respuesta = generar_respuesta_natural(dia)

    return {
        "respuesta": respuesta
    }


# ===================================================
# RAG - MAYOR VENTA
# ===================================================

@app.get("/max-ventas")
def max_ventas():

    resultado = obtener_maxima_venta()

    return {
        "mensaje": f"El día con mayores ventas fue {resultado['dia']}",
        "ventas": resultado["ventas"]
    }


# ===================================================
# RAG - PROMEDIO DE VENTAS
# ===================================================

@app.get("/promedio-ventas")
def promedio_ventas():

    promedio = obtener_promedio_ventas()

    return {
        "promedio": promedio
    }
# ===================================================
# PREDICCIONES
# ===================================================

@app.post("/predict")
def predict(datos: Entrada):
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
return {
"modelo": ACTIVE_MODEL,
"dia": datos.dia,
"prediccion": float(resultado[0]),
"latencia": latencia
}
# latencia:
pred_logger.info(
f"{datetime.now()} | "
f"Modelo={ACTIVE_MODEL} | "
 f"Dia={datos.dia} | "
f"Prediccion={float(resultado[0])} | "
f"Latencia={latencia}"
)

# ===================================================
# BLUE-GREEN DEPLOYMENT
# ===================================================

@app.put("/switch/{color}")
def switch_model(color: str):
global ACTIVE_MODEL
color = color.upper()
if color not in ["BLUE","GREEN"\]:
return {
"error":
"Color inválido"
}
modelo_anterior = ACTIVE_MODEL
ACTIVE_MODEL = color
deploy_logger.info(
f"{datetime.now()} | "
f"{modelo_anterior} -> "
f"{ACTIVE_MODEL}"
)
return {
"mensaje":
f"Cambio realizado a {ACTIVE_MODEL}"
}


return {

"mensaje":
f"Producción ahora usa {ACTIVE_MODEL}"

}

# ===================================================
# RECARGAR MODELOS
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

return {

"mensaje":
"Modelos recargados exitosamente"

}

# ===================================================
# MÉTRICAS BÁSICAS
# ===================================================

@app.get("/metrics")
def metrics():

return {

"estado": "ok",

"modelo_activo": ACTIVE_MODEL,

"total_predicciones":
TOTAL_REQUESTS

}

# ===================================================
# RESET DEL SERVICIO
# ===================================================

@app.delete("/reset")
def reset_service():

return {

"mensaje":
"Recursos reiniciados correctamente"

}
