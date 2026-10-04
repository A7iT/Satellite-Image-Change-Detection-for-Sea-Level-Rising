from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio

from rasterio.mask import mask
from rasterio.transform import rowcol
from shapely.geometry import mapping

from loguru import logger



# ==============================================================
# CONFIGURATION
# ==============================================================

BASE_DIR = Path("data")

ANALYSIS_DIR = BASE_DIR / "analysis"

INDICES_DIR = BASE_DIR / "indices"

OUTPUT_FILE = (
    BASE_DIR /
    "dataset" /
    "final_ml_dataset.csv"
)


BUFFER_DISTANCE = 60



# ==============================================================
# LOAD RASTERS
# ==============================================================

def load_indices(year):

    year_dir = INDICES_DIR / str(year)

    rasters = {}


    for name in [
        "ndwi",
        "ndvi",
        "mndwi"
    ]:

        path = (
            year_dir /
            f"{name}.tif"
        )


        if not path.exists():

            raise FileNotFoundError(
                f"Missing raster: {path}"
            )


        rasters[name] = rasterio.open(path)


    return rasters



def load_composite(year):

    band_names = ["blue", "green", "red", "nir", "swir1", "swir2"]
    rasters = {}
    
    for name in band_names:
        path = (
            BASE_DIR /
            "composites" /
            str(year) /
            f"{name}.tif"
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Missing composite band: {path}"
            )

        rasters[name] = rasterio.open(path)

    return rasters




# ==============================================================
# VALIDATE SPECTRAL VALUES
# ==============================================================

def clean_pixels(
    pixels,
    index_name
):

    pixels = pixels.astype(float)


    # Remove NaN
    pixels = pixels[
        ~pd.isna(pixels)
    ]


    # Remove invalid spectral values

    pixels = pixels[
        (pixels >= -1)
        &
        (pixels <= 1)
    ]


    return pixels



# ==============================================================
# EXTRACT BUFFER VALUE
# ==============================================================

def extract_value(
    raster,
    geometry,
    index_name
):

    try:

        values, _ = mask(

            raster,

            [
                mapping(
                    geometry
                )
            ],

            crop=True,

            filled=False

        )


        pixels = values[0].compressed()


        pixels = clean_pixels(

            pixels,

            index_name

        )


        if len(pixels) > 0:

            return {
                "mean": float(pixels.mean()),
                "var": float(pixels.var())
            }


        return nearest_valid_pixel(

            raster,

            geometry.centroid.x,

            geometry.centroid.y,

            index_name

        )


    except Exception:

        return None



def extract_bands(
    composite_rasters,
    geometry
):
    band_means = {}
    band_names = ["blue", "green", "red", "nir", "swir1", "swir2"]
    
    for name in band_names:
        try:
            raster = composite_rasters[name]
            values, _ = mask(
                raster,
                [mapping(geometry)],
                crop=True,
                filled=False
            )
            
            pixels = values[0].compressed()
            pixels = pixels[~pd.isna(pixels)]
            
            if len(pixels) > 0:
                band_means[name] = float(pixels.mean())
            else:
                band_means[name] = None
                
        except Exception:
            band_means[name] = None
            
    return band_means




# ==============================================================
# FALLBACK SEARCH
# ==============================================================

def nearest_valid_pixel(

    raster,

    x,

    y,

    index_name,

    radius=5

):

    try:

        row, col = rowcol(

            raster.transform,

            x,

            y

        )


        data = raster.read(1)


        height, width = data.shape



        candidates = []



        for r in range(

            max(0, row-radius),

            min(height, row+radius+1)

        ):


            for c in range(

                max(0, col-radius),

                min(width, col+radius+1)

            ):


                value = data[r, c]


                candidates.append(

                    value

                )



        candidates = clean_pixels(

            candidates,

            index_name

        )


        if len(candidates) > 0:

            return {
                "mean": float(candidates.mean()),
                "var": float(candidates.var())
            }


        return None


    except Exception:

        return None




# ==============================================================
# PROCESS TRANSECT
# ==============================================================

