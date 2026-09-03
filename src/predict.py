import joblib
import pandas as pd

# Cargar el modelo entrenado
modelo = joblib.load("models/modelo.pkl")

# Crear la entrada como DataFrame respetando el nombre de columna 'dia'
dia = pd.DataFrame({"dia": [12]})

# Realizar la predicción
prediccion = modelo.predict(dia)

print(prediccion)