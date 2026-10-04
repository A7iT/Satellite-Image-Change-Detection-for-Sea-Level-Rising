from pathlib import Path

import geopandas as gpd


class ShorelineLoader:
    """
    Loads shoreline vectors from one or more years.
    """

    def load(
        self,
        analysis_directory: Path,
        year: int,
    ) -> gpd.GeoDataFrame:
        """
        Load a shoreline vector for a specific year.

        Parameters
        ----------
        analysis_directory : Path
            Root analysis directory.

        year : int
            Year to load.

        Returns
        -------
        GeoDataFrame
            Shoreline geometry.
        """

        shoreline_path = (
            analysis_directory
            / str(year)
            / "shoreline.gpkg"
        )

        shoreline = gpd.read_file(
            shoreline_path,
            layer="shoreline",
        )

        shoreline["year"] = year

        return shoreline

    def load_multiple(
        self,
        analysis_directory: Path,
        years: list[int],
    ) -> dict[int, gpd.GeoDataFrame]:
        """
        Load shorelines for multiple years.

        Parameters
        ----------
        analysis_directory : Path
            Root analysis directory.

        years : list[int]
            Years to load.

        Returns
        -------
        dict
            Dictionary of year -> shoreline GeoDataFrame.
        """

        shorelines = {}

        for year in years:

            shorelines[year] = self.load(
                analysis_directory,
                year,
            )

        return shorelines