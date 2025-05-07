const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const preview = document.getElementById("preview");

function mostrarPrevisualizacion() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
            canvas.style.display = "none";
            video.style.display = "none";
        };
        reader.readAsDataURL(file);
    }
}

function iniciarCamara() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.style.display = "block";
            preview.style.display = "none";
        })
        .catch(err => alert("No se pudo acceder a la cámara."));
}

function capturarFrame() {
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);
    canvas.style.display = "block";
}

async function procesarImagen() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];
    const resultado = document.getElementById("resultado");
    resultado.innerHTML = "";

    const formData = new FormData();

    if (file) {
        formData.append("file", file);
    } else if (canvas.width > 0 && canvas.height > 0) {
        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg"));
        formData.append("file", blob, "captura.jpg");
    } else {
        alert("Primero selecciona una imagen o captura una desde la cámara.");
        return;
    }

    try {
        const res = await fetch("/analizar", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        resultado.innerHTML = `
        <strong>Número detectado:</strong> ${data.numero}<br>
        <strong>En palabras:</strong> ${data.palabras}<br>
        <strong>¿Es par?:</strong> ${data.es_par ? "Sí" : "No"}<br>
        <strong>Factorial:</strong> ${data.factorial}<br>
        <strong>Dígitos primos:</strong> ${data.primos}
    `;
    
    } catch (err) {
        resultado.innerHTML = `<span style="color:red;">❌ Error al procesar la imagen.</span>`;
        console.error(err);
    }
}
