import numpy as np
import rasterio
from pathlib import Path


class QAMask:
    """
    Creates a valid-pixel mask from the Landsat
    Collection 2 QA_PIXEL band.
    """

    # Official USGS QA_PIXEL bits
    FILL = 0
    DILATED_CLOUD = 1
    CIRRUS = 2
    CLOUD = 3
    CLOUD_SHADOW = 4
    SNOW = 5

    def create_mask(
        self,
        qa_path: Path,
    ) -> np.ndarray:

        with rasterio.open(qa_path) as src:
            qa = src.read(1)

        mask = np.ones(qa.shape, dtype=bool)

        bits_to_remove = [
            self.FILL,
            self.DILATED_CLOUD,
            self.CIRRUS,
            self.CLOUD,
            self.CLOUD_SHADOW,
            self.SNOW,
        ]

        for bit in bits_to_remove:
            mask &= ((qa >> bit) & 1) == 0

        return mask