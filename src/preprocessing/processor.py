from src.models.scene import Scene

from src.preprocessing.constants import OPTICAL_BANDS
from src.preprocessing.qa_mask import QAMask
from src.preprocessing.scaler import ReflectanceScaler
from src.io.raster_writer import RasterWriter


class SceneProcessor:
    """
    Processes a single Landsat scene into analysis-ready imagery.

    Workflow:
        1. Create a QA mask.
        2. Scale each optical band.
        3. Apply the QA mask.
        4. Write the processed raster.
    """

    def __init__(self):

        self.scaler = ReflectanceScaler()
        self.qa_mask = QAMask()
        self.writer = RasterWriter()

    def process(
        self,
        scene: Scene,
    ) -> Scene:

        # ---------------------------------------------------------
        # Create QA mask once for the entire scene
        # ---------------------------------------------------------

        mask = self.qa_mask.create_mask(
            scene.raw_band("qa_pixel"),
        )

        # ---------------------------------------------------------
        # Process each optical band
        # ---------------------------------------------------------

        for band in OPTICAL_BANDS:

            image, profile = self.scaler.scale(
                scene.raw_band(band),
            )

            # -----------------------------------------------------
            # Apply QA mask
            # -----------------------------------------------------

            processed_image = image.copy()
            processed_image[~mask] = profile["nodata"]

            # -----------------------------------------------------
            # Save processed band
            # -----------------------------------------------------

            self.writer.write(
                image=processed_image,
                profile=profile,
                output_path=scene.processed_band(band),
            )

        return scene