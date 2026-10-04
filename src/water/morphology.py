import numpy as np
from scipy.ndimage import (
    binary_closing,
    binary_fill_holes,
    binary_opening,
)


class Morphology:
    """
    Cleans a binary water mask using morphological operations.

    Workflow
    --------
    1. Binary opening
    2. Binary closing
    3. Hole filling
    """

    def clean(
        self,
        water_mask: np.ndarray,
    ) -> np.ndarray:

        # ---------------------------------------------------------
        # Remove isolated pixels
        # ---------------------------------------------------------

        cleaned = binary_opening(
            water_mask.astype(bool),
            iterations=2,
        )

        # ---------------------------------------------------------
        # Close small gaps
        # ---------------------------------------------------------

        cleaned = binary_closing(
            cleaned,
            iterations=2,
        )

        # ---------------------------------------------------------
        # Fill holes inside water bodies
        # ---------------------------------------------------------

        cleaned = binary_fill_holes(cleaned)

        return cleaned.astype(np.uint8)