# EFFIS Fire Data and ERA5 Climate Analysis for Europe

## Project Description

This repository contains code and analysis exploring the relationship between fire occurrences and severity in Europe, using data from the European Forest Fire Information System (EFFIS), and climate variables from the ERA5 reanalysis dataset provided by the Copernicus Climate Change Service (C3S).

The primary goals include:
* Acquiring and preprocessing EFFIS fire polygon data and relevant ERA5 climate data for Europe.
* Performing geospatial analysis, such as clipping data to specific regions (e.g., EEA38 countries) and calculating geometric properties like centroids.
* Conducting temporal analysis, grouping data into periods (e.g., 5-year intervals from 2000-2024).
* Visualizing spatial patterns (e.g., heatmaps of fire area) and statistical distributions (e.g., box plots of latitude by year group and forest type).
* Investigating potential correlations between climate variables and fire characteristics across different regions and forest types within Europe.

---

## Table of Contents

* [Project Description](#project-description)
* [Features](#features)
* [Data Sources](#data-sources)
* [Installation](#installation)
    * [Prerequisites](#prerequisites)
    * [Cloning the Repository](#cloning-the-repository)
    * [Setting up the Environment](#setting-up-the-environment)
    * [CDS API Setup (Required for ERA5 Data)](#cds-api-setup-required-for-era5-data)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Results](#results)
* [License](#license)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

---

## Features

* **Data Acquisition:** Scripts/notebooks to download EFFIS data and ERA5 climate variables via the CDS API.
* **Geospatial Preprocessing:**
    * Loading and handling European shapefiles.
    * Filtering data based on geographic regions (e.g., EEA38 countries).
    * Clipping fire data to the European outline.
    * Calculating centroids and latitudes for fire events.
* **Temporal Analysis:**
    * Extracting year information from date columns.
    * Grouping data into multi-year intervals (e.g., 5-year periods 2000-2024).
* **Visualization:**
    * Map-based plots showing fire locations/centroids, potentially colored by attributes like Forest Type.
    * Choropleth maps ("heatmaps") displaying spatial distribution of variables like Area Burned (`AREA_HA`).
    * Statistical plots (box plots) showing distributions of variables (e.g., latitude) across different time periods and categories (e.g., Forest Type).

---

## Data Sources

* **EFFIS (European Forest Fire Information System):** Provides data on fire events across Europe. [Link to EFFIS data portal or relevant source]
* **ERA5 Reanalysis:** Global atmospheric reanalysis data provided by ECMWF through the Copernicus Climate Change Service (C3S) Climate Data Store (CDS). [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/)
* **European Boundaries:** Administrative or geographical boundaries for Europe (e.g., from Eurostat/GISCO, Natural Earth). [Specify source if known]

---

## Installation

### Prerequisites

* **Git:** For cloning the repository.
* **Python:** Version 3.9 or higher recommended.
* **Conda:** Recommended for managing Python environments, especially with geospatial libraries. ([Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution)).

### Cloning the Repository

```bash
git clone [https://github.com/cshatto/effis-era5-europe
cd effis-era5-europe
```

### Set up Virtual Environment
```
python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```


