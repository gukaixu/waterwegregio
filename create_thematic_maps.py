import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os
import re
import numpy as np
from matplotlib.colors import Normalize, LinearSegmentedColormap, TwoSlopeNorm
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import AnchoredText
import matplotlib.patheffects as path_effects

# Define the input file names
gpkg_file = "WijkBuurtkaart_2025_v0.gpkg"
excel_file = "waterweg_wijken.xlsx"
output_dir = "figures"
output_dir_labels = "figures_labels"

# Ensure the output directories exist
for directory in [output_dir, output_dir_labels]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Map '{directory}' aangemaakt voor de figuren.")

# Construct the full path to the input files
script_dir = os.path.dirname(os.path.abspath(__file__))
gpkg_path = os.path.join(script_dir, gpkg_file)
excel_path = os.path.join(script_dir, excel_file)

def add_north_arrow(ax, x=0.95, y=0.95, size=0.03):
    """Add a north arrow to the map"""
    # Create north arrow
    arrow = mpatches.FancyArrowPatch((x, y-size), (x, y),
                                    arrowstyle='-|>', 
                                    mutation_scale=20,
                                    color='black',
                                    transform=ax.transAxes,
                                    zorder=1000)
    ax.add_patch(arrow)
    
    # Add 'N' text
    ax.text(x, y+size/2, 'N', transform=ax.transAxes, 
           fontsize=10, fontweight='bold', ha='center', va='bottom',
           zorder=1001)

def add_scale_bar(ax, gdf, length_km=1):
    """Add a scale bar to the map"""
    # Get map bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Position scale bar (bottom left)
    scale_x = minx + (maxx - minx) * 0.05
    scale_y = miny + (maxy - miny) * 0.05
    
    # Convert km to map units (assuming CRS is in meters)
    length_m = length_km * 1000
    
    # Draw scale bar
    ax.plot([scale_x, scale_x + length_m], [scale_y, scale_y], 
           'k-', linewidth=3, zorder=1000)
    
    # Add text
    ax.text(scale_x + length_m/2, scale_y + (maxy - miny) * 0.01, 
           f'{length_km} km', ha='center', va='bottom',
           fontsize=9, fontweight='bold',
           bbox=dict(boxstyle="round,pad=0.2", fc='white', ec='none', alpha=0.8),
           zorder=1001)

def get_optimized_colormap(has_negative, has_positive):
    """Create optimized color schemes for different data types"""
    if has_negative and has_positive:
        # Diverging colormap for both positive and negative values
        colors = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf',
                 '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850']
        return LinearSegmentedColormap.from_list('custom_diverging', colors, N=256)
    elif has_positive:
        # Sequential colormap for positive values only - start with light blue instead of white
        colors = ['#cce7f0', '#a6d8ea', '#7cc7e8', '#52b3d9', '#2e8bc8',
                 '#1264aa', '#0b4d8c', '#08306b']
        return LinearSegmentedColormap.from_list('custom_sequential', colors, N=256)
    else:
        # For negative values only
        colors = ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
                 '#ef3b2c', '#cb181d', '#a50f15', '#67000d']
        return LinearSegmentedColormap.from_list('custom_negative', colors, N=256)

