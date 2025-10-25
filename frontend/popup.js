const saveBtn = document.getElementById("saveBtn");
const output = document.getElementById("output");

// Save risk level to Chrome local storage
saveBtn.addEventListener("click", () => {
    const risk = document.getElementById("riskLevel").value;
    chrome.storage.local.set({ riskLevel: risk }, () => {
        output.textContent = `Risk level saved: ${risk}`;
    });
});

// Load risk level on popup open
chrome.storage.local.get(["riskLevel"], (result) => {
    if(result.riskLevel){
        document.getElementById("riskLevel").value = result.riskLevel;
        output.textContent = `Current risk level: ${result.riskLevel}`;
    }
});
