from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import os
import requests
import math
from tensorflow.keras.models import load_model
import mysql.connector
from mysql.connector import Error

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def descargar_modelo():
    file_id = "1LpJ77kovtk_MztVp2y6jbydoa2mcsQLV"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    ruta = "modelo_mnist.keras"

    if not os.path.exists(ruta):
        print("Descargando modelo desde Google Drive...")
        response = requests.get(url)
        with open(ruta, "wb") as f:
            f.write(response.content)
        print("Modelo descargado.")

    return load_model(ruta)

modelo = descargar_modelo()

def numero_a_palabras(numero):
    palabras = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
    return ' '.join(palabras[int(d)] for d in numero)

def es_par(numero):
    try:
        return int(numero) % 2 == 0
    except:
        return False

def factorial_reducido(n):
    try:
        n = int(n)
        if n < 0:
            return "no válido"
        result = math.factorial(n)
        result_str = str(result)
        if len(result_str) > 10:
            principal = result_str[:10]
            exponente = len(result_str) - 1
            return f"{principal}e+{exponente}"
        return result_str
    except:
        return "indefinido"

def contar_digitos_primos(numero):
    primos = {'2', '3', '5', '7'}
    return sum(1 for d in numero if d in primos)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analizar")
async def analizar(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img_pil = Image.open(BytesIO(contents)).convert("L")
        img = np.array(img_pil)
        img = cv2.bitwise_not(img)
        _, thresh = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos = sorted(contornos, key=lambda c: cv2.boundingRect(c)[0])

        digitos = []
        for c in contornos:
            x, y, w, h = cv2.boundingRect(c)
            if w > 5 and h > 5:
                roi = thresh[y:y+h, x:x+w]
                roi = cv2.resize(roi, (18, 18))
                roi = cv2.copyMakeBorder(roi, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=0)
                roi = roi.astype("float32") / 255.0
                roi = np.expand_dims(roi, axis=-1)
                roi = np.expand_dims(roi, axis=0)
                pred = modelo.predict(roi, verbose=0)
                digito = np.argmax(pred)
                digitos.append(str(digito))

        numero = ''.join(digitos)
        fact = factorial_reducido(numero)

        # Intentar guardar en la base de datos
        mensaje_bd = "Los datos fueron enviados correctamente a la base de datos."
        try:
            guardar_en_bd(numero, fact)
        except Exception as e:
            print(f"❌ Error al guardar en BD: {e}")
            mensaje_bd = "Hubo un error al enviar los datos a la base."

        resultado = {
            "numero": numero,
            "palabras": numero_a_palabras(numero),
            "es_par": es_par(numero),
            "factorial": fact,
            "digitos_primos": contar_digitos_primos(numero),
            "mensaje_bd": mensaje_bd
        }

        return resultado

    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return {
            "numero": "Error",
            "palabras": "Error",
            "es_par": False,
            "factorial": "Error",
            "digitos_primos": "Error",
            "mensaje_bd": "Hubo un error interno en el análisis."
        }

    
def guardar_en_bd(numero_detectado: str, factorial: str):
    try:
        conn = mysql.connector.connect(
            host="www.server.daossystem.pro",
            port=3301,
            database="bd_ia_lf_2025",
            user="usr_ia_lf_2025",
            password="5sr_31_lf_2025"
        )
        if conn.is_connected():
            cursor = conn.cursor()
            query = """
                INSERT INTO segundo_parcial (valor, factorial, nombre_estudiante)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (numero_detectado, factorial, "Lester Estrada"))
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Información enviada a la base de datos.")
    except Error as e:
        print("❌ Error al guardar información en la base de datos:", e)

