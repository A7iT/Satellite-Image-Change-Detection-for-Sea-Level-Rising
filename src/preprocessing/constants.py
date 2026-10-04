"""
Official USGS Landsat Collection 2 Level-2 scale factors.
"""

# Surface Reflectance
REFLECTANCE_SCALE = 0.0000275
REFLECTANCE_OFFSET = -0.2

# Surface Temperature (reserved for future use)
TEMPERATURE_SCALE = 0.00341802
TEMPERATURE_OFFSET = 149.0

# Optical bands used in this thesis
OPTICAL_BANDS = [
    "blue",
    "green",
    "red",
    "nir",
    "swir1",
    "swir2",
]