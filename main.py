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
from tensorflow.keras.models import load_model

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def descargar_modelo():
    file_id = "1LpJ77kovtk_MztVp2y6jbydoa2mcsQLV"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    ruta = "modelo_mnist.keras"

    # 🚨 Fuerza la descarga cada vez (para depurar)
    if os.path.exists(ruta):
        os.remove(ruta)

    print("Descargando modelo desde Google Drive...")
    response = requests.get(url)
    print(f"🪵 Estado descarga: {response.status_code}")
    print(f"🪵 Tipo de contenido: {response.headers.get('Content-Type')}")
    with open(ruta, "wb") as f:
        f.write(response.content)
    print("Modelo descargado.")

    return load_model(ruta)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predecir")
async def predecir(file: UploadFile = File(...)):
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

    return {"numero": "".join(digitos)}

# 👇 Este bloque permite que Railway ejecute el servidor correctamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
