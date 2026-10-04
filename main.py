from pathlib import Path

import pandas as pd

from config.config import config
from config.paths import ANALYSIS, STATISTICS

from src.change_detection.change_processor import ChangeProcessor
from src.pipeline.year_pipeline import YearPipeline

from src.utils.aoi import load_aoi
from src.utils.banner import print_banner
from src.utils.logger import logger



# ==============================================================
# DATASET PATH
# ==============================================================

DATASET_DIR = Path(
    "data/dataset"
)

DATASET_DIR.mkdir(
    parents=True,
    exist_ok=True
)



# ==============================================================
# MAIN
# ==============================================================

def main() -> None:


    print_banner()



    # ----------------------------------------------------------
    # Load study area
    # ----------------------------------------------------------

    aoi = load_aoi()



    # ----------------------------------------------------------
    # Process yearly shoreline extraction
    # ----------------------------------------------------------

    pipeline = YearPipeline()


    for year in config.processing_years:

        pipeline.process(

            year=year,

            aoi=aoi,

        )



    logger.success(
        "All yearly shoreline processing completed."
    )



    # ----------------------------------------------------------
    # Create automatic year pairs from successful years
    # ----------------------------------------------------------

    all_years = sorted(config.processing_years)
    
    years = []
    for y in all_years:
        shoreline_path = ANALYSIS / str(y) / "shoreline.gpkg"
        if shoreline_path.exists():
            years.append(y)
        else:
            logger.warning(f"Year {y} has no shoreline output. Skipping for change detection.")

    periods = []


    for i in range(
        len(years) - 1
    ):

        periods.append(

            (
                years[i],
                years[i + 1],
            )

        )



    logger.info(
        f"Change detection periods: {periods}"
    )



    # ----------------------------------------------------------
    # Run change detection
    # ----------------------------------------------------------

    change_processor = ChangeProcessor()


    all_labels = []



    for reference_year, comparison_year in periods:



        logger.info("")

        logger.info(
            "=" * 70
        )

        logger.info(
            f"Comparing {reference_year} -> {comparison_year}"
        )

        logger.info(
            "=" * 70
        )



        result = change_processor.process(

            analysis_directory=ANALYSIS,

            reference_year=reference_year,

            comparison_year=comparison_year,

        )



        # ------------------------------------------------------
        # Save statistics summary
        # ------------------------------------------------------

        statistics_file = (

            STATISTICS /

            f"shoreline_statistics_{reference_year}_{comparison_year}.csv"

        )


        result.statistics.table.to_csv(

            statistics_file,

            index=False,

        )


        logger.info(
            f"Statistics saved: {statistics_file}"
        )



        # ------------------------------------------------------
        # Save transect change data
        # THIS IS THE LABEL DATA
        # ------------------------------------------------------

        transects = result.transects.copy()



        # Remove geometry before CSV export

        transects = transects.drop(

            columns=[

                "geometry"

            ],

            errors="ignore",

        )



        transects["reference_year"] = reference_year

        transects["comparison_year"] = comparison_year



        # Save individual period labels

        label_file = (

            STATISTICS /

            f"shoreline_labels_{reference_year}_{comparison_year}.csv"

        )


        transects.to_csv(

            label_file,

            index=False,

        )


        logger.info(
            f"Labels saved: {label_file}"
        )



        # Add to final dataset

        all_labels.append(

            transects

        )



        # ------------------------------------------------------
        # Save GeoPackage
        # ------------------------------------------------------

        gpkg_file = (

            ANALYSIS /

            f"shoreline_change_{reference_year}_{comparison_year}.gpkg"

        )


        result.transects.to_file(

            gpkg_file,

            driver="GPKG",

        )


        logger.info(
            f"Transects saved: {gpkg_file}"
        )



    # ----------------------------------------------------------
    # Merge all labeled samples
    # ----------------------------------------------------------

    final_dataset = pd.concat(

        all_labels,

        ignore_index=True,

    )



    dataset_file = (

        DATASET_DIR /

        "shoreline_change_labels.csv"

    )


    final_dataset.to_csv(

        dataset_file,

        index=False,

    )



    logger.success("")

    logger.success(
        "=" * 70
    )

    logger.success(
        "LABELED DATASET CREATED"
    )

    logger.success(
        "=" * 70
    )


    logger.success(
        f"Total samples: {len(final_dataset)}"
    )


    logger.success(
        f"Saved: {dataset_file}"
    )



    logger.success(
        "=" * 70
    )



if __name__ == "__main__":

    main()