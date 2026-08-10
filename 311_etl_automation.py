import requests
import logging
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_311_data(output_geojson):
    logging.info("Starting live API ETL process from Dallas OpenData")

    try:
        API_URL = "https://www.dallasopendata.com/resource/gc4d-8a49.json"

        # Request the 1000 most recent records
        query_params = {
            "$limit": 50,
            "$order": "created_date DESC"
        }

        logging.info("Fetching data from Dallas 311 API...")
        response = requests.get(API_URL, params=query_params)
        response.raise_for_status()

        df = pd.DataFrame(response.json())
        logging.info(f"Successfully fetched {len(df)} records from API.")

    except requests.exceptions.RequestException as e:
        logging.error(f"API Request failed: {e}")
        return

    available_columns = df.columns.tolist()

    if 'lat_location' not in available_columns:
        logging.error(f"Could not find 'lat_location'. Available columns: {available_columns}")
        return

    logging.info("Extracting coordinates from 'lat_location' string...")

    # 1. Clean the string: remove '(' and ')' then split by the comma
    # This turns "(32.90, -96.71)" into two separate data pieces
    coords = df['lat_location'].astype(str).str.replace('(', '', regex=False).str.replace(')', '',
                                                                                          regex=False).str.split(',',
                                                                                                                 expand=True)

    # 2. Assign the split data to lat and lon columns
    df['lat'] = coords[0]
    df['lon'] = coords[1]

    # 3. Convert the text into actual decimal numbers
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    # 4. Drop rows with missing or invalid coordinates
    initial_count = len(df)
    df = df.dropna(subset=['lat', 'lon'])
    dropped_count = initial_count - len(df)
    logging.info(f"Dropped {dropped_count} records due to missing or invalid spatial coordinates.")

    if len(df) == 0:
        logging.error("No valid coordinates found after extraction. The file will not save.")
        return

    # 5. Geometry Creation
    geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    logging.info("Successfully converted DataFrame to GeoDataFrame.")

    # 6. Export to GeoJSON
    try:
        if os.path.exists(output_geojson):
            os.remove(output_geojson)

        gdf.to_file(output_geojson, driver='GeoJSON')
        logging.info(f"SUCCESS: Exported geospatial data to {output_geojson}")
    except Exception as e:
        logging.error(f"Failed to export data: {e}")


if __name__ == "__main__":
    # Force the output to save in the exact same directory as this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FILE = os.path.join(current_dir, "processed_311_reports.geojson")

    process_311_data(OUTPUT_FILE)
