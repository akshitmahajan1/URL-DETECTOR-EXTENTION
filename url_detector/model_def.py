from typing import Dict, Tuple

import tensorflow as tf
from tensorflow.keras import Input, Model
from tensorflow.keras.layers import (
    LSTM,
    GRU,
    Conv1D,
    Dense,
    Dropout,
    Embedding,
    GlobalMaxPooling1D,
    Concatenate,
)


def build_hybrid_model(
    vocab_size: int,
    max_len: int,
    manual_feat_dim: int = 4,
    embedding_dim: int = 32,
    rnn_type: str = "gru",
    use_conv: bool = True,
) -> Model:
    # Character sequence branch
    seq_input = Input(shape=(max_len,), name="url_seq")
    x = Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        input_length=max_len,
        mask_zero=True,
        name="char_embedding",
    )(seq_input)

    if use_conv:
        x = Conv1D(filters=64, kernel_size=3, activation="relu", name="conv1d")(x)
        x = GlobalMaxPooling1D(name="global_max_pool")(x)
    else:
        if rnn_type.lower() == "lstm":
            x = LSTM(64, name="lstm")(x)
        else:
            x = GRU(64, name="gru")(x)

    # Manual feature branch
    manual_input = Input(shape=(manual_feat_dim,), name="manual_features")
    y = Dense(32, activation="relu", name="manual_dense")(manual_input)

    # Concatenate branches
    combined = Concatenate(name="concat")([x, y])
    z = Dense(64, activation="relu", name="dense_1")(combined)
    z = Dropout(0.5, name="dropout")(z)
    output = Dense(1, activation="sigmoid", name="risk_score")(z)

    model = Model(inputs=[seq_input, manual_input], outputs=output, name="url_hybrid_model")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model
