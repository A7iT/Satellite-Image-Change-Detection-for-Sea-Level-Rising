from dataclasses import dataclass


@dataclass(slots=True)
class ChangeSummary:
    """
    Statistical summary of shoreline change.
    """

    number_of_transects: int

    mean_nsm: float
    median_nsm: float
    min_nsm: float
    max_nsm: float
    std_nsm: float

    mean_epr: float
    median_epr: float
    min_epr: float
    max_epr: float
    std_epr: float

    eroding_transects: int
    accreting_transects: int
    stable_transects: int