from pathlib import Path

import numpy as np
import rasterio


class RasterWriter:
    """
    Writes raster data to disk while preserving
    raster metadata.
    """

    def write(
        self,
        image: np.ndarray,
        profile: dict,
        output_path: Path,
    ) -> Path:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        profile = profile.copy()

        profile.update(
            dtype="float32",
            compress="lzw",
            nodata=np.nan,
        )

        with rasterio.open(
            output_path,
            "w",
            **profile,
        ) as dst:

            dst.write(image.astype(np.float32), 1)

        return output_path