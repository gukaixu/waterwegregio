#!/usr/bin/env python3
"""
Script to extract Waterwegregio boundary from GeoPackage and save as GeoJSON
Run this script to update the boundary with accurate geographic data
"""

import geopandas as gpd
import pandas as pd
import json
import os

# File paths
GPKG_FILE = "../WijkBuurtkaart_2025_v0.gpkg"
EXCEL_FILE = "../waterweg_wijken_data.xlsx"
OUTPUT_FILE = "data/waterwegregio_boundary.geojson"

def extract_boundary():
    """Extract Waterwegregio boundary from GeoPackage"""
    
    print("Loading GeoPackage...")
    gdf = gpd.read_file(GPKG_FILE, layer='wijken_v0')
    
    print("Loading wijk codes from Excel...")
    excel_df = pd.read_excel(EXCEL_FILE, header=None)
    data_rows = excel_df.iloc[4:35].copy()
    data_rows.columns = excel_df.iloc[0]
    data_df = data_rows.reset_index(drop=True)
    data_df['gwb_code_10'] = data_df['gwb_code_10'].astype(str)
    
    # Get wijk codes
    wijken_codes = data_df['gwb_code_10'].dropna().tolist()
    print(f"Found {len(wijken_codes)} wijken codes")
    
    # Determine the correct column name
    if 'wk_code' in gdf.columns:
        wijk_code_column = 'wk_code'
    elif 'wijkcode' in gdf.columns:
        wijk_code_column = 'wijkcode'
    else:
        raise ValueError("Could not find wijk code column in GeoPackage")
    
    gdf[wijk_code_column] = gdf[wijk_code_column].astype(str)
    
    # Filter for Waterwegregio wijken
    waterwegregio_gdf = gdf[gdf[wijk_code_column].isin(wijken_codes)]
    print(f"Filtered to {len(waterwegregio_gdf)} wijken")
    
    # Convert to WGS84 for web mapping
    waterwegregio_gdf = waterwegregio_gdf.to_crs(epsg=4326)
    
    # Create boundary (dissolve all wijken into one polygon)
    print("Creating boundary...")
    boundary = waterwegregio_gdf.dissolve()
    
    # Convert to GeoJSON
    geojson = json.loads(boundary.to_json())
    
    # Save to file
    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    
    print("✓ Boundary GeoJSON created successfully!")
    print(f"  Bounds: {boundary.total_bounds}")
    
    return True

if __name__ == "__main__":
    try:
        extract_boundary()
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nMake sure you have the required dependencies:")
        print("  pip install geopandas pandas openpyxl")
        exit(1)

