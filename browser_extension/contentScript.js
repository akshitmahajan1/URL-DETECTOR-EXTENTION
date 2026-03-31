// Content script responsible for displaying warning overlays

function createWarningOverlay(url, riskScore) {
  if (document.getElementById("phish-detector-overlay")) {
    return; // already shown
  }

  const overlay = document.createElement("div");
  overlay.id = "phish-detector-overlay";
  overlay.style.position = "fixed";
  overlay.style.top = 0;
  overlay.style.left = 0;
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
  overlay.style.color = "#fff";
  overlay.style.zIndex = 2147483647;
  overlay.style.display = "flex";
  overlay.style.flexDirection = "column";
  overlay.style.alignItems = "center";
  overlay.style.justifyContent = "center";
  overlay.style.fontFamily = "Arial, sans-serif";

  const box = document.createElement("div");
  box.style.backgroundColor = "#b00020";
  box.style.padding = "20px 30px";
  box.style.borderRadius = "8px";
  box.style.boxShadow = "0 4px 12px rgba(0,0,0,0.4)";
  box.style.maxWidth = "600px";
  box.style.textAlign = "center";

  const title = document.createElement("h2");
  title.innerText = "Warning: Suspicious Site";
  title.style.marginBottom = "10px";

  const message = document.createElement("p");
  message.innerText = `The URL ${url} has a high risk score (${riskScore.toFixed(
    2
  )}). It may be phishing or malware-related.`;
  message.style.marginBottom = "20px";

  const proceedBtn = document.createElement("button");
  proceedBtn.innerText = "Proceed Anyway";
  proceedBtn.style.marginRight = "10px";
  proceedBtn.style.padding = "8px 16px";
  proceedBtn.style.border = "none";
  proceedBtn.style.borderRadius = "4px";
  proceedBtn.style.cursor = "pointer";

  const closeBtn = document.createElement("button");
  closeBtn.innerText = "Go Back";
  closeBtn.style.padding = "8px 16px";
  closeBtn.style.border = "none";
  closeBtn.style.borderRadius = "4px";
  closeBtn.style.cursor = "pointer";

  proceedBtn.onclick = () => {
    overlay.remove();
  };

  closeBtn.onclick = () => {
    overlay.remove();
    window.history.back();
  };

  const btnRow = document.createElement("div");
  btnRow.appendChild(proceedBtn);
  btnRow.appendChild(closeBtn);

  box.appendChild(title);
  box.appendChild(message);
  box.appendChild(btnRow);

  overlay.appendChild(box);
  document.body.appendChild(overlay);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SHOW_WARNING_OVERLAY") {
    const { url, riskScore } = message.payload;
    createWarningOverlay(url, riskScore);
  }
});
