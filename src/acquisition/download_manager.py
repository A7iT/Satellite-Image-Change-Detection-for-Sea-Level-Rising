from config.paths import (
    ANALYSIS,
    COMPOSITES,
    INDICES,
    PROCESSED,
    RAW,
    STATISTICS,
    VISUALIZATION,
    WATER,
)

from src.models.year_dataset import YearDataset


class DownloadManager:
    """
    Prepares the directory structure for a processing year.
    """

    def prepare_year(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        # ---------------------------------------------------------
        # Year Directories
        # ---------------------------------------------------------

        raw_year_directory = RAW / str(dataset.year)
        processed_year_directory = PROCESSED / str(dataset.year)
        composite_year_directory = COMPOSITES / str(dataset.year)
        indices_year_directory = INDICES / str(dataset.year)
        water_year_directory = WATER / str(dataset.year)
        analysis_year_directory = ANALYSIS / str(dataset.year)
        statistics_year_directory = STATISTICS / str(dataset.year)
        visualization_year_directory = VISUALIZATION / str(dataset.year)

        year_directories = [
            raw_year_directory,
            processed_year_directory,
            composite_year_directory,
            indices_year_directory,
            water_year_directory,
            analysis_year_directory,
            statistics_year_directory,
            visualization_year_directory,
        ]

        for directory in year_directories:

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        dataset.raw_directory = raw_year_directory
        dataset.processed_directory = processed_year_directory
        dataset.composite_directory = composite_year_directory
        dataset.indices_directory = indices_year_directory
        dataset.water_directory = water_year_directory
        dataset.analysis_directory = analysis_year_directory
        dataset.statistics_directory = statistics_year_directory
        dataset.visualization_directory = visualization_year_directory

        # ---------------------------------------------------------
        # Scene Directories
        # ---------------------------------------------------------

        for scene in dataset.scenes:

            raw_scene_directory = raw_year_directory / scene.id
            processed_scene_directory = processed_year_directory / scene.id

            raw_scene_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            processed_scene_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            scene.raw_directory = raw_scene_directory
            scene.processed_directory = processed_scene_directory

        return dataset