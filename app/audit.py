import logging
import os
from datetime import datetime

# ============================================
# CREAR CARPETA DE LOGS
# ============================================

os.makedirs(
    "logs",
    exist_ok=True
)

# ============================================
# LOGGER DE AUDITORIA
# ============================================

audit_logger = logging.getLogger(
    "audit"
)

audit_logger.setLevel(
    logging.INFO
)

audit_handler = logging.FileHandler(
    "logs/audit.log"
)

audit_formatter = logging.Formatter(
    "%(message)s"
)

audit_handler.setFormatter(
    audit_formatter
)

if not audit_logger.handlers:
    audit_logger.addHandler(
        audit_handler
    )

# ============================================
# REGISTRAR EVENTOS
# ============================================

def registrar_evento(
    accion,
    detalle
):

    audit_logger.info(
        f"{datetime.now()} | "
        f"{accion} | "
        f"{detalle}"
    )