def process_transect(

    row,

    raster_cache

):


    start_year = int(

        row.reference_year

    )


    end_year = int(

        row.comparison_year

    )


    geometry = row.geometry.buffer(

        BUFFER_DISTANCE

    )



    result = {


        "transect_id":

            row.transect_id,


        "reference_year":

            start_year,


        "comparison_year":

            end_year,


        "years":

            row.years,


        "NSM":

            row.NSM,


        "Distance":

            row.Distance,


        "EPR":

            row.EPR,


        "Direction":

            row.Direction

    }



    for name in [

        "ndwi",

        "ndvi",

        "mndwi"

    ]:


        start_stats = extract_value(

            raster_cache[start_year][name],

            geometry,

            name

        )


        end_stats = extract_value(

            raster_cache[end_year][name],

            geometry,

            name

        )


        start_value = start_stats["mean"] if start_stats else None
        start_var = start_stats["var"] if start_stats else None

        end_value = end_stats["mean"] if end_stats else None
        end_var = end_stats["var"] if end_stats else None


        result[

            f"{name}_start"

        ] = start_value

        
        result[
            f"{name}_var_start"
        ] = start_var


        result[

            f"{name}_end"

        ] = end_value


        result[
            f"{name}_var_end"
        ] = end_var


        if (

            start_value is not None

            and

            end_value is not None

        ):

            result[

                f"{name}_change"

            ] = (

                end_value -

                start_value

            )

        else:

            result[

                f"{name}_change"

            ] = 0



    # Extract bands from composites
    
    start_bands = extract_bands(
        raster_cache[start_year]["composite"],
        geometry
    )
    
    end_bands = extract_bands(
        raster_cache[end_year]["composite"],
        geometry
    )
    
    for b in ["blue", "green", "red", "nir", "swir1", "swir2"]:
        result[f"{b}_start"] = start_bands[b]
        result[f"{b}_end"] = end_bands[b]
        
    # Band ratios
    
    if start_bands["green"] and start_bands["green"] != 0 and start_bands["nir"] is not None:
        result["nir_green_ratio_start"] = start_bands["nir"] / start_bands["green"]
    else:
        result["nir_green_ratio_start"] = None
        
    if end_bands["green"] and end_bands["green"] != 0 and end_bands["nir"] is not None:
        result["nir_green_ratio_end"] = end_bands["nir"] / end_bands["green"]
    else:
        result["nir_green_ratio_end"] = None
        
    if start_bands["nir"] and start_bands["nir"] != 0 and start_bands["swir1"] is not None:
        # User specified swir/nir, usually SWIR1 is used, let's use swir1.
        result["swir_nir_ratio_start"] = start_bands["swir1"] / start_bands["nir"]
    else:
        result["swir_nir_ratio_start"] = None
        
    if end_bands["nir"] and end_bands["nir"] != 0 and end_bands["swir1"] is not None:
        result["swir_nir_ratio_end"] = end_bands["swir1"] / end_bands["nir"]
    else:
        result["swir_nir_ratio_end"] = None


    return result



# ==============================================================
# MAIN
# ==============================================================

def main():


    logger.info(
        "Loading GeoPackages..."
    )


    files = sorted(

        ANALYSIS_DIR.glob(

            "shoreline_change_*.gpkg"

        )

    )


    frames = []



    for file in files:

        logger.info(

            f"Reading {file.name}"

        )


        frames.append(

            gpd.read_file(file)

        )



    transects = gpd.GeoDataFrame(

        pd.concat(

            frames,

            ignore_index=True

        ),

        crs=frames[0].crs

    )



    logger.info(

        f"Transects: {len(transects)}"

    )



    years = sorted(

        set(transects.reference_year)

        |

        set(transects.comparison_year)

    )



    raster_cache = {}



    for year in years:
        logger.info(
            f"Loading {year}"
        )

        raster_cache[year] = load_indices(
            year
        )

        raster_cache[year]["composite"] = load_composite(
            year
        )




    results = []



    for i, row in transects.iterrows():


        results.append(

            process_transect(

                row,

                raster_cache

            )

        )


        if i % 100 == 0:

            logger.info(

                f"Processed {i}/{len(transects)}"

            )



    df = pd.DataFrame(

        results

    )


    df.to_csv(

        OUTPUT_FILE,

        index=False

    )


    logger.success(

        "Dataset created"

    )


    logger.success(

        f"Saved: {OUTPUT_FILE}"

    )


    logger.success(

        f"Shape: {df.shape}"

    )



    for year in raster_cache:
        for key, value in raster_cache[year].items():
            if isinstance(value, dict):
                for band_raster in value.values():
                    band_raster.close()
            else:
                value.close()



if __name__ == "__main__":

    main()