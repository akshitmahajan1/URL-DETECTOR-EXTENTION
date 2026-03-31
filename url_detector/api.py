# import json
# from pathlib import Path

# import joblib
# import numpy as np
# from fastapi import FastAPI
# from pydantic import BaseModel
# import tensorflow as tf

# from .preprocessing import extract_manual_features, url_to_sequence


# BASE_DIR = Path(__file__).resolve().parent.parent
# MODEL_DIR = BASE_DIR / "models"


# class URLRequest(BaseModel):
#     url: str


# class URLResponse(BaseModel):
#     url: str
#     risk_score: float
#     label: str


# app = FastAPI(title="URL Phishing & Malware Detector")


# # Load model and preprocessing artifacts at startup
# model = tf.keras.models.load_model(MODEL_DIR / "url_hybrid_model.h5")

# with open(MODEL_DIR / "char2idx.json", "r", encoding="utf-8") as f:
#     char2idx = json.load(f)

# artifacts = joblib.load(MODEL_DIR / "preprocess.joblib")
# scaler = artifacts["scaler"]
# max_len = int(artifacts["max_len"])


# @app.post("/predict", response_model=URLResponse)
# async def predict(request: URLRequest):
#     url = request.url

#     seq = np.array([url_to_sequence(url, char2idx, max_len)], dtype="int32")
#     manual = np.array([extract_manual_features(url)], dtype="float32")
#     manual_scaled = scaler.transform(manual)

#     pred = model.predict({"url_seq": seq, "manual_features": manual_scaled})[0, 0]
#     risk_score = float(pred)
#     label = "Malicious" if risk_score >= 0.5 else "Benign"

#     return URLResponse(url=url, risk_score=risk_score, label=label)


# @app.get("/health")
# async def health():
#     return {"status": "ok"}


# # To run: uvicorn url_detector.api:app --reload

import json
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf

from .preprocessing import extract_manual_features, url_to_sequence


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


class URLRequest(BaseModel):
    url: str


class URLResponse(BaseModel):
    url: str
    risk_score: float
    label: str


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="URL Phishing & Malware Detector")

# Add this block right after 'app = FastAPI(...)'
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows the extension to talk to the backend
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"message": "API is online. Visit /docs to test the model."}

# Root endpoint (fix 404)
@app.get("/")
async def home():
    return {"message": "URL Phishing & Malware Detector API is running"}


# Load model and preprocessing artifacts at startup
model = tf.keras.models.load_model(MODEL_DIR / "url_hybrid_model.h5")

with open(MODEL_DIR / "char2idx.json", "r", encoding="utf-8") as f:
    char2idx = json.load(f)

artifacts = joblib.load(MODEL_DIR / "preprocess.joblib")
scaler = artifacts["scaler"]
max_len = int(artifacts["max_len"])


@app.post("/predict", response_model=URLResponse)
async def predict(request: URLRequest):
    url = request.url.strip()

    if not url or len(url) < 5:
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        seq = np.array([url_to_sequence(url, char2idx, max_len)], dtype="int32")
        manual = np.array([extract_manual_features(url)], dtype="float32")
        manual_scaled = scaler.transform(manual)

        pred = model(
            {"url_seq": seq, "manual_features": manual_scaled},
            training=False
        ).numpy()[0, 0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    risk_score = float(pred)
    label = "Malicious" if risk_score >= 0.5 else "Benign"

    return URLResponse(url=url, risk_score=risk_score, label=label)


@app.get("/health")
async def health():
    return {"status": "ok"}


# To run: uvicorn url_detector.api:app --reload