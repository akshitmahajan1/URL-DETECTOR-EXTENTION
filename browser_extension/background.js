// Background service worker for Manifest V3

const API_URL = "http://127.0.0.1:8080/predict"; // FastAPI backend
const RISK_THRESHOLD = 0.8;

async function checkUrlRisk(url, tabId) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    if (!response.ok) {
      // This will log if you are getting 404s or 500s
      console.error(`Backend Error: ${response.status} ${response.statusText}`);
      return;
    }
    // ... rest of logic
  } catch (err) {
    console.error("Network error - is the server running at localhost:8000?", err);
  }
}

// Use webNavigation to detect navigations and then query backend
chrome.webNavigation.onCommitted.addListener((details) => {
  if (details.frameId !== 0) {
    return; // only top-level frame
  }
  const url = details.url;
  const tabId = details.tabId;

  if (!url || !url.startsWith("http")) {
    return;
  }

  checkUrlRisk(url, tabId);
});
