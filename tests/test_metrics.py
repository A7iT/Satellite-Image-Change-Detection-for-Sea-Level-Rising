import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import Point, LineString
import geopandas as gpd
from unittest.mock import patch, MagicMock

from src.change_detection.metrics import ChangeMetrics
from config.config import config

@pytest.fixture
def sample_data():
    # Transect goes from (0,0) to (10,0)
    transect = gpd.GeoDataFrame({
        "transect_id": [1, 2],
        "geometry": [LineString([(0, 0), (10, 0)]), LineString([(0, 5), (10, 5)])]
    })
    
    # Year 1 (reference) intersections
    ref_intersections = gpd.GeoDataFrame({
        "transect_id": [1, 2],
        "year": [2000, 2000],
        "geometry": [Point(2, 0), Point(5, 5)]
    })
    
    # Year 2 (comparison) intersections
    comp_intersections = gpd.GeoDataFrame({
        "transect_id": [1, 2],
        "year": [2010, 2010],
        "geometry": [Point(6, 0), Point(5, 5)]
    })
    
    intersections = pd.concat([ref_intersections, comp_intersections], ignore_index=True)
    return intersections, transect

@patch("src.change_detection.metrics.rasterio.open")
def test_compute_metrics(mock_rasterio, sample_data):
    intersections, transects = sample_data
    
    # Mock the rasterio water mask reading
    mock_src = MagicMock()
    # Return a 2D numpy array for the water mask (all 0 for simplicity)
    mock_src.read.return_value = np.zeros((100, 100))
    # Identity transform
    mock_src.transform = MagicMock()
    # Mock rowcol to return valid indices
    from rasterio.transform import rowcol
    with patch("src.change_detection.metrics.rowcol", return_value=(50, 50)):
        mock_rasterio.return_value.__enter__.return_value = mock_src
        
        metrics = ChangeMetrics()
        result = metrics.compute(
            intersections=intersections,
            transects=transects,
            reference_year=2000,
            comparison_year=2010,
            water_mask_path=Path("dummy.tif")
        )
        
        assert len(result) == 2
        
        # Test transect 1 (movement from x=2 to x=6)
        t1 = result[result["transect_id"] == 1].iloc[0]
        assert t1["years"] == 10
        assert t1["Distance"] == 4.0
        assert t1["EPR"] == t1["NSM"] / 10
        assert t1["Direction"] in ["Eroding", "Accreting", "Stable"]
        
        # Test transect 2 (no movement, x=5 to x=5)
        t2 = result[result["transect_id"] == 2].iloc[0]
        assert t2["Distance"] == 0.0
        assert t2["NSM"] == 0.0
        assert t2["EPR"] == 0.0
        assert t2["Direction"] == "Stable"
