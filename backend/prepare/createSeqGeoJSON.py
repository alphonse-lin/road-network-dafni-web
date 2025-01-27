import geopandas as gpd
import pandas as pd
import os
from pathlib import Path

#TODO: 002_需要验证
def create_sequence_geojson(geojson_path, flag_csv_path, output_dir):
    """
    Create sequence of GeoJSON files based on flooding flags
    
    Args:
        geojson_path (str): Path to the original road network GeoJSON file
        flag_csv_path (str): Path to the flag_sequenced_flooded_roads.csv file
        output_dir (str): Directory to save output GeoJSON files
    """
    output_dir=os.path.join(output_dir,"001_inundate_roadnetwork")
    os.makedirs(output_dir, exist_ok=True)
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Read the original GeoJSON file
        road_network = gpd.read_file(geojson_path)
        road_network['id'] = road_network['id'].astype(int)
        # Read the flag CSV file
        flag_df = pd.read_csv(flag_csv_path)
        
        # Add sequential ID to road network if it doesn't exist
        if 'id' not in road_network.columns:
            road_network['id'] = range(len(road_network))
        
        # Get all time steps (columns that start with 'h_')
        time_steps = [col for col in flag_df.columns if col.startswith('h_')]
        
        # Process each time step
        for time_step in time_steps:
            # Create a mask for non-flooded roads (where flag is 0)
            non_flooded_mask = flag_df[time_step] == 0
            
            # Get IDs of non-flooded roads
            non_flooded_ids = flag_df.loc[non_flooded_mask, 'id'].tolist()
            # Filter road network to keep only non-flooded roads
            filtered_network = road_network[road_network['id'].isin(non_flooded_ids)].copy()
            
            # Save the filtered network as GeoJSON
            output_path = os.path.join(output_dir, f'network_{time_step}.geojson')
            filtered_network.to_file(output_path, driver='GeoJSON')
            
            print(f'Created GeoJSON for time step {time_step} with {len(filtered_network)} roads')
        
        return {
            'status': 'success',
            'message': f'Created {len(time_steps)} GeoJSON files in {output_dir}',
            'output_dir': output_dir
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 
    
if __name__ == "__main__":
    geojson_path=r'src\assets\sample_data\roadnetwork.geojson'
    output_dir=r'src\assets\sample_data\output'
    result = create_sequence_geojson(
    geojson_path=geojson_path,
    flag_csv_path=os.path.join(output_dir,'001_inundate_roadnetwork','flag_sequenced_flooded_roads.csv'),
    output_dir=output_dir
    )

    if result['status'] == 'success':
        print(result['message'])
    else:
        print(f"Error: {result['message']}")

