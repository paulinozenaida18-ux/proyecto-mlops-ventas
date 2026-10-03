from fastapi import Header, HTTPException
from app.audit import (
registrar_evento
)

# ===================================================
# API KEY DEL SISTEMA
# ===================================================

API_KEY = "UMA-IA-2026"

# ===================================================
# VALIDAR API KEY
# ===================================================

def validar_api_key(
x_api_key: str = Header(None)
):

if x_api_key != API_KEY:

registrar_evento(
"ACCESO_DENEGADO",
"API KEY INVALIDA"
)

raise HTTPException(

status_code=401,

detail="API Key inválida"

)

registrar_evento(
"ACCESO_AUTORIZADO",
"API KEY CORRECTA"
)

return True
