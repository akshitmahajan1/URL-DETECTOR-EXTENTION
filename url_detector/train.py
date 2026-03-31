import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .preprocessing import build_char_vocab, preprocess_dataframe
from .model_def import build_hybrid_model


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)


def main():
    # Using Kaggle malicious_phish.csv dataset: columns [url, type]
    csv_path = BASE_DIR / "data" / "malicious_phish.csv"
    df = pd.read_csv(csv_path)

    # Map multi-class "type" to binary label: benign = 0, others = 1
    # types typically include: benign, phishing, malware, defacement
    df["label"] = df["type"].apply(lambda t: 0 if str(t).lower() == "benign" else 1)

    url_column = "url"
    label_column = "label"  # 1 = malicious (phishing/malware/defacement), 0 = benign
    max_len = 200

    # Build character vocabulary from training URLs
    char2idx = build_char_vocab(df[url_column])
    vocab_size = max(char2idx.values()) + 1

    # Preprocess into sequences + manual features
    X_seq, X_manual, y = preprocess_dataframe(
        df=df,
        url_column=url_column,
        label_column=label_column,
        max_len=max_len,
        char2idx=char2idx,
    )

    # Scale manual features
    scaler = StandardScaler()
    X_manual_scaled = scaler.fit_transform(X_manual)

    X_seq_train, X_seq_val, X_manual_train, X_manual_val, y_train, y_val = train_test_split(
        X_seq, X_manual_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    model = build_hybrid_model(
        vocab_size=vocab_size,
        max_len=max_len,
        manual_feat_dim=X_manual.shape[1],
        embedding_dim=32,
        rnn_type="gru",
        use_conv=True,
    )

    model.summary()

    history = model.fit(
        x={"url_seq": X_seq_train, "manual_features": X_manual_train},
        y=y_train,
        validation_data=({"url_seq": X_seq_val, "manual_features": X_manual_val}, y_val),
        epochs=10,
        batch_size=256,
    )

    # Evaluation on validation set
    y_val_pred_proba = model.predict(
        {"url_seq": X_seq_val, "manual_features": X_manual_val}
    ).ravel()
    y_val_pred = (y_val_pred_proba >= 0.5).astype(int)

    print("\n=== Validation Classification Report ===")
    print(classification_report(y_val, y_val_pred, digits=4))

    print("\n=== Validation Confusion Matrix ===")
    print(confusion_matrix(y_val, y_val_pred))

    # ROC curve
    fpr, tpr, _ = roc_curve(y_val, y_val_pred_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(6, 6))
    plt.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - URL Phishing & Malware Detector")
    plt.legend(loc="lower right")
    roc_path = MODEL_DIR / "roc_curve.png"
    plt.tight_layout()
    plt.savefig(roc_path)
    plt.close()

    print(f"Saved ROC curve to {roc_path}")

    # Save model and preprocessing artifacts
    model_path = MODEL_DIR / "url_hybrid_model.h5"
    model.save(model_path)

    with open(MODEL_DIR / "char2idx.json", "w", encoding="utf-8") as f:
        json.dump(char2idx, f, ensure_ascii=False)

    joblib.dump({"scaler": scaler, "max_len": max_len}, MODEL_DIR / "preprocess.joblib")

    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
