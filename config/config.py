from dataclasses import dataclass


@dataclass(frozen=True)
class Config:

    # ==========================================================
    # Study Period
    # ==========================================================

    start_year: int = 2000
    end_year: int = 2025

    processing_years: tuple[int, ...] = tuple(
        range(2000, 2026)
    )

    reference_year: int = 2000
    comparison_year: int = 2025

    # ==========================================================
    # AOI
    # ==========================================================

    aoi_filename: str = "CAZ.shp"

    # ==========================================================
    # Coordinate Systems
    # ==========================================================

    geographic_crs: str = "EPSG:4326"
    projected_crs: str = "EPSG:32646"

    # ==========================================================
    # Landsat
    # ==========================================================

    landsat_collection: str = "landsat-c2-l2"
    max_cloud_cover: int = 30

    # ==========================================================
    # Processing
    # ==========================================================

    pixel_size: int = 30
    composite_method: str = "median"

    # ==========================================================
    # NDWI
    # ==========================================================

    ndwi_method: str = "McFeeters"
    use_otsu: bool = True

    # ==========================================================
    # Morphology
    # ==========================================================

    min_water_pixels: int = 25

    stable_threshold: float = 15.0  # meters (half a Landsat pixel)


config = Config()