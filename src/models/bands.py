from dataclasses import dataclass, field


@dataclass(frozen=True)
class BandAsset:
    """
    Represents one remote raster band.
    """

    name: str
    href: str


@dataclass
class BandSet:
    """
    Collection of raster bands.
    """

    bands: dict[str, BandAsset] = field(default_factory=dict)

    def add(self, band: BandAsset) -> None:
        self.bands[band.name] = band

    def get(self, name: str) -> BandAsset:
        return self.bands[name]

    def __getitem__(self, name: str) -> BandAsset:
        return self.bands[name]

    def __contains__(self, name: str) -> bool:
        return name in self.bands

    def __len__(self) -> int:
        return len(self.bands)

    def items(self):
        return self.bands.items()

    def keys(self):
        return self.bands.keys()

    def values(self):
        return self.bands.values()