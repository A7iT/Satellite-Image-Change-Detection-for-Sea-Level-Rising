from src.acquisition.bands import BAND_MAPPING
from src.models.bands import BandAsset, BandSet


class BandMapper:

    @staticmethod
    def get(item):

        bandset = BandSet()

        for name, asset_name in BAND_MAPPING.items():

            asset = item.assets[asset_name]

            bandset.add(
                BandAsset(
                    name=name,
                    href=asset.href,
                )
            )

        return bandset