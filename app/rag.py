import pandas as pd

def cargar_datos():

return pd.read_csv(
"data/ventas.csv"
)

def buscar_ventas(dia):

datos = cargar_datos()

resultado = datos[
datos["dia"] == dia
]
if resultado.empty:
return None

return int(
resultado["ventas"].values[0]
)

def obtener_maxima_venta():

datos = cargar_datos()

fila = datos.loc[
datos["ventas"].idxmax()
]

return {
"dia": int(fila["dia"]),
"ventas": int(fila["ventas"])
}

def obtener_promedio_ventas():

datos = cargar_datos()

return round(
datos["ventas"].mean(),
)

def generar_respuesta_natural(dia):

venta = buscar_ventas(dia)

if venta is None:

return (
f"No existe información "
f"para el día {dia}"
)

return (
f"Las ventas registradas "
f"para el día {dia} "
f"fueron {venta} unidades."
)
