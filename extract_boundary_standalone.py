#!/usr/bin/env python
"""
Extract Waterwegregio boundary - standalone version
Run with the same Python that runs create_thematic_maps.py
"""
import geopandas as gpd
import pandas as pd
import json
import os

# File paths
gpkg_file = "WijkBuurtkaart_2025_v0.gpkg"
excel_file = "waterweg_wijken_data.xlsx"
output_file = "web/data/waterwegregio_boundary.geojson"

print("Loading GeoPackage...")
gdf = gpd.read_file(gpkg_file, layer='wijken_v0')

print("Loading wijk codes from Excel...")
excel_df = pd.read_excel(excel_file, header=None)
data_rows = excel_df.iloc[4:35].copy()
data_rows.columns = excel_df.iloc[0]
data_df = data_rows.reset_index(drop=True)
data_df['gwb_code_10'] = data_df['gwb_code_10'].astype(str)
wijken_codes = data_df['gwb_code_10'].dropna().tolist()

print(f"Found {len(wijken_codes)} wijken codes")

# Determine correct column
wijk_code_column = 'wk_code' if 'wk_code' in gdf.columns else 'wijkcode'
gdf[wijk_code_column] = gdf[wijk_code_column].astype(str)

# Filter for Waterwegregio
waterwegregio_gdf = gdf[gdf[wijk_code_column].isin(wijken_codes)]
print(f"Filtered to {len(waterwegregio_gdf)} wijken")

# Convert to WGS84
waterwegregio_gdf = waterwegregio_gdf.to_crs(epsg=4326)

# Create boundary
print("Creating boundary...")
boundary = waterwegregio_gdf.dissolve()

# Convert to GeoJSON
geojson = json.loads(boundary.to_json())

# Save
print(f"Saving to {output_file}...")
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2)

print("✓ Boundary GeoJSON created successfully!")
print(f"  Number of wijken: {len(waterwegregio_gdf)}")
print(f"  Bounds: {boundary.total_bounds}")

