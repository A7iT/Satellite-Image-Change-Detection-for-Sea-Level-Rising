import time

from loguru import logger
from pystac_client import Client
from pystac_client.exceptions import APIError
import planetary_computer

from config.config import config

from src.models.scene import Scene


class LandsatSearcher:
    """
    Searches the Microsoft Planetary Computer STAC catalog
    for Landsat Collection 2 Level-2 imagery.
    """


    def __init__(self):

        self.catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,
        )


    def search(
        self,
        geometry,
        year,
    ) -> list[Scene]:


        # ------------------------------------------------------
        # Convert AOI polygon to bounding box
        #
        # STAC searches are faster using bbox.
        # Exact clipping happens later during download.
        # ------------------------------------------------------

        coordinates = geometry["coordinates"][0]


        xs = [
            point[0]
            for point in coordinates
        ]

        ys = [
            point[1]
            for point in coordinates
        ]


        bbox = [
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        ]



        search = self.catalog.search(
            collections=[
                config.landsat_collection
            ],

            bbox=bbox,

            datetime=f"{year}-01-01/{year}-12-31",

            query={
                "eo:cloud_cover": {
                    "lt": config.max_cloud_cover
                }
            },

            # Reduce STAC response size
            max_items=100,
            limit=50,
        )



        items = None



        # ------------------------------------------------------
        # Retry STAC query if Planetary Computer times out
        # ------------------------------------------------------

        for attempt in range(3):

            try:

                items = search.item_collection()

                break


            except APIError as e:

                logger.warning(
                    f"STAC search failed for {year} "
                    f"(attempt {attempt + 1}/3)"
                )


                if attempt == 2:

                    raise e


                wait_time = 10 * (attempt + 1)


                logger.warning(
                    f"Retrying in {wait_time} seconds..."
                )


                time.sleep(
                    wait_time
                )



        scenes = []


        for item in items:

            scene = Scene(
                id=item.id,

                datetime=item.datetime,

                cloud_cover=item.properties.get(
                    "eo:cloud_cover",
                    -1.0,
                ),

                platform=item.properties.get(
                    "platform",
                    "Unknown",
                ),

                collection=item.collection_id,
            )


            scenes.append(
                scene
            )



        scenes.sort(
            key=lambda scene: scene.datetime
        )


        logger.info(
            f"Found {len(scenes)} scenes for {year}"
        )


        return scenes