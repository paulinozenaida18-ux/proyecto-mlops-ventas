from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import logging
import time
from datetime import datetime
import os

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
# PREDICCIONES
# ===================================================

@app.post("/predict")
def predict(datos: Entrada):

global TOTAL_REQUESTS

TOTAL_REQUESTS += 1

# Medición de latencia

tiempo_inicio = time.time()

# Seleccionar modelo activo

if ACTIVE_MODEL == "BLUE":

resultado = modelo_blue.predict(
[[datos.dia]]
)

else:

resultado = modelo_green.predict(
[[datos.dia]]
)

tiempo_fin = time.time()

latencia = tiempo_fin - tiempo_inicio

prediccion = float(resultado[0])

# Registrar en logs

pred_logger.info(

f"{datetime.now()} | "
f"Modelo={ACTIVE_MODEL} | "
f"Dia={datos.dia} | "
f"Prediccion={prediccion:.2f} | "
f"Latencia={latencia:.6f}"

)

return {

"modelo_utilizado": ACTIVE_MODEL,

"dia": datos.dia,

"prediccion": prediccion,

"latencia_segundos": round(
latencia,
6
)

}

# ===================================================
# BLUE-GREEN DEPLOYMENT
# ===================================================

@app.put("/switch/{color}")
def switch_model(color: str):

global ACTIVE_MODEL

color = color.upper()

if color not in ["BLUE", "GREEN"\]:

return {
"error":
"Debe elegir BLUE o GREEN"
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
