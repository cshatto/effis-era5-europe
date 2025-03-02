# ERA5-Land Data Query for FWI and VPD Calculation

This repository provides a Python script that uses the Google Earth Engine (GEE) Python API along with geemap to query the ERA5-Land hourly dataset. The extracted data includes the necessary variables to calculate the Fire Weather Index (FWI) and Vapor Pressure Deficit (VPD).

## Features

- **Data Query:** Filters the ERA5-Land hourly dataset by date and region.
- **Variable Extraction:** Retrieves 2m air temperature, 2m dewpoint temperature, 10m wind components, and total precipitation.
- **Derived Calculations:** Computes wind speed from the u and v components.
- **Visualization:** Displays mean values for each variable on an interactive geemap.

## Requirements

- Python 3.11.9
- [Google Earth Engine Python API](https://developers.google.com/earth-engine/guides/python_install)
- [geemap](https://github.com/giswqs/geemap)

Additional dependencies can be installed via the provided `requirements.txt`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo_url>
   cd <repo_directory>
