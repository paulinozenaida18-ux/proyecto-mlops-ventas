 from fastapi import FastAPI
import joblib

app = FastAPI()
# joblib.load(...) carga el modelo entrenado
modelo = joblib.load("models/modelo.pkl")

@app.get("/")
def inicio():
return {"estado":"activo"}
