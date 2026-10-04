import geopandas as gpd
from shapely.geometry import Point, MultiPoint


class IntersectionFinder:
    """
    Finds shoreline intersections with transects.
    """


    def find(
        self,
        transects: gpd.GeoDataFrame,
        shoreline: gpd.GeoDataFrame,
        year: int,
    ) -> gpd.GeoDataFrame:
        """
        Find one representative shoreline intersection
        for every transect.
        """


        shoreline_union = shoreline.geometry.union_all()


        intersections = []



        for _, transect in transects.iterrows():


            intersection = transect.geometry.intersection(
                shoreline_union
            )


            if intersection.is_empty:

                continue



            point = None



            # --------------------------------------------------
            # Single intersection
            # --------------------------------------------------

            if intersection.geom_type == "Point":

                point = intersection



            # --------------------------------------------------
            # Multiple intersections
            # Select closest to transect midpoint
            # --------------------------------------------------

            elif intersection.geom_type == "MultiPoint":


                midpoint = transect.geometry.interpolate(
                    0.5,
                    normalized=True
                )


                point = min(

                    intersection.geoms,

                    key=lambda p: midpoint.distance(p)

                )



            # --------------------------------------------------
            # Handle geometry collections
            # --------------------------------------------------

            elif intersection.geom_type == "GeometryCollection":


                points = [

                    geom

                    for geom in intersection.geoms

                    if geom.geom_type == "Point"

                ]


                if len(points) > 0:


                    midpoint = transect.geometry.interpolate(
                        0.5,
                        normalized=True
                    )


                    point = min(

                        points,

                        key=lambda p: midpoint.distance(p)

                    )



            if point is not None:


                intersections.append(

                    {

                        "transect_id":
                            transect["transect_id"],


                        "year":
                            year,


                        "geometry":
                            point,

                    }

                )



        return gpd.GeoDataFrame(

            intersections,

            geometry="geometry",

            crs=shoreline.crs,

        )