# Satellite-Based Shoreline Change Detection

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This project implements a complete pipeline for satellite-based shoreline change detection using Landsat imagery (Collection 2 Level-2). The system processes Landsat data over a study period (2000-2025) and extracts shorelines using the Modified Normalized Difference Water Index (MNDWI), Otsu thresholding, and morphological cleanup. Change detection is performed using transect-based analysis (similar to the Digital Shoreline Analysis System, DSAS) to compute metrics such as Net Shoreline Movement (NSM) and End Point Rate (EPR). Additionally, it generates a labeled machine learning dataset for predicting shoreline change direction (Eroding, Accreting, Stable).

## Study Area and Methodology

**Study Area**: The coastal zone of Bangladesh/Bengal.
**CRS**: EPSG:32646 (UTM Zone 46N) and geographic EPSG:4326.
**Data**: Landsat Collection 2 Level-2 imagery (configured for max cloud cover of 30%).

**Methodology**:
1. **Acquisition & Preprocessing**: Landsat imagery is searched via STAC, downloaded, and preprocessed into annual median composites.
2. **Water Extraction**: Spectral indices (like MNDWI) are calculated, and an automatic Otsu threshold is applied to separate land and water.
3. **Shoreline Extraction**: Morphological operations filter noise, and vectorization extracts continuous shorelines.
4. **Change Detection**: Using predefined transects, intersections with annual shorelines are determined. The displacement between years computes NSM and EPR, defining change direction.
5. **Dataset Generation**: Outputs an extensive dataset (`shoreline_change_labels.csv`) with spatial and tabular metrics for ML modeling.

## Directory Structure

```text
D:\_Thesis\
├── config/              # Configuration files (study period, AOI, Landsat params, paths)
├── data/                # Data directory (managed by paths.py)
│   ├── raw/             # Raw Landsat downloads
│   ├── processed/       # Preprocessed scenes
│   ├── composites/      # Annual median composites
│   ├── indices/         # Computed spectral indices
│   ├── water/           # Binary water masks
│   ├── analysis/        # Shoreline vectors (GPKG)
│   ├── statistics/      # Change detection statistics (CSV)
│   ├── visualization/   # Validation plots
│   └── dataset/         # Final labeled ML dataset
├── logs/                # Application logs (Loguru)
├── notebooks/           # Jupyter notebooks for EDA and prototyping
├── results/             # General results output
├── shapefiles/          # Reference shapefiles (e.g., CAZ.shp)
├── src/                 # Main source code
│   ├── acquisition/     # Landsat STAC search and download
│   ├── change_detection/# DSAS-like transect analysis and metrics
│   ├── compositing/     # Annual composite generation
│   ├── indices/         # Spectral indices calculation
│   ├── models/          # Data models (dataclasses)
│   ├── pipeline/        # Workflow pipelines (e.g., YearPipeline)
│   ├── preprocessing/   # Image preprocessing
│   ├── shoreline/       # Shoreline vectorization
│   ├── utils/           # Utility scripts (logging, AOI load)
│   └── water/           # Water mask generation
└── tests/               # Unit tests
```

## Prerequisites & Installation

The project uses a Python virtual environment. Key dependencies include:
- `rasterio`, `geopandas`, `pandas`, `numpy`
- `scikit-learn`, `scikit-image`, `shapely`, `scipy`
- `pystac-client`, `planetary-computer`
- `joblib`, `loguru`, `matplotlib`

To install:
```bash
# Activate the virtual environment
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

## How to Run

1. **Configure Settings**: Review `config/config.py` to set the study period (`start_year`, `end_year`), AOI filename, Landsat parameters, and method choices.
2. **Execute Main Pipeline**:
   Run the main script to process yearly imagery, extract shorelines, run change detection, and output the labeled dataset.
   ```bash
   python main.py
   ```
3. **Outputs**:
   - `data/dataset/shoreline_change_labels.csv`: Final labeled dataset.
   - `data/statistics/`: Pairwise statistical comparisons.
   - `data/analysis/`: GeoPackages containing vectors of shorelines and change transects.
