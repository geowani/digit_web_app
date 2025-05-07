async function enviarImagen() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];
    if (!file) {
        alert("Por favor selecciona una imagen.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/analizar", {
        method: "POST",
        body: formData
    });
