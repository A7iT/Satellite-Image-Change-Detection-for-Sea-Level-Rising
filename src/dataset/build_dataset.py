"""
Unified Dataset Build Pipeline.

Runs all dataset enrichment steps in sequence, passing
DataFrames in memory to avoid intermediate file I/O.

Steps:
    1. Satellite features (spectral indices + band values)
    2. Location features (UTM coordinates)
    3. Temporal features (rolling, cumulative, trend)
    4. Spatial features (neighbor EPR, curvature)
    5. Missing value handling (temporal → spatial → median)
    6. Cloud features (metadata-based)
    7. DEM features (elevation)
    8. Final ML dataset (drop leakage columns)

Usage:
    python -m src.dataset.build_dataset
    # or
    python src/dataset/build_dataset.py
"""

import sys
from pathlib import Path

# Add project root to path so 'src' can be resolved when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from loguru import logger



# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path("data")

DATASET_DIR = BASE_DIR / "dataset"

ANALYSIS_DIR = BASE_DIR / "analysis"

STATISTICS_DIR = BASE_DIR / "statistics"


FINAL_OUTPUT = (
    DATASET_DIR /
    "shoreline_change_master_dataset.csv"
)

ML_OUTPUT = (
    DATASET_DIR /
    "shoreline_change_ml_dataset.csv"
)



# ==========================================================
# STEP RUNNERS
# ==========================================================

def step_1_satellite_features():
    """
    Run satellite feature extraction.
    Produces: data/dataset/final_ml_dataset.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 1: Satellite Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.add_satellite_features import main

    main()

    return pd.read_csv(
        DATASET_DIR / "final_ml_dataset.csv"
    )



def step_2_location_features():
    """
    Run location feature extraction.
    Produces: data/dataset/shoreline_change_with_location.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 2: Location Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.create_location_features import main

    main()



def step_3_temporal_features():
    """
    Run temporal feature engineering.
    Produces: data/dataset/final_ml_dataset_v0_temporal.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 3: Temporal Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.add_temporal_features import main

    main()



def step_4_spatial_features():
    """
    Run spatial neighborhood feature extraction.
    Produces: data/dataset/final_ml_dataset_v0b_spatial.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 4: Spatial Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.add_spatial_features import main

    main()



def step_5_missing_values():
    """
    Handle missing values (temporal + spatial + median fallback).
    Produces: data/dataset/final_ml_dataset_v1_missing_handled.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 5: Missing Value Handling"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.handle_missing_values import main

    main()



def step_6_cloud_features():
    """
    Add cloud cover metadata features.
    Produces: data/dataset/final_ml_dataset_v2_cloud_features.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 6: Cloud Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.add_cloud_features import main

    main()



def step_7_dem_features():
    """
    Add DEM-derived elevation features.
    Produces: data/dataset/final_ml_dataset_v3_dem_features.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 7: DEM Features"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.add_dem_features import main

    main()



def step_8_create_ml_dataset():
    """
    Create final ML dataset by removing leakage columns.
    Produces: data/dataset/final_ml_training_dataset.csv
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 8: Create ML Dataset"
    )

    logger.info(
        "=" * 70
    )

    from src.dataset.create_ml_training_dataset import main

    main()



def step_9_save_master():
    """
    Copy the DEM-enriched dataset as the master dataset
    and create the ML-ready version.
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "STEP 9: Save Master & ML Datasets"
    )

    logger.info(
        "=" * 70
    )


    # Master dataset (all columns)

    dem_file = (
        DATASET_DIR /
        "final_ml_dataset_v3_dem_features.csv"
    )

    if dem_file.exists():

        df = pd.read_csv(dem_file)

        df.to_csv(
            FINAL_OUTPUT,
            index=False,
        )

        logger.success(
            f"Master dataset: {FINAL_OUTPUT}"
        )

        logger.success(
            f"Shape: {df.shape}"
        )


    # ML dataset (no leakage columns)

    ml_file = (
        DATASET_DIR /
        "final_ml_training_dataset.csv"
    )

    if ml_file.exists():

        df_ml = pd.read_csv(ml_file)

        df_ml.to_csv(
            ML_OUTPUT,
            index=False,
        )

        logger.success(
            f"ML dataset: {ML_OUTPUT}"
        )

        logger.success(
            f"Shape: {df_ml.shape}"
        )

        logger.info(
            f"Features ({len(df_ml.columns)}):"
        )

        for col in df_ml.columns:

            logger.info(
                f"  {col}"
            )



# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("")
    logger.info("=" * 70)
    logger.info("UNIFIED DATASET BUILD PIPELINE")
    logger.info("=" * 70)
    logger.info("")


    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # Run all steps in order

    step_1_satellite_features()

    step_2_location_features()

    step_3_temporal_features()

    step_4_spatial_features()

    step_5_missing_values()

    step_6_cloud_features()

    step_7_dem_features()

    step_8_create_ml_dataset()

    step_9_save_master()


    logger.success("")
    logger.success("=" * 70)
    logger.success("DATASET BUILD COMPLETE")
    logger.success("=" * 70)
    logger.success("")



if __name__ == "__main__":

    main()

