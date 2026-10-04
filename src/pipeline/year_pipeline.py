from pathlib import Path

from geopandas import GeoDataFrame
from loguru import logger

from src.acquisition.download_manager import DownloadManager
from src.acquisition.searcher import LandsatSearcher
from src.acquisition.year_downloader import YearDownloader
from src.compositing.annual_composite import AnnualCompositeBuilder
from src.indices.index_processor import IndexProcessor
from src.models.year_dataset import YearDataset
from src.preprocessing.year_processor import YearProcessor
from src.shoreline.shoreline_processor import ShorelineProcessor
from src.water.water_processor import WaterProcessor


class YearPipeline:
    """
    Executes the complete shoreline extraction workflow for a
    single processing year.

    Workflow
    --------
    Check Existing Results
        ↓
    Search
        ↓
    Prepare Directories
        ↓
    Download
        ↓
    Preprocess
        ↓
    Annual Composite
        ↓
    Spectral Indices
        ↓
    Water Extraction
        ↓
    Shoreline Extraction
    """


    def __init__(self):

        self.searcher = LandsatSearcher()

        self.download_manager = DownloadManager()
        self.downloader = YearDownloader()

        self.preprocessor = YearProcessor()
        self.composite_builder = AnnualCompositeBuilder()
        self.index_processor = IndexProcessor()
        self.water_processor = WaterProcessor()
        self.shoreline_processor = ShorelineProcessor()


        # ---------------------------------------------
        # Analysis output directory
        # ---------------------------------------------

        self.analysis_directory = Path(
            "data/analysis"
        )


    # =================================================
    # CHECK IF YEAR ALREADY PROCESSED
    # =================================================

    def _is_year_processed(
        self,
        year: int,
    ) -> bool:


        shoreline_file = (
            self.analysis_directory
            / str(year)
            / "shoreline.gpkg"
        )


        return shoreline_file.exists()



    def process(
        self,
        year: int,
        aoi: GeoDataFrame,
    ) -> YearDataset:


        logger.info("=" * 70)
        logger.info(f"Processing Year: {year}")
        logger.info("=" * 70)



        # -------------------------------------------------
        # Skip already completed years
        # -------------------------------------------------

        if self._is_year_processed(year):

            logger.success(
                f"Year {year} already processed. Skipping."
            )

            return YearDataset(
                year=year,
                scenes=[],
            )



        try:


            # -------------------------------------------------
            # Search Landsat scenes
            # -------------------------------------------------

            scenes = self.searcher.search(
                geometry=aoi.geometry.iloc[0].__geo_interface__,
                year=year,
            )


            dataset = YearDataset(
                year=year,
                scenes=scenes,
            )



            # -------------------------------------------------
            # Prepare directory structure
            # -------------------------------------------------

            dataset = self.download_manager.prepare_year(
                dataset,
            )



            # -------------------------------------------------
            # Download scenes
            # -------------------------------------------------

            dataset = self.downloader.download(
                dataset=dataset,
                aoi=aoi,
            )



            # -------------------------------------------------
            # Filter out incomplete scenes
            # -------------------------------------------------

            required = [
                "blue", "green", "red", 
                "nir", "swir1", "swir2", 
                "qa_pixel"
            ]

            complete_scenes = []

            for scene in dataset.scenes:

                missing = [
                    b for b in required
                    if not scene.raw_band(b).exists()
                ]

                if missing:

                    logger.warning(
                        f"Dropping incomplete scene: "
                        f"{scene.id} (missing: {missing})"
                    )

                else:

                    complete_scenes.append(scene)


            dropped = len(dataset.scenes) - len(complete_scenes)

            if dropped > 0:

                logger.info(
                    f"Dropped {dropped} incomplete scene(s), "
                    f"{len(complete_scenes)} remaining."
                )


            dataset.scenes = complete_scenes

            if len(dataset.scenes) == 0:
                raise RuntimeError(
                    f"No complete scenes remaining for year {year}. Aborting year."
                )



            # -------------------------------------------------
            # Preprocess scenes
            # -------------------------------------------------

            dataset = self.preprocessor.process(
                dataset,
            )



            # -------------------------------------------------
            # Build annual composite
            # -------------------------------------------------

            dataset = self.composite_builder.build(
                dataset,
            )



            # -------------------------------------------------
            # Calculate spectral indices
            # -------------------------------------------------

            dataset = self.index_processor.process(
                dataset,
            )



            # -------------------------------------------------
            # Extract water
            # -------------------------------------------------

            dataset = self.water_processor.process(
                dataset,
            )



            # -------------------------------------------------
            # Extract shoreline
            # -------------------------------------------------

            dataset = self.shoreline_processor.process(
                dataset,
            )



            logger.success(
                f"Year {year} processed successfully."
            )


            return dataset



        except Exception:


            logger.exception(
                f"Failed to process year {year}."
            )


            logger.warning(
                f"Skipping year {year} and continuing."
            )

            return YearDataset(
                year=year,
                scenes=[],
            )