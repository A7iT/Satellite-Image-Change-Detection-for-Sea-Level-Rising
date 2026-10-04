from pathlib import Path
import json

import pandas as pd

from loguru import logger



# ==========================================================
# PATHS
# ==========================================================

INPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v1_missing_handled.csv"
)


OUTPUT_FILE = Path(
    "data/dataset/final_ml_dataset_v2_cloud_features.csv"
)


RAW_DIR = Path(
    "data/raw"
)



# ==========================================================
# CLOUD METADATA
# ==========================================================

def get_year_cloud_cover(year):

    """
    Find average cloud cover for a given year
    from Landsat metadata files.
    """

    year_dir = RAW_DIR / str(year)


    metadata_files = list(
        year_dir.rglob(
            "metadata.json"
        )
    )


    if len(metadata_files) == 0:

        logger.warning(
            f"No metadata found for {year}"
        )

        return None



    cloud_values = []


    for file in metadata_files:

        try:

            with open(file) as f:

                data = json.load(f)


            if "cloud_cover" in data:

                cloud_values.append(
                    float(
                        data["cloud_cover"]
                    )
                )


        except Exception as e:

            logger.warning(
                f"Failed reading {file}: {e}"
            )



    if len(cloud_values) == 0:

        return None



    return sum(cloud_values) / len(cloud_values)



# ==========================================================
# MAIN
# ==========================================================

def main():


    logger.info(
        "Loading dataset..."
    )


    df = pd.read_csv(
        INPUT_FILE
    )


    logger.info(
        f"Original shape: {df.shape}"
    )


    years = sorted(
        set(
            df["reference_year"]
        )
        |
        set(
            df["comparison_year"]
        )
    )


    cloud_data = {}



    for year in years:


        logger.info(
            f"Reading cloud metadata for {year}"
        )


        cloud_data[year] = get_year_cloud_cover(

            year

        )


        logger.info(

            f"{year} cloud cover: "
            f"{cloud_data[year]}"

        )



    # Add cloud features

    df["cloud_start"] = (

        df["reference_year"]
        .map(
            cloud_data
        )

    )


    df["cloud_end"] = (

        df["comparison_year"]
        .map(
            cloud_data
        )

    )



    # Handle missing cloud values

    for col in [

        "cloud_start",

        "cloud_end"

    ]:


        if df[col].isna().sum() > 0:


            median = df[col].median()


            df[col] = df[col].fillna(

                median

            )


            logger.info(

                f"{col}: filled missing with {median}"

            )



    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True

    )



    df.to_csv(

        OUTPUT_FILE,

        index=False

    )



    logger.success(

        "Cloud feature generation complete"

    )


    logger.success(

        f"Saved: {OUTPUT_FILE}"

    )


    logger.success(

        f"Final shape: {df.shape}"

    )


    logger.info(

        df.head()

    )



if __name__ == "__main__":

    main()