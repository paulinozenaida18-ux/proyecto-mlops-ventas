import os

def test_archivos_existen():
    assert os.path.exists("src/train.py"), "El archivo train.py no existe"
    assert os.path.exists("data/ventas.csv"), "El archivo ventas.csv no existe"
