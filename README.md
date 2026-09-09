# Satellite Image Change Detection for Sea Level Rise Assessment and Coastal Risk Prediction

A research project focused on analyzing shoreline changes, sea-level trends, and future coastal risk in **Cox's Bazar, Bangladesh** using satellite imagery, geospatial analysis, and machine learning.

## Objectives

* Detect historical shoreline changes using satellite imagery.
* Quantify coastal erosion and shoreline retreat.
* Analyze historical sea-level trends.
* Forecast future sea-level conditions.
* Identify potentially vulnerable coastal areas.

## Methodology

```text
Satellite Imagery
       ↓
Preprocessing
       ↓
NDWI Water Detection
       ↓
Coastline Extraction
       ↓
Shoreline Change Analysis
       ↓
Sea-Level Forecasting
       ↓
Coastal Risk Assessment
```

## Data

* Landsat satellite imagery
* Sea-level time-series data
* Digital Elevation Model (DEM)
* Geographic and land-use data where available

The satellite-processing pipeline supports year-based acquisition, compositing, water detection, and shoreline extraction.

## Technologies

* Python
* Google Earth Engine
* Rasterio
* GeoPandas
* GDAL
* OpenCV
* NumPy
* Pandas
* Scikit-learn
* Matplotlib
* QGIS

## Outputs

* Annual satellite composites
* Water masks
* Extracted shoreline geometries
* Shoreline-change measurements
* Sea-level forecasts
* Coastal-risk maps
* GIS-compatible datasets

## Project Status

**In Development**

The current pipeline includes satellite data acquisition, preprocessing, annual compositing, NDWI-based water detection, coastline extraction, and GIS output generation.

Forecasting, model evaluation, and integrated coastal-risk analysis are being developed as subsequent stages.

## Study Area

**Cox's Bazar, Bangladesh**

## Citation

```bibtex
@thesis{atit_coastal_risk,
  title  = {Satellite Image Change Detection for Sea Level Rise Assessment and Coastal Risk Prediction in Cox's Bazar, Bangladesh},
  author = {Atit Imtiaz},
  year   = {2026}
}
```

## License

Apache 2.0; for academic and research purposes.