def place_labels_optimized(merged_gdf, data_df, ax, wijk_code_gdf_column, show_data_values=False, data_column=None, title=""):
    """Improved label placement - show all labels"""
    from shapely.geometry import Point
    
    for idx, row in merged_gdf.iterrows():
        try:
            wijk_code = row[wijk_code_gdf_column]
            wijk_row = data_df[data_df['gwb_code_10'] == wijk_code]
            
            if not wijk_row.empty and 'wk_naam' in data_df.columns and pd.notna(wijk_row['wk_naam'].iloc[0]):
                wijk_naam = wijk_row['wk_naam'].iloc[0]
            else:
                wijk_naam = row['wk_naam'] if 'wk_naam' in row and pd.notna(row['wk_naam']) else f"Wijk {wijk_code}"
            
            # Prepare label text
            label_text = wijk_naam
            
            # Add data value if requested
            if show_data_values and 'data_value' in row and pd.notna(row['data_value']):
                data_value = row['data_value']
                
                # Check if this is a percentage field
                is_percentage = any(indicator in title.lower() for indicator in ['percentage', 'perc.', '%'])
                
                # Format the data value appropriately
                if abs(data_value) >= 1000:
                    # For large numbers, check if it's a whole number
                    if data_value == int(data_value) and not is_percentage:
                        formatted_value = f'{int(data_value):,}'.replace(',', '.')
                    else:
                        formatted_value = f'{data_value:,.1f}'.replace(',', '.').replace('.', ',', 1)
                elif abs(data_value) >= 1:
                    # For numbers >= 1, check if it's a whole number
                    if data_value == int(data_value) and not is_percentage:
                        formatted_value = f'{int(data_value)}'
                    else:
                        formatted_value = f'{data_value:.1f}'.replace('.', ',')
                else:
                    # For small numbers, always show decimals but remove trailing zeros
                    if is_percentage:
                        formatted_value = f'{data_value:.1f}'.replace('.', ',')
                    else:
                        formatted_value = f'{data_value:.2f}'.replace('.', ',').rstrip('0').rstrip(',')
                
                label_text = f"{wijk_naam}\n{formatted_value}"
            
            # Get centroid
            centroid = row.geometry.centroid
            
            # Add label with improved styling - show all labels
            text = ax.annotate(text=label_text, 
                             xy=(centroid.x, centroid.y),
                             ha='center', va='center', 
                             fontsize=7, fontweight='600',
                             fontfamily='sans-serif',
                             color='#2c3e50',
                             bbox=dict(boxstyle="round,pad=0.4", 
                                     fc='white', ec='#34495e', 
                                     alpha=0.9, linewidth=0.5),
                             zorder=1000)
            
            # Add text outline for better readability
            text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])
            
        except Exception as e:
            print(f"Waarschuwing: Kon label voor wijk {wijk_code} niet plaatsen: {e}")

def create_overview_map(waterwegregio_gdf, data_df, wijk_code_gdf_column, script_dir, output_dir):
    """
    Create an administrative overview map showing wijken colored by gemeente
    """
    try:
        # Define 4 colors for municipalities
        gemeente_colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']  # Blue, Red, Green, Orange
        
        # Get unique gemeente names
        if 'gm_naam' in waterwegregio_gdf.columns:
            unique_gemeenten = waterwegregio_gdf['gm_naam'].unique()
            print(f"Gevonden gemeenten: {list(unique_gemeenten)}")
            
            # Create color mapping
            gemeente_color_map = {}
            for i, gemeente in enumerate(unique_gemeenten):
                gemeente_color_map[gemeente] = gemeente_colors[i % len(gemeente_colors)]
        else:
            print("Waarschuwing: geen 'gm_naam' kolom gevonden voor gemeente kleuring")
            return
        
        # Create the figure
        plt.style.use('default')
        fig, ax = plt.subplots(1, 1, figsize=(14, 11), facecolor='white', dpi=150)
        
        # Plot each gemeente with its assigned color
        for gemeente, color in gemeente_color_map.items():
            gemeente_gdf = waterwegregio_gdf[waterwegregio_gdf['gm_naam'] == gemeente]
            if not gemeente_gdf.empty:
                gemeente_gdf.plot(ax=ax, facecolor=color, edgecolor='#2c3e50', 
                                linewidth=0.8, alpha=0.7)
        
        # Plot municipality borders with thick lines
        waterwegregio_gdf.dissolve(by='gm_naam').plot(ax=ax, facecolor="none", 
                                                     edgecolor='#2c3e50', linewidth=2.5, alpha=0.8)
        
        # Add wijk labels
        place_labels_optimized(waterwegregio_gdf, data_df, ax, wijk_code_gdf_column, title="")
        
        # Get the bounds of the area to set map extent
        minx, miny, maxx, maxy = waterwegregio_gdf.total_bounds
        
        # Add padding
        padding_x = (maxx - minx) * 0.03
        padding_y = (maxy - miny) * 0.03
        
        # Set the map extent
        ax.set_xlim(minx - padding_x, maxx + padding_x)
        ax.set_ylim(miny - padding_y, maxy + padding_y)
        
        # Set title
        ax.set_title('Wijken Waterwegregio', fontsize=20, fontweight='700', 
                    pad=25, color='#2c3e50', fontfamily='sans-serif')
        
        # Remove axis
        ax.set_axis_off()
        
        # Create legend for gemeenten
        legend_elements = []
        for gemeente, color in gemeente_color_map.items():
            patch = mpatches.Patch(facecolor=color, edgecolor='#2c3e50', 
                                 label=gemeente, alpha=0.7)
            legend_elements.append(patch)
        
        # Add legend
        legend = ax.legend(handles=legend_elements, loc='lower right', 
                         frameon=True, facecolor='white', framealpha=0.95, 
                         fontsize=10, edgecolor='#bdc3c7')
        legend.get_frame().set_linewidth(0.5)
        
        # Add professional cartographic elements
        add_north_arrow(ax)
        add_scale_bar(ax, waterwegregio_gdf)
        
        # Set background
        ax.set_facecolor('#f8f9fa')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the overview map
        output_file = "00_wijken_waterwegregio_overzicht.png"
        output_path = os.path.join(script_dir, output_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.15,
                   metadata={'Creator': 'Waterwegregio Thematic Maps'})
        plt.close(fig)
        
        print(f"Overzichtskaart opgeslagen als: {output_path}")
        
    except Exception as e:
        print(f"Fout bij het maken van overzichtskaart: {e}")
        import traceback
        traceback.print_exc()

