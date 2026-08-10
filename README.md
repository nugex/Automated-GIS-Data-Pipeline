# Automated 311 Data ETL Pipeline

## Overview
This project demonstrates an automated Extract, Transform, Load (ETL) pipeline designed for municipal GIS environments. It simulates a daily workflow where raw, unstructured 311 citizen reports (like potholes or water leaks) are ingested, cleaned of spatial errors, converted into a geospatial format, and exported for use in enterprise mapping systems like ArcGIS Online or Experience Builder.

## The Problem
Municipal departments often receive daily tabular exports of citizen requests. These datasets frequently contain errors (e.g., missing coordinates, improper formatting) that prevent them from being mapped accurately. Manually cleaning and converting this data daily is a drain on GIS and IT resources.

## The Solution
This Python script automates the process by:
1. **Extracting** the raw tabular data (CSV).
2. **Transforming** the data by identifying and removing records with missing or invalid spatial coordinates (lat/lon).
3. **Loading** the data into a `GeoDataFrame` and defining the Coordinate Reference System (EPSG: 4326).
4. **Exporting** the clean data as a `GeoJSON` file, ready for immediate ingestion into a web map or spatial database.

## Technologies Used
* **Python 3.x**
* **Pandas:** For tabular data manipulation and cleaning.
* **GeoPandas & Shapely:** For creating spatial geometries and managing the Coordinate Reference System (CRS).

## How to Run
1. Ensure you have the required libraries installed: `pip install pandas geopandas shapely`
2. Place the `raw_311_reports.csv` in the same directory as the script.
3. Run `python 311_etl_automation.py`.
4. Check the directory for the newly created `processed_311_reports.geojson`.
