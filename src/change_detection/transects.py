import math

import geopandas as gpd
from shapely.geometry import LineString


class TransectGenerator:
    """
    Generates transects perpendicular to a baseline.
    """


    def generate(
        self,
        baseline: LineString,
        spacing: float = 100.0,
        length: float = 300.0,
    ) -> gpd.GeoDataFrame:
        """
        Parameters
        ----------
        baseline : LineString
            Baseline geometry.

        spacing : float
            Distance between transects (meters).

        length : float
            Total transect length (meters).

        Returns
        -------
        GeoDataFrame
            Transect geometries with unique IDs.
        """


        transects = []

        distance = 0.0

        transect_id = 0



        while distance <= baseline.length:


            # -----------------------------------------------------
            # Sample point on baseline
            # -----------------------------------------------------

            point = baseline.interpolate(
                distance
            )



            # -----------------------------------------------------
            # Local baseline direction
            # -----------------------------------------------------

            next_distance = min(
                distance + 1,
                baseline.length,
            )


            next_point = baseline.interpolate(
                next_distance
            )


            dx = next_point.x - point.x

            dy = next_point.y - point.y



            angle = math.atan2(
                dy,
                dx,
            )



            # -----------------------------------------------------
            # Perpendicular angle
            # -----------------------------------------------------

            perpendicular = angle + math.pi / 2


            half = length / 2



            x1 = (
                point.x
                +
                half * math.cos(perpendicular)
            )


            y1 = (
                point.y
                +
                half * math.sin(perpendicular)
            )


            x2 = (
                point.x
                -
                half * math.cos(perpendicular)
            )


            y2 = (
                point.y
                -
                half * math.sin(perpendicular)
            )



            transects.append(
                {
                    "transect_id": transect_id,

                    "geometry": LineString(
                        [
                            (x1, y1),
                            (x2, y2),
                        ]
                    ),
                }
            )



            transect_id += 1


            distance += spacing



        return gpd.GeoDataFrame(
            transects,
            geometry="geometry",
            crs=None,
        )