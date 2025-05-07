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

    const data = await res.json();
    document.getElementById("resultado").innerHTML = `
        <strong>Número detectado:</strong> ${data.numero}<br>
        <strong>En palabras:</strong> ${data.palabras}<br>
        <strong>¿Es par?:</strong> ${data.es_par ? "Sí" : "No"}<br>
        <strong>Factorial:</strong> ${data.factorial}<br>
        <strong>Dígitos primos:</strong> ${data.primos}
    `;
}
