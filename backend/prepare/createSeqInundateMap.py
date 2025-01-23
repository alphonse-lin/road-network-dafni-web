import os
import re
import sys
import zipfile
import tempfile
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
import warnings
from pathlib import Path
import shutil

#TODO: 001_需要验证
def extract_number(filename):
    """Extract number from filename, return 0 if no number found"""
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

def process_zip_file(zip_path):
    """
    Extract zip file to a temporary directory
    
    Args:
        zip_path (str): Path to the zip file
    
    Returns:
        str: Path to the temporary directory containing extracted files
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Extract zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    return temp_dir

def create_inundate_map(geojson_path, flood_zip_path, output_dir):
    """
    Create inundation maps from GeoJSON network data and flooding event zip file
    
    Args:
        geojson_path (str): Path to the road network GeoJSON file
        flood_zip_path (str): Path to the zip file containing flood event ASC files
        output_dir (str): Directory to save output CSV files
    """
    try:
        # Disable warnings and scientific notation
        warnings.filterwarnings('ignore')
        np.set_printoptions(suppress=True)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract zip file to temporary directory
        temp_dir = process_zip_file(flood_zip_path)
        
        # Load road network data
        road_network = gpd.read_file(geojson_path)
        
        # Get and sort flood event files
        files = [f for f in os.listdir(temp_dir) if f.endswith('.asc')]
        sorted_files = sorted(files, key=extract_number)
        
        flag_dic = {}
        depth_dic = {}
        ids = []
        
        for file in sorted_files:
            if file.startswith('h_') and file.endswith('.asc'):
                flood_map_path = os.path.join(temp_dir, file)
                temp_attr = file.split('.')[0]

                with rasterio.open(flood_map_path) as asc:
                    flood_map = asc.read(1)

                depths = []
                flags = []
                for i, row in road_network.iterrows():
                    if temp_attr == 'h_0':
                        ids.append(int(row['id']))

                    road_bounds = row.geometry.bounds
                    minx, miny, maxx, maxy = road_bounds
                    left, bottom = rasterio.transform.rowcol(asc.transform, minx, miny)
                    right, top = rasterio.transform.rowcol(asc.transform, maxx, maxy)

                    check_value = flood_map[min(left, right):max(left, right), 
                                         min(top, bottom):max(top, bottom)]
                    
                    max_value = np.max(check_value) if check_value.size > 0 else 0
                    depths.append(max_value)
                    flags.append(1 if (check_value > 3).any() else 0)

                flag_dic[temp_attr] = flags
                depth_dic[f'{temp_attr}_depth'] = depths
                print(f'Processed {temp_attr}')

        flag_dic['id'] = ids
        depth_dic['id'] = ids
        
        # Create and save flag DataFrame
        flag_df = pd.DataFrame(flag_dic)
        flag_df.sort_values(by=['id'], inplace=True, ascending=True)
        flag_path = os.path.join(output_dir, 'flag_sequenced_flooded_roads.csv')
        flag_df.to_csv(flag_path, index=False)

        # Create and save depth DataFrame
        depth_df = pd.DataFrame(depth_dic)
        depth_df.sort_values(by=['id'], inplace=True, ascending=True)
        depth_path = os.path.join(output_dir, 'depth_sequenced_flooded_roads.csv')
        depth_df.to_csv(depth_path, index=False)

        return {
            'flag_path': flag_path,
            'depth_path': depth_path,
            'status': 'success'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
        
    finally:
        # Clean up temporary directory
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    create_inundate_map(
        geojson_path='data/road_network.geojson',
        flood_zip_path='data/flood_event.zip',
        output_dir='data/output'
    )