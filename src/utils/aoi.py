import geopandas as gpd

from config.config import config
from config.paths import SHAPEFILES


def load_aoi():
    aoi = gpd.read_file(SHAPEFILES / config.aoi_filename)

    if str(aoi.crs) != config.geographic_crs:
        aoi = aoi.to_crs(config.geographic_crs)

    return aoi