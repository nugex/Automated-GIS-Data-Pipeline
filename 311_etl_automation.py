import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import logging

# Set up basic logging to track the script's progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_311_data(input_csv, output_geojson):
    logging.info(f"Starting ETL process for {input_csv}")

    try:
        # Load the raw CSV data
        df = pd.read_csv(input_csv)
        logging.info(f"Successfully loaded {len(df)} records.")
    except FileNotFoundError:
        logging.error("Input CSV not found. Please check the file path.")
        return

    # Data Cleaning: Drop rows where latitude or longitude is missing
    initial_count = len(df)
    df = df.dropna(subset=['lat', 'lon'])
    dropped_count = initial_count - len(df)
    logging.info(f"Dropped {dropped_count} records due to missing spatial coordinates.")

    # Data Transformation: Ensure coordinates are numeric
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df = df.dropna(subset=['lat', 'lon'])

    # Geometry Creation: Convert lat/lon into Shapely Point objects
    geometry = [Point(xy) for xy in zip(df.lon, df.lat)]

    # Create a GeoDataFrame, defining the Coordinate Reference System (WGS 84)
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    logging.info("Successfully converted DataFrame to GeoDataFrame.")

    # Export to GeoJSON for use in Web GIS (like ArcGIS Online or Experience Builder)
    try:
        # Remove file if it already exists to ensure fresh daily data
        if os.path.exists(output_geojson):
            os.remove(output_geojson)

        gdf.to_file(output_geojson, driver='GeoJSON')
        logging.info(f"Successfully exported geospatial data to {output_geojson}")
    except Exception as e:
        logging.error(f"Failed to export data: {e}")


if __name__ == "__main__":
    # Define file paths
    INPUT_FILE = "raw_311_reports.csv"
    OUTPUT_FILE = "processed_311_reports.geojson"

    process_311_data(INPUT_FILE, OUTPUT_FILE)
