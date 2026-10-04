from pathlib import Path
import pandas as pd
from loguru import logger


# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v3_dem_features.csv"
)


OUTPUT_FILE = Path(
    "data/dataset/final_ml_training_dataset.csv"
)



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info(
        "Loading final dataset..."
    )


    df = pd.read_csv(
        INPUT_FILE
    )


    logger.info(
        f"Original shape: {df.shape}"
    )


    # ------------------------------------------------------
    # Remove leakage / ID columns
    # ------------------------------------------------------

    remove_columns = [

        "transect_id",

        # label-generation features
        "NSM",
        "Distance",
        "EPR",

        # future time information
        "comparison_year"

    ]


    df_ml = df.drop(
        columns=remove_columns
    )


    logger.info(
        "Removed leakage columns:"
    )

    for col in remove_columns:

        logger.info(
            col
        )


    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    df_ml.to_csv(
        OUTPUT_FILE,
        index=False
    )


    logger.success(
        "ML training dataset created"
    )


    logger.success(
        f"Saved: {OUTPUT_FILE}"
    )


    logger.success(
        f"Final shape: {df_ml.shape}"
    )


    print("\nColumns:")
    
    for c in df_ml.columns:
        print(c)



if __name__ == "__main__":
    main()