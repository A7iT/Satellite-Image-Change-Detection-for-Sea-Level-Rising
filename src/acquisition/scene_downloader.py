from pathlib import Path

import planetary_computer
from loguru import logger
from pystac_client import Client
from pystac_client.exceptions import APIError

from config.config import config

from src.acquisition.band_mapper import BandMapper
from src.io.raster import download_and_clip


class SceneDownloader:
    """
    Downloads Landsat scene assets from Microsoft Planetary Computer.

    Asset URLs are refreshed before every scene download because
    Planetary Computer signed URLs expire.
    """


    def __init__(self):

        self.catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,
        )



    # ==========================================================
    # GET FRESH STAC ASSETS
    # ==========================================================

    def _get_fresh_bands(
        self,
        scene,
    ):

        logger.info(
            f"Refreshing assets: {scene.id}"
        )


        try:

            search = self.catalog.search(

                collections=[
                    scene.collection
                ],

                ids=[
                    scene.id
                ],

            )


            items = search.item_collection()


        except APIError:

            logger.exception(
                f"Failed refreshing STAC item: {scene.id}"
            )

            raise



        if len(items) == 0:

            raise RuntimeError(
                f"Could not find STAC item: {scene.id}"
            )



        item = items[0]


        planetary_computer.sign_inplace(
            item
        )


        return BandMapper.get(
            item
        )



    # ==========================================================
    # DOWNLOAD SINGLE SCENE
    # ==========================================================

    def download(
        self,
        scene,
        aoi,
    ):


        if scene.raw_directory is None:

            raise RuntimeError(
                "Scene raw directory is not assigned."
            )



        bands = self._get_fresh_bands(
            scene
        )



        downloaded = []



        for band_name, band in bands.items():


            output_file = scene.raw_band(
                band_name
            )



            if output_file.exists():

                logger.debug(
                    f"Exists: {output_file.name}"
                )


                downloaded.append(
                    band_name
                )


                continue



            try:

                download_and_clip(

                    url=band.href,

                    output_path=output_file,

                    aoi=aoi,

                )



                if output_file.exists():

                    downloaded.append(
                        band_name
                    )



            except Exception:


                logger.error(

                    f"Band {band_name} failed for {scene.id}. "
                    f"Aborting scene."

                )

                raise RuntimeError(

                    f"Scene aborted: {scene.id}. "

                    f"Failed band: {band_name}"

                )



        required_bands = {

            "green",

            "nir",

            "qa_pixel",

        }



        missing = (

            required_bands -

            set(downloaded)

        )



        if missing:


            raise RuntimeError(

                f"Scene incomplete: {scene.id}. "

                f"Missing: {missing}"

            )



        logger.success(

            f"Scene downloaded successfully: {scene.id}"

        )


        return scene