from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge


class BaselineGenerator:
    """
    Generates a baseline from a shoreline.

    The baseline is created by offsetting the shoreline by
    a fixed distance.
    """

    def generate(
        self,
        shoreline,
        offset_distance: float = 100.0,
    ) -> LineString:
        """
        Parameters
        ----------
        shoreline : GeoDataFrame
            Shoreline geometry.

        offset_distance : float
            Offset distance in map units (meters).

        Returns
        -------
        LineString
            Baseline geometry.
        """

        # ---------------------------------------------------------
        # Merge shoreline segments
        # ---------------------------------------------------------

        merged = linemerge(
            shoreline.geometry.unary_union
        )

        if isinstance(merged, MultiLineString):

            merged = max(
                merged.geoms,
                key=lambda line: line.length,
            )

        # ---------------------------------------------------------
        # Offset shoreline
        # ---------------------------------------------------------

        baseline = merged.parallel_offset(
            distance=offset_distance,
            side="left",
            join_style=2,
        )

        if isinstance(
            baseline,
            MultiLineString,
        ):

            baseline = max(
                baseline.geoms,
                key=lambda line: line.length,
            )

        return baseline