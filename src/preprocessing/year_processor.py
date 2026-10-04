from tqdm import tqdm

from src.models.year_dataset import YearDataset
from src.preprocessing.processor import SceneProcessor


class YearProcessor:
    """
    Processes all Landsat scenes for a single year.

    Each scene is converted into an analysis-ready dataset by
    applying reflectance scaling, QA masking, and writing the
    processed optical bands to disk.
    """

    def __init__(self):

        self.scene_processor = SceneProcessor()

    def process(
        self,
        dataset: YearDataset,
    ) -> YearDataset:

        processed_scenes = []

        for scene in tqdm(
            dataset.scenes,
            desc=f"Processing {dataset.year}",
            unit="scene",
        ):

            processed_scene = self.scene_processor.process(scene)
            processed_scenes.append(processed_scene)

        dataset.scenes = processed_scenes

        return dataset