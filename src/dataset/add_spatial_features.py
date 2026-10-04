from pathlib import Path

import geopandas as gpd
import pandas as pd
import numpy as np

from loguru import logger



# ==============================================================
# CONFIGURATION
# ==============================================================

BASE_DIR = Path("data")

DATASET_DIR = BASE_DIR / "dataset"

ANALYSIS_DIR = BASE_DIR / "analysis"

INPUT_FILE = (
    DATASET_DIR /
    "final_ml_dataset_v0_temporal.csv"
)

OUTPUT_FILE = (
    DATASET_DIR /
    "final_ml_dataset_v0b_spatial.csv"
)



# ==============================================================
# CURVATURE
# ==============================================================

def compute_curvature(
    p1,
    p2,
    p3
):

    try:

        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3


        # Fit circle through 3 points
        # Using determinant method
        
        A = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2


        if abs(A) < 1e-8:

            return 0.0


        A_sq = x1**2 + y1**2
        B_sq = x2**2 + y2**2
        C_sq = x3**2 + y3**2


        Cx = (A_sq * (y3 - y2) + B_sq * (y1 - y3) + C_sq * (y2 - y1)) / (2 * A)
        Cy = (A_sq * (x2 - x3) + B_sq * (x3 - x1) + C_sq * (x1 - x2)) / (2 * A)


        radius = np.sqrt(
            (x1 - Cx)**2 +
            (y1 - Cy)**2
        )


        if radius == 0:

            return 0.0


        curvature = 1.0 / radius


        # Determine sign: positive for convex (headland), negative for concave (bay)
        # Using cross product of vectors P1P2 and P2P3
        
        cross_product = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)


        if cross_product < 0:

            curvature = -curvature


        return curvature


    except Exception:

        return 0.0



# ==============================================================
# MAIN
# ==============================================================

def main():


    logger.info(
        "Loading dataset..."
    )


    if not INPUT_FILE.exists():

        logger.error(
            f"Input file not found: {INPUT_FILE}"
        )

        return


    df = pd.read_csv(INPUT_FILE)


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


    if not frames:

        logger.error(
            "No GeoPackages found"
        )

        return


    transects = gpd.GeoDataFrame(
        pd.concat(
            frames,
            ignore_index=True
        ),
        crs=frames[0].crs
    )


    # Sort transects by ID to ensure order for neighbors
    transects = transects.sort_values("transect_id").reset_index(drop=True)


    logger.info(
        f"Transects: {len(transects)}"
    )


    # Compute spatial features for each period
    
    periods = df[["reference_year", "comparison_year"]].drop_duplicates().values

    spatial_features_list = []

    for start_year, end_year in periods:

        logger.info(f"Processing period {start_year} -> {end_year}")

        period_df = df[
            (df["reference_year"] == start_year) & 
            (df["comparison_year"] == end_year)
        ].copy()


        # Get transects for this period
        
        period_transects = transects[
            (transects["reference_year"] == start_year) &
            (transects["comparison_year"] == end_year)
        ].copy()


        if period_transects.empty:

            logger.warning(
                f"No transects found for period {year_period}"
            )

            continue


        period_transects = period_transects.sort_values(
            "transect_id"
        ).reset_index(drop=True)


        for i, row in period_transects.iterrows():

            t_id = row["transect_id"]


            # Find 5 nearest neighbors by transect_id
            
            # Assuming transect_id is sequential or we can use index
            
            # Actually instructions say: "5 nearest transects (by transect_id proximity, i.e., transect_id ± 1 through ± 3)"
            
            # This means up to 6 neighbors? Or just 5 nearest. Let's just take indices max(0, i-3) to i+4 excluding i
            
            start_idx = max(0, i - 3)
            
            end_idx = min(len(period_transects), i + 4)
            

            neighbors = period_transects.iloc[start_idx:end_idx]
            
            neighbors = neighbors[
                neighbors["transect_id"] != t_id
            ]


            if not neighbors.empty:

                neighbor_epr_mean = neighbors["EPR"].mean()

                neighbor_epr_std = neighbors["EPR"].std()

            else:

                neighbor_epr_mean = np.nan

                neighbor_epr_std = np.nan


            
            # Curvature using midpoint of this transect and 2 immediate neighbors
            
            p2 = (
                row.geometry.centroid.x,
                row.geometry.centroid.y
            )


            p1 = p2
            p3 = p2


            if i > 0:

                p1 = (
                    period_transects.iloc[i-1].geometry.centroid.x,
                    period_transects.iloc[i-1].geometry.centroid.y
                )


            if i < len(period_transects) - 1:

                p3 = (
                    period_transects.iloc[i+1].geometry.centroid.x,
                    period_transects.iloc[i+1].geometry.centroid.y
                )


            if p1 == p2 or p2 == p3 or p1 == p3:

                curvature = 0.0

            else:

                curvature = compute_curvature(
                    p1,
                    p2,
                    p3
                )



            spatial_features_list.append({
                "transect_id": t_id,
                "reference_year": start_year,
                "comparison_year": end_year,
                "neighbor_epr_mean": neighbor_epr_mean,
                "neighbor_epr_std": neighbor_epr_std,
                "shoreline_curvature": curvature
            })



    features_df = pd.DataFrame(
        spatial_features_list
    )


    # Merge with original dataset
    
    result_df = pd.merge(
        df,
        features_df,
        on=["transect_id", "reference_year", "comparison_year"],
        how="left"
    )


    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    logger.success(
        "Spatial features added"
    )

    logger.success(
        f"Saved: {OUTPUT_FILE}"
    )

    logger.success(
        f"Shape: {result_df.shape}"
    )



if __name__ == "__main__":

    main()
