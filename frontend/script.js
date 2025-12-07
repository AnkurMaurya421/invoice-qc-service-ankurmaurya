const API_BASE = "http://127.0.0.1:8000";
let resultsCache = [];  // store all results


// Validate PDFs
// ----------------------
async function uploadPDFs() {
    const files = document.getElementById("pdfInput").files;
    if (!files.length) return alert("Select at least one PDF");

    const formData = new FormData();
    [...files].forEach(file => formData.append("files", file));

    const res = await fetch(`${API_BASE}/extract-and-validate-pdfs`, { method: "POST", body: formData });
    const data = await res.json();
    console.log("API response:", data);

    resultsCache = data.validation_results;
    render(resultsCache);
}


// Validate JSON
async function validateJSON() {
    let raw = document.getElementById("jsonInput").value.trim();
    if (!raw) return alert("Paste JSON first.");

    let parsed;
    try { parsed = JSON.parse(raw); }
    catch { return alert("Invalid JSON"); }

    const res = await fetch(`${API_BASE}/validate-json`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed)
    });

    const data = await res.json();
    resultsCache = data.results;
    render(resultsCache);
}

// Render Table
function render(list) {
    const tbody = document.querySelector("#resultsTable tbody");
    tbody.innerHTML = "";

    list.forEach(item => {
        const row = `
            <tr>
                <td>${item.invoice_id ?? item.filename}</td>
                <td class="${item.valid ? "status-valid" : "status-invalid"}">
                    ${item.valid ? "VALID" : "INVALID"}
                </td>
                <td>${item.error || ""}</td>
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
    });
}


// Filter invalid only                 
function filterResults() {
    const showInvalidOnly = document.getElementById("filterInvalid").checked;
    const filtered = showInvalidOnly ? resultsCache.filter(r => !r.valid) : resultsCache;
    render(filtered);
}
