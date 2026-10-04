from shapely.geometry import LineString


class ShorelineSmoother:
    """
    Performs geometry cleanup on extracted shorelines.

    The current implementation preserves the original shoreline
    while ensuring valid geometries.

    Future smoothing algorithms can be added here without changing
    the pipeline architecture.
    """

    def smooth(
        self,
        shoreline: LineString,
    ) -> LineString:

        # Remove duplicate consecutive vertices
        coordinates = list(shoreline.coords)

        cleaned = []

        for coordinate in coordinates:

            if not cleaned or coordinate != cleaned[-1]:
                cleaned.append(coordinate)

        if len(cleaned) < 2:
            return shoreline

        return LineString(cleaned)