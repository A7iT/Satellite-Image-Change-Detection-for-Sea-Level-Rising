from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Scene:
    """
    Represents a single Landsat scene.

    Stores only scene metadata.
    Remote asset URLs are fetched fresh during download.
    """

    id: str
    datetime: datetime
    cloud_cover: float
    platform: str
    collection: str

    raw_directory: Path | None = None
    processed_directory: Path | None = None


    @property
    def metadata_path(self) -> Path:
        return self.raw_directory / "metadata.json"


    @property
    def download_manifest_path(self) -> Path:
        return self.raw_directory / "download.json"


    def raw_band(self, band_name: str) -> Path:
        """
        Returns the path to a raw band.
        """

        if self.raw_directory is None:
            raise RuntimeError(
                "Raw directory has not been assigned."
            )

        return self.raw_directory / f"{band_name}.tif"


    def processed_band(self, band_name: str) -> Path:
        """
        Returns the path to a processed band.
        """

        if self.processed_directory is None:
            raise RuntimeError(
                "Processed directory has not been assigned."
            )

        return self.processed_directory / f"{band_name}.tif"


    def __str__(self) -> str:

        return (
            f"{self.platform:<12} | "
            f"{self.datetime.strftime('%Y-%m-%d')} | "
            f"Cloud: {self.cloud_cover:5.2f}% | "
            f"{self.id}"
        )