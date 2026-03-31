# URL Phishing & Malware Detector

FastAPI backend + Chrome extension that use a **hybrid deep learning model** to flag malicious URLs (phishing, malware, defacement) in real time. The model looks at both the raw URL string (character‑level sequence) and simple statistical features (length, digits, special characters, entropy) to produce a risk score between 0 and 1. The browser extension sends every visited URL to this local API and, when the score is high, shows a full‑screen warning overlay so the user can back out before interacting with a suspicious site.

---

## Architecture

- **Backend (url_detector/api.py)**
	- FastAPI service exposing `POST /predict` and `GET /health`.
	- Loads a trained Keras model (`models/url_hybrid_model.h5`) plus preprocessing artifacts (`char2idx.json`, `preprocess.joblib`).

- **Model**
	- Character-level URL sequence (embedding + Conv1D/GRU).
	- Manual features: URL length, digit count, special char count, Shannon entropy.
	- Outputs a risk score in `[0, 1]` and label: `Malicious` if score ≥ 0.5, else `Benign`.

- **Chrome Extension (browser_extension/)**
	- Background script watches navigation events and calls the local API at `http://127.0.0.1:8080/predict`.
	- Content script injects a full-screen warning overlay on high‑risk URLs.

---

## Setup & Run

From the project root:

```bash
pip install -r requirements.txt
python -m url_detector.train        # only if models/ is empty
uvicorn url_detector.api:app --reload --port 8080
```

Key endpoints:

- `POST /predict` – body: `{ "url": "https://example.com" }`
- `GET /health` – returns `{ "status": "ok" }`

Example request:

```bash
curl -X POST "http://127.0.0.1:8080/predict" \
	-H "Content-Type: application/json" \
	-d '{"url": "https://example.com/login"}'
```

---

## Using the Chrome Extension

1. Make sure the API is running on `http://127.0.0.1:8080`.
2. In Chrome, open `chrome://extensions/` and enable **Developer mode**.
3. Click **Load unpacked** and select the `browser_extension/` folder.
4. Browse normally; high‑risk URLs will trigger the warning overlay.

---

## Project Layout

```text
browser_extension/   # Chrome extension scripts + manifest
data/                # malicious_phish.csv dataset
models/              # trained model + preprocess artifacts
url_detector/        # API, training script, preprocessing, model
requirements.txt     # Python dependencies
```
