# Satellite Image Change Detection for Sea Level Rise Assessment and Coastal Risk Prediction

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green)
![Release](https://img.shields.io/badge/release-v1.0.0-orange)

An end-to-end automated pipeline that processes 26 years (2000–2025) of Landsat satellite imagery to extract historical shorelines, calculate coastal change metrics (Erosion/Accretion/Stable), and engineer a rich tabular dataset for Machine Learning predictions.

---

## 📊 Get the Data (No Code Required)

If you just want to train Machine Learning models without running the heavy satellite extraction pipeline, you can download the fully processed, model-ready datasets directly from the [Releases Page](https://github.com/A7iT/[YOUR_REPO_NAME](https://github.com/A7iT/Satellite-Image-Change-Detection-for-Sea-Level-Rising)/releases/latest).

To load it directly into Google Colab or Jupyter:
```python
import pandas as pd

url = "https://github.com/A7iT/YOUR_REPO_NAME/releases/download/v1.0.0/final_ml_training_dataset.csv"
df = pd.read_csv(url)

# Drop target variable for ML
X = df.drop(columns=['Direction'])
y = df['Direction']
```

---

## 🛠️ Setup & Installation

If you want to run the extraction pipeline from scratch:

**1. Clone the Repository**
```bash
git clone https://github.com/A7iT/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

**2. Virtual Environment Setup (Crucial)**
*Do not install these packages globally. Always use a virtual environment to prevent geospatial dependency conflicts (e.g., rasterio/geopandas).*
```bash
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Initial Data Placement**
- Place your Area of Interest (AOI) shapefile and its sidecar files (`.shx`, `.dbf`, `.prj`) in the `shapefiles/` directory or root, and update `config/config.py` to point to it.

---

## 🚀 Pipeline Execution: Step-by-Step

### Phase 1: Imagery Download & Shoreline Extraction
This phase handles the heavy geospatial lifting. It connects to Microsoft Planetary Computer, downloads Landsat 5/7/8/9 scenes, creates annual median composites, generates MNDWI indices, vectorizes the shoreline, and calculates distances (EPR/NSM) across transects.

```bash
python main.py
```
> 💡 **Resilience Note:** Downloading 26 years of imagery takes time and Planetary Computer API tokens occasionally expire (HTTP 403 errors). The pipeline will log warnings and drop bad scenes automatically. If the script gets interrupted, **just run it again**—it will intelligently resume and skip already-processed years.

### Phase 2: Building the ML Dataset
Once `main.py` finishes, run the unified dataset builder to compile the spatial `.gpkg` files into the final Machine Learning CSV.

```bash
python src/dataset/build_dataset.py
```
This single command engineers over 30 features across 9 sequential steps:
1. **Spectral Features:** NDWI/NDVI variances, raw band reflectances, sediment ratios.
2. **Location Features:** UTM coordinates.
3. **Temporal Features:** Rolling averages, cumulative movement, and historical trends.
4. **Spatial Features:** Neighborhood EPR tracking and 3-point circle-fit shoreline curvature.
5. **Missing Values:** Cascading imputation (Temporal → Spatial → Global median).
6. **Cloud Features:** Adds scene cloud cover metadata.
7. **DEM Features:** Elevation data integration.
8. **Training Pre-processing:** Drops target-leakage columns to prepare for model training.

---

## 📂 Directory Structure

```text
├── config/                 # Pipeline settings (years, thresholds, CRS)
├── shapefiles/             # AOI shapes and input geometries
├── src/                    # Source code
│   ├── acquisition/        # Downloading Landsat data
│   ├── change_detection/   # EPR/NSM metrics and geometry operations
│   ├── dataset/            # ML feature engineering scripts
│   └── pipeline/           # Orchestration
├── data/                   # ALL GENERATED DATA (Ignored by git)
│   ├── raw/                # Raw downloaded Landsat scenes
│   ├── composites/         # Annual median composites
│   ├── indices/            # MNDWI/NDVI rasters
│   ├── water/              # Cleaned binary water masks
│   ├── analysis/           # Generated shorelines (.gpkg)
│   ├── statistics/         # Erosion/Accretion counts
│   └── dataset/            # Final ML tabular data (.csv)
├── main.py                 # Phase 1 Entry Point
└── requirements.txt        # Python dependencies
```

## 📝 License
This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
