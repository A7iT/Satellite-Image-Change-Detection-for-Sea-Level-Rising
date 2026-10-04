from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from loguru import logger



# ==========================================================
# PATHS
# ==========================================================

INPUT_DATASET = Path(
    "data/dataset/shoreline_change_ml_dataset.csv"
)

OUTPUT_DIR = Path(
    "data/ml"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info(
        "Loading ML dataset..."
    )


    df = pd.read_csv(
        INPUT_DATASET
    )


    logger.info(
        f"Dataset shape: {df.shape}"
    )


    # ======================================================
    # Separate features and label
    # ======================================================

    X = df.drop(
        columns=[
            "Direction"
        ]
    )


    y = df[
        "Direction"
    ]


    logger.info(
        f"Features: {X.shape[1]}"
    )


    logger.info(
        f"Classes:\n{y.value_counts()}"
    )



    # ======================================================
    # Encode labels
    # ======================================================

    encoder = LabelEncoder()


    y_encoded = encoder.fit_transform(
        y
    )


    logger.info(
        f"Label mapping:"
    )


    for label, value in zip(
        encoder.classes_,
        range(len(encoder.classes_))
    ):
        logger.info(
            f"{label} -> {value}"
        )



    joblib.dump(
        encoder,
        OUTPUT_DIR / "label_encoder.pkl"
    )



    # ======================================================
    # Stratified train-test split
    # ======================================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y_encoded,

        test_size=0.20,

        random_state=42,

        stratify=y_encoded

    )


    logger.info(
        f"Training samples: {len(X_train)}"
    )

    logger.info(
        f"Testing samples: {len(X_test)}"
    )



    # ======================================================
    # Save datasets
    # ======================================================

    X_train.to_csv(
        OUTPUT_DIR / "X_train.csv",
        index=False
    )


    X_test.to_csv(
        OUTPUT_DIR / "X_test.csv",
        index=False
    )


    pd.DataFrame(
        {
            "label": y_train
        }
    ).to_csv(
        OUTPUT_DIR / "y_train.csv",
        index=False
    )


    pd.DataFrame(
        {
            "label": y_test
        }
    ).to_csv(
        OUTPUT_DIR / "y_test.csv",
        index=False
    )



    # ======================================================
    # Save feature names
    # ======================================================

    pd.DataFrame(
        {
            "feature": X.columns
        }
    ).to_csv(
        OUTPUT_DIR / "feature_names.csv",
        index=False
    )



    logger.success(
        "ML dataset preparation completed"
    )


    logger.success(
        f"Saved files in: {OUTPUT_DIR}"
    )



if __name__ == "__main__":
    main()