from pathlib import Path

import numpy as np
import rasterio

from rasterio.warp import reproject, Resampling

from src.models.year_dataset import YearDataset


class CompositeLoader:
    """
    Loads processed rasters and aligns them
    into a common grid for compositing.

    Selects the best quality scenes before loading
    to reduce memory usage.
    """


    MAX_SCENES = 25


    def load(
        self,
        dataset: YearDataset,
        band: str,
    ) -> tuple[list[np.ndarray], dict]:


        images = []

        profile = None

        reference = None



        # -------------------------------------------------
        # Select scenes with lowest cloud cover
        # -------------------------------------------------

        scenes = sorted(
            dataset.scenes,
            key=lambda scene: scene.cloud_cover
        )


        scenes = scenes[
            :self.MAX_SCENES
        ]



        for scene in scenes:


            raster_path: Path = scene.processed_band(
                band
            )


            if not raster_path.exists():

                continue



            with rasterio.open(
                raster_path
            ) as src:


                image = src.read(1).astype(
                    np.float32
                )



                if profile is None:


                    profile = src.profile.copy()


                    reference = {

                        "shape": image.shape,

                        "transform": src.transform,

                        "crs": src.crs,

                    }


                    images.append(
                        image
                    )


                    continue



                # ---------------------------------------------
                # Align raster to reference grid
                # ---------------------------------------------

                aligned = np.empty(
                    reference["shape"],
                    dtype=np.float32,
                )



                reproject(

                    source=image,

                    destination=aligned,


                    src_transform=src.transform,

                    src_crs=src.crs,


                    dst_transform=reference["transform"],

                    dst_crs=reference["crs"],


                    resampling=Resampling.bilinear,

                )



                images.append(
                    aligned
                )



        if profile is None:


            raise RuntimeError(
                f"No processed rasters found for band '{band}'."
            )



        if len(images) == 0:


            raise RuntimeError(
                f"No valid images available for band '{band}'."
            )



        return images, profile