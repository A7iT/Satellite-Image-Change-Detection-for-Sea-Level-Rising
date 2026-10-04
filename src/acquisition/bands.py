"""
Band mappings used during STAC acquisition.
"""

BAND_MAPPING = {
    "blue": "blue",
    "green": "green",
    "red": "red",
    "nir": "nir08",
    "swir1": "swir16",
    "swir2": "swir22",
    "qa_pixel": "qa_pixel",
}

REQUIRED_BANDS = (
    "blue",
    "green",
    "red",
    "nir",
    "swir1",
    "swir2",
    "qa_pixel",
)