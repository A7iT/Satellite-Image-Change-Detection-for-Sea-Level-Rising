from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loguru import logger



# ==========================================================
# PATH
# ==========================================================

DATASET = Path(
    "data/dataset/final_ml_dataset_v3_dem_features.csv"
)


OUTPUT_DIR = Path(
    "outputs/dataset_audit"
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
        "Loading dataset..."
    )


    df = pd.read_csv(
        DATASET
    )


    print("\n==============================")
    print("DATASET SHAPE")
    print("==============================")

    print(df.shape)



    # ------------------------------------------------------
    # Missing values
    # ------------------------------------------------------

    print("\n==============================")
    print("MISSING VALUES")
    print("==============================")

    print(
        df.isna().sum()
    )



    # ------------------------------------------------------
    # Labels
    # ------------------------------------------------------

    print("\n==============================")
    print("LABEL DISTRIBUTION")
    print("==============================")

    print(
        df["Direction"].value_counts()
    )

    print(
        df["Direction"].value_counts(normalize=True)
    )



    # ------------------------------------------------------
    # Potential leakage
    # ------------------------------------------------------

    print("\n==============================")
    print("POSSIBLE LABEL LEAKAGE")
    print("==============================")


    leakage_features = [
        "NSM",
        "Distance",
        "EPR"
    ]


    for col in leakage_features:

        print(
            col,
            "correlation with label unavailable (categorical)"
        )

        print(
            df.groupby("Direction")[col].describe()
        )



    # ------------------------------------------------------
    # Numeric correlations
    # ------------------------------------------------------

    print("\n==============================")
    print("CORRELATION")
    print("==============================")


    numeric = df.select_dtypes(
        include=np.number
    )


    corr = numeric.corr()


    plt.figure(
        figsize=(14,12)
    )


    sns.heatmap(
        corr,
        cmap="coolwarm",
        center=0
    )


    plt.title(
        "Feature Correlation"
    )


    plt.tight_layout()


    plt.savefig(
        OUTPUT_DIR / "correlation.png",
        dpi=300
    )


    plt.close()



    # ------------------------------------------------------
    # Feature list
    # ------------------------------------------------------

    print("\n==============================")
    print("FEATURES")
    print("==============================")


    for c in df.columns:

        print(c)



    logger.success(
        "Dataset audit completed"
    )


if __name__ == "__main__":
    main()