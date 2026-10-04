from pathlib import Path

import pandas as pd
import rasterio
from rasterio.transform import rowcol

from config.config import config


class ChangeMetrics:
    """
    Computes shoreline change metrics between two shoreline years.
    """


    def compute(
        self,
        intersections,
        transects,
        reference_year: int,
        comparison_year: int,
        water_mask_path: Path,
    ) -> pd.DataFrame:


        reference = intersections[
            intersections["year"] == reference_year
        ]


        comparison = intersections[
            intersections["year"] == comparison_year
        ]


        years = comparison_year - reference_year


        rows = []


        with rasterio.open(water_mask_path) as src:
            water_mask = src.read(1)
            transform = src.transform


        common_ids = sorted(
            set(reference["transect_id"]).intersection(
                comparison["transect_id"]
            )
        )


        for transect_id in common_ids:


            reference_point = reference[
                reference["transect_id"] == transect_id
            ].iloc[0]


            comparison_point = comparison[
                comparison["transect_id"] == transect_id
            ].iloc[0]


            transect = transects[
                transects["transect_id"] == transect_id
            ].iloc[0]



            # =====================================================
            # Movement vector
            # =====================================================

            dx = (
                comparison_point.geometry.x
                -
                reference_point.geometry.x
            )


            dy = (
                comparison_point.geometry.y
                -
                reference_point.geometry.y
            )



            # =====================================================
            # Transect direction vector
            # =====================================================

            coords = list(
                transect.geometry.coords
            )


            tx = (
                coords[1][0]
                -
                coords[0][0]
            )


            ty = (
                coords[1][1]
                -
                coords[0][1]
            )



            # =====================================================
            # Signed shoreline movement
            # =====================================================

            dot_product = (

                dx * tx

                +

                dy * ty

            )


            distance = (

                reference_point.geometry.distance(

                    comparison_point.geometry

                )

            )

            row0, col0 = rowcol(transform, coords[0][0], coords[0][1])
            row1, col1 = rowcol(transform, coords[1][0], coords[1][1])

            val0 = water_mask[row0, col0] if 0 <= row0 < water_mask.shape[0] and 0 <= col0 < water_mask.shape[1] else 0
            val1 = water_mask[row1, col1] if 0 <= row1 < water_mask.shape[0] and 0 <= col1 < water_mask.shape[1] else 0

            if val1 == 1 and val0 != 1:
                if dot_product > 0:
                    nsm = -distance
                else:
                    nsm = distance
            elif val0 == 1 and val1 != 1:
                if dot_product < 0:
                    nsm = -distance
                else:
                    nsm = distance
            else:
                if dot_product < 0:
                    nsm = -distance
                else:
                    nsm = distance



            # =====================================================
            # End Point Rate
            # =====================================================

            epr = nsm / years



            # =====================================================
            # Direction classification
            #
            # NOTE:
            # Direction determined dynamically using water mask.
            # Positive movement = erosion
            # Negative movement = accretion
            # =====================================================

            if abs(nsm) <= config.stable_threshold:

                direction = "Stable"


            elif nsm > 0:

                direction = "Eroding"


            else:

                direction = "Accreting"



            rows.append(

                {

                    "transect_id": transect_id,

                    "reference_year": reference_year,

                    "comparison_year": comparison_year,

                    "years": years,

                    "NSM": nsm,

                    "Distance": distance,

                    "EPR": epr,

                    "Direction": direction,

                }

            )



        return pd.DataFrame(rows)