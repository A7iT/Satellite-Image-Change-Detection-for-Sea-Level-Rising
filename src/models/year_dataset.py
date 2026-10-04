from dataclasses import dataclass
from pathlib import Path

from src.models.scene import Scene


@dataclass
class YearDataset:
    """
    Represents all data and derived products associated
    with a single processing year.
    """

    # ---------------------------------------------------------
    # Dataset Information
    # ---------------------------------------------------------

    year: int
    scenes: list[Scene]

    # ---------------------------------------------------------
    # Processing Directories
    # ---------------------------------------------------------

    raw_directory: Path | None = None
    processed_directory: Path | None = None

    composite_directory: Path | None = None
    indices_directory: Path | None = None
    water_directory: Path | None = None
    analysis_directory: Path | None = None
    statistics_directory: Path | None = None
    visualization_directory: Path | None = None

    # ---------------------------------------------------------
    # Processing Status
    # ---------------------------------------------------------

    download_complete: bool = False