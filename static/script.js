async function enviarImagen() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];
    if (!file) {
        alert("Por favor selecciona una imagen.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/predecir", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    document.getElementById("resultado").innerText = "Número detectado: " + data.numero;
}