def create_single_thematic_map(merged_gdf, data_df, wijk_code_gdf_column, column, title, source, output_path, show_labels=False):
    """
    Create a single thematic map
    """
    try:
        # Create the figure with better styling
        plt.style.use('default')  # Reset any previous styles
        fig, ax = plt.subplots(1, 1, figsize=(14, 11), facecolor='white', dpi=150)
        
        # Get valid min and max values for normalization
        valid_values = merged_gdf['data_value'].dropna()
        if len(valid_values) == 0:
            print(f"Kolom '{column}' overgeslagen: geen geldige waarden voor kleurenschaal.")
            plt.close(fig)
            return False
            
        vmin = valid_values.min()
        vmax = valid_values.max()
        
        # Determine if we have negative values and choose appropriate colormap
        has_negative = vmin < 0
        has_positive = vmax > 0
        
        # Get optimized colormap
        cmap = get_optimized_colormap(has_negative, has_positive)
        
        # Create normalization
        if has_negative and has_positive:
            # Create a normalization centered at zero
            max_abs = max(abs(vmin), abs(vmax))
            norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)
        else:
            norm = Normalize(vmin=vmin, vmax=vmax)
        
        # Create two GeoDataFrames - one for data with values and one for missing data
        gdf_with_values = merged_gdf[merged_gdf['data_value'].notna()].copy()
        gdf_missing = merged_gdf[merged_gdf['data_value'].isna()].copy()
        
        # Plot the data layer with appropriate color gradient
        if not gdf_with_values.empty:
            gdf_with_values.plot(ax=ax, column='data_value', cmap=cmap, norm=norm, 
                               legend=False, edgecolor='#2c3e50', linewidth=0.8, alpha=0.9)
        
        # Plot missing data with improved styling
        if not gdf_missing.empty:
            gdf_missing.plot(ax=ax, facecolor='#ecf0f1', edgecolor='#2c3e50', 
                          linewidth=0.8, hatch='///', alpha=0.8)
        
        # Plot municipality borders with improved styling
        try:
            if 'gm_naam' in merged_gdf.columns:
                merged_gdf.dissolve(by='gm_naam').plot(ax=ax, facecolor="none", 
                                                    edgecolor='#2c3e50', linewidth=2.5, alpha=0.8)
        except Exception as e:
            print(f"Waarschuwing: Kon gemeentegrenzen niet tekenen: {e}")
        
        # Add optimized labels
        place_labels_optimized(merged_gdf, data_df, ax, wijk_code_gdf_column, show_data_values=show_labels, title=title)
        
        # Get the bounds of the area to set map extent
        minx, miny, maxx, maxy = merged_gdf.total_bounds
        
        # Add padding (3% instead of 5% for better use of space)
        padding_x = (maxx - minx) * 0.03
        padding_y = (maxy - miny) * 0.03
        
        # Set the map extent
        ax.set_xlim(minx - padding_x, maxx + padding_x)
        ax.set_ylim(miny - padding_y, maxy + padding_y)

        # Improved title styling
        title_fontsize = 20
        if title and len(title) > 40:
            title_fontsize = max(16, int(20 - (len(title) - 40) / 12))
        
        # Set title with better typography
        ax.set_title(title, fontsize=title_fontsize, fontweight='700', 
                   pad=25, color='#2c3e50', fontfamily='sans-serif')
        
        # Remove axis
        ax.set_axis_off()
        
        # Add improved colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="3%", pad=0.6)
        
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, cax=cax)
        
        # Improved colorbar formatting
        def format_ticks(x, pos):
            if abs(x) >= 1000:
                return f'{int(x):,}'.replace(',', '.')
            elif abs(x) >= 1:
                return f'{x:.1f}'.replace('.', ',')
            else:
                return f'{x:.2f}'.replace('.', ',')
        
        cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
        cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(6))
        cbar.ax.tick_params(labelsize=9)
        
        # Add improved legend for missing values and source
        legend_elements = []
        if not gdf_missing.empty:
            missing_patch = mpatches.Patch(facecolor='#ecf0f1', hatch='///', 
                                          edgecolor='#2c3e50', label='Geen data',
                                          alpha=0.8)
            legend_elements.append(missing_patch)
        
        # Add source as legend element if available
        if pd.notna(source) and source:
            # Create invisible patch for source text
            source_patch = mpatches.Patch(facecolor='none', edgecolor='none', 
                                         label=f"Bron: {source}")
            legend_elements.append(source_patch)
        
        # Create legend if we have elements
        if legend_elements:
            legend = ax.legend(handles=legend_elements, loc='lower right', 
                             frameon=True, facecolor='white', framealpha=0.95, 
                             fontsize=9, edgecolor='#bdc3c7')
            legend.get_frame().set_linewidth(0.5)
            
            # Style the source text in legend
            if pd.notna(source) and source:
                legend_texts = legend.get_texts()
                if len(legend_texts) > 1:  # If we have both "Geen data" and source
                    legend_texts[-1].set_style('italic')
                    legend_texts[-1].set_color('#7f8c8d')
                elif len(legend_texts) == 1 and 'Bron:' in legend_texts[0].get_text():  # Only source
                    legend_texts[0].set_style('italic')
                    legend_texts[0].set_color('#7f8c8d')
        
        # Add professional cartographic elements
        add_north_arrow(ax)
        add_scale_bar(ax, merged_gdf)
        
        # Set subtle background
        ax.set_facecolor('#f8f9fa')
        
        # Adjust layout with better spacing
        plt.tight_layout()
        
        # Save with higher quality settings
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                  facecolor='white', edgecolor='none', pad_inches=0.15,
                  metadata={'Creator': 'Waterwegregio Thematic Maps'})
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"Fout bij het maken van kaart: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_thematic_maps():
    """
    Creates thematic maps for all variables in the Excel file.
    """
    try:
        # Load the Excel file
        print(f"Laden van Excel bestand...")
        excel_df = pd.read_excel(excel_path, header=None)
        print(f"Excel bestand succesvol geladen: {excel_path}")
        
        # Extract metadata from specific rows
        var_names = excel_df.iloc[0, 6:].tolist()  # From column G onwards (index 6)
        var_titles = excel_df.iloc[1, 6:].tolist()  # Titles from row 2
        var_sources = excel_df.iloc[2, 6:].tolist()  # Sources from row 3
        
        # Create a dictionary mapping variable names to their titles and sources
        var_info = {}
        for var_name, title, source in zip(var_names, var_titles, var_sources):
            if pd.notna(var_name):
                var_info[var_name] = {'title': title, 'source': source}
        
        # Extract only rows 5 through 35 (index 4-34)
        data_rows = excel_df.iloc[4:35].copy()
        # Set the header to be the first row of the Excel file (variable names)
        data_rows.columns = excel_df.iloc[0]
        # Reset index after slicing
        data_df = data_rows.reset_index(drop=True)
        
        print(f"Data geëxtraheerd van rijen 5 t/m 35 van het Excel bestand.")
        
        # Check for gwb_code_10 column
        if 'gwb_code_10' not in data_df.columns:
            print(f"Fout: Kolom 'gwb_code_10' niet gevonden in het Excel bestand.")
            return
        
        # Make sure ID column is treated as string
        data_df['gwb_code_10'] = data_df['gwb_code_10'].astype(str)
            
        # Load the GeoPackage file, specifically the wijken layer
        print(f"Laden van {gpkg_path}, laag 'wijken_v0'...")
        try:
            gdf = gpd.read_file(gpkg_path, layer='wijken_v0')
            print("Wijken laag succesvol geladen.")
        except Exception as e:
            print(f"Fout bij het laden van de wijken laag: {e}")
            # Try to load the GeoPackage without specifying a layer
            try:
                print("Proberen om GeoPackage te laden zonder laagnaam...")
                gdf = gpd.read_file(gpkg_path)
                print("GeoPackage succesvol geladen zonder laagnaam.")
            except Exception as e2:
                print(f"Fout bij het laden van het GeoPackage bestand: {e2}")
                return

        # Determine the correct column name for wijk code in the GeoPackage
        if 'wk_code' in gdf.columns:
            wijk_code_gdf_column = 'wk_code'
        elif 'wijkcode' in gdf.columns:
            wijk_code_gdf_column = 'wijkcode'
        else:
            print("Geen standaard wijkcode kolom gevonden in GeoPackage. Beschikbare kolommen:")
            print(gdf.columns.tolist())
            return
        
        # Make sure GeoPackage ID column is treated as string for comparison
        gdf[wijk_code_gdf_column] = gdf[wijk_code_gdf_column].astype(str)

        # Get list of wijk codes from the Excel file
        wijken_codes = data_df['gwb_code_10'].dropna().tolist()
        
        # Filter for the specified wijken based on Excel data
        print(f"Filteren op {len(wijken_codes)} wijken uit Excel data...")
        waterwegregio_gdf = gdf[gdf[wijk_code_gdf_column].isin(wijken_codes)]

        if waterwegregio_gdf.empty:
            print(f"Geen data gevonden voor de opgegeven wijken. Controleer de codes.")
            
            # Detailed debug info for troubleshooting
            print(f"Excel wijkcodes: {wijken_codes[:5]}...")  # Print first few codes
            gdf_codes = gdf[wijk_code_gdf_column].unique().tolist()
            print(f"GeoPackage wijkcodes (eerste 5): {gdf_codes[:5]}...")
            
            return

        print(f"{len(waterwegregio_gdf)} wijken gevonden voor de Waterwegregio.")
        
        # Create overview maps for both directories
        create_overview_map(waterwegregio_gdf, data_df, wijk_code_gdf_column, script_dir, output_dir)
        create_overview_map(waterwegregio_gdf, data_df, wijk_code_gdf_column, script_dir, output_dir_labels)
        
        # Create the data columns list using only variables from column G onwards
        data_columns = [col for col in var_names if col is not None and pd.notna(col)]
        
        print(f"Genereren van {len(data_columns)} thematische kaarten...")
        
        # Create thematic maps for each data column
        for column in data_columns:
            try:
                # Skip if column is not in the dataframe
                if column not in data_df.columns:
                    print(f"Kolom '{column}' niet gevonden in de data.")
                    continue
                
                # Try to convert the column to numeric, forcing errors to NaN
                data_df[column] = pd.to_numeric(data_df[column], errors='coerce')
                
                # Check if the column has any valid numeric data after conversion
                if data_df[column].isna().all():
                    print(f"Kolom '{column}' overgeslagen: bevat geen geldige numerieke data.")
                    continue
                
                # Print how many valid values we have
                valid_count = data_df[column].notna().sum()
                print(f"Kolom '{column}' heeft {valid_count} geldige numerieke waarden.")
                
                # Get variable title and source
                if column in var_info:
                    title = var_info[column]['title'] if pd.notna(var_info[column]['title']) else column
                    source = var_info[column]['source'] if pd.notna(var_info[column]['source']) else ""
                else:
                    title = column
                    source = ""
                
                # Create a merged geodataframe with the data column
                merged_gdf = waterwegregio_gdf.copy()
                merged_gdf['data_value'] = np.nan
                
                # Add the data values to the geodataframe
                for idx, row in merged_gdf.iterrows():
                    wijk_code = row[wijk_code_gdf_column]
                    matching_rows = data_df[data_df['gwb_code_10'] == wijk_code]
                    
                    if not matching_rows.empty and pd.notna(matching_rows[column].iloc[0]):
                        merged_gdf.at[idx, 'data_value'] = matching_rows[column].iloc[0]
                
                # Check if we have any valid data after merging
                if merged_gdf['data_value'].isna().all():
                    print(f"Kolom '{column}' overgeslagen: geen geldige data na koppeling met geometrie.")
                    continue
                
                # Create output file paths for both versions
                output_file = f"{column}.png"
                output_path_regular = os.path.join(script_dir, output_dir, output_file)
                output_path_labels = os.path.join(script_dir, output_dir_labels, output_file)
                
                # Create regular map (without data values in labels)
                success_regular = create_single_thematic_map(
                    merged_gdf, data_df, wijk_code_gdf_column, column, title, source, 
                    output_path_regular, show_labels=False
                )
                
                if success_regular:
                    print(f"Kaart voor {column} opgeslagen als: {output_path_regular}")
                
                # Create map with data values in labels
                success_labels = create_single_thematic_map(
                    merged_gdf, data_df, wijk_code_gdf_column, column, title, source, 
                    output_path_labels, show_labels=True
                )
                
                if success_labels:
                    print(f"Kaart met data labels voor {column} opgeslagen als: {output_path_labels}")
                
            except Exception as e:
                print(f"Fout bij het maken van kaart voor {column}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"Alle thematische kaarten zijn opgeslagen in de mappen: {output_dir} en {output_dir_labels}")

    except FileNotFoundError as e:
        print(f"Fout: Een bestand is niet gevonden: {e}")
    except Exception as e:
        print(f"Er is een onverwachte fout opgetreden: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_thematic_maps() 