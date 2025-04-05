document.getElementById("pdfForm").addEventListener("submit", function (event) {
    event.preventDefault();
    let fileInput = document.getElementById("pdfFile");
    let file = fileInput.files[0];
    if (!file) return alert("Please select a PDF file.");

    let formData = new FormData();
    formData.append("file", file);

    document.getElementById("pdfLoading").style.display = "block";

    fetch("/upload_pdf", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("pdfLoading").style.display = "none";
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            document.getElementById("summary").innerText = data.summary;
            document.getElementById("story").innerText = data.story;
        }
    })
    .catch(error => console.error("Error:", error));
});
