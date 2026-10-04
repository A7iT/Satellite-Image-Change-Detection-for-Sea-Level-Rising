import json

from loguru import logger
from tqdm import tqdm

from src.acquisition.scene_downloader import SceneDownloader
from src.models.year_dataset import YearDataset


class YearDownloader:
    """
    Downloads all scenes belonging to one processing year.
    """


    def __init__(self):

        self.scene_downloader = SceneDownloader()



    def _is_scene_complete(
        self,
        scene,
    ) -> bool:

        manifest = scene.download_manifest_path

        if not manifest.exists():
            return False


        try:

            with open(
                manifest,
                "r",
                encoding="utf-8",
            ) as f:

                state = json.load(f)


            return state.get(
                "completed",
                False,
            )


        except Exception:

            return False



    def download(
        self,
        dataset: YearDataset,
        aoi,
    ) -> YearDataset:


        downloaded = 0
        skipped = 0
        failed = 0

        failed_scenes = []


        for scene in tqdm(
            dataset.scenes,
            desc=f"Downloading {dataset.year}",
            unit="scene",
        ):


            if self._is_scene_complete(scene):

                skipped += 1
                continue



            try:

                self.scene_downloader.download(
                    scene=scene,
                    aoi=aoi,
                )

                downloaded += 1


            except Exception:

                failed += 1

                failed_scenes.append(
                    scene.id
                )

                logger.exception(
                    f"Failed downloading scene: {scene.id}"
                )


                continue



        dataset.download_complete = (
            failed == 0
        )


        logger.info("")
        logger.info("=" * 60)
        logger.info("Download Summary")
        logger.info("=" * 60)

        logger.info(
            f"Year         : {dataset.year}"
        )

        logger.info(
            f"Total Scenes : {len(dataset.scenes)}"
        )

        logger.info(
            f"Downloaded   : {downloaded}"
        )

        logger.info(
            f"Skipped      : {skipped}"
        )

        logger.info(
            f"Failed       : {failed}"
        )


        if failed_scenes:

            logger.warning("")
            logger.warning(
                "Failed Scene IDs:"
            )

            for scene_id in failed_scenes:

                logger.warning(
                    f"  • {scene_id}"
                )


        logger.info("=" * 60)


        return dataset