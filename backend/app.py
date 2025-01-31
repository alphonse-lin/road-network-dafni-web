from flask import Flask, request, jsonify
from flask_cors import CORS  # 添加跨域支持
from pathlib import Path
import os
from prepare.createSeqInundateMap import create_inundate_map
from prepare.createSeqGeoJSON import create_sequence_geojson
from prepare.csharpCalculation import calculate_space_syntax_for_each_file, calculate_space_syntax
from prepare.generateDailyActivityChain import generate_daily_activity_chain
from prepare.runMatsim import run_matsim
from prepare.convertData import process_matsim_output
from prepare.mergeData import merge_data
from prepare.dtwmatching import dtw_matching
from prepare.vulnerabilityCalculation import calculate_vulnerability
import json
import sys  # 添加这行
import geopandas as gpd
from pyproj import CRS
import pandas as pd
from collections import Counter
import csv

#TODO: 输出直接改成4326的geojson
#TODO: 在后端计算面积
#TODO: 后端计算平均路网密度

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'  # 所有计算任务的根目录

def ensure_task_directories(project_id):
    # 获取项目根目录
    base_dir = Path(__file__).parent.parent
    
    # 构建目录路径
    task_dir = base_dir / 'data' / project_id
    input_dir = task_dir / 'input'
    output_dir = task_dir / 'output'
    
    # 打印调试信息
    print(f"Base directory: {base_dir}")
    print(f"Task directory: {task_dir}")
    print(f"Output directory: {output_dir}")
    
    # 确保目录存在
    task_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return task_dir, input_dir, output_dir

@app.route('/api/create-inundate-map', methods=['POST'])
def api_create_inundate_map():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        # 确保目录存在
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        # 使用任务特定的路径
        geojson_path = data.get('geojson_path', str(input_dir / 'roadnetwork.geojson'))
        flood_zip_path = data.get('flood_zip_path', str(input_dir / 'flooding_output.zip'))
        
        result = create_inundate_map(
            geojson_path=geojson_path,
            flood_zip_path=flood_zip_path,
            output_dir=str(output_dir)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/create-sequence-geojson', methods=['POST'])
def api_create_sequence_geojson():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        geojson_path = data.get('geojson_path', str(input_dir / 'roadnetwork.geojson'))
        flag_csv_path = data.get('flag_csv_path', str(output_dir / '001_inundate_roadnetwork' / 'flag_sequenced_flooded_roads.csv'))
        
        result = create_sequence_geojson(
            geojson_path=geojson_path,
            flag_csv_path=flag_csv_path,
            output_dir=str(output_dir)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calculate-space-syntax', methods=['POST'])
def api_calculate_space_syntax():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        radii = data.get('radii', "100")  # 获取前端传入的半径
        
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        input_dir = data.get('input_dir', str(output_dir / '001_inundate_roadnetwork'))
        
        success = calculate_space_syntax_for_each_file(
            input_dir=input_dir,
            output_base_folder=str(output_dir),
            radii=radii  # 使用前端传入的半径
        )
        
        if success:
            return jsonify({
                'status': 'success', 
                'message': 'Space syntax calculation completed',
                'radii': radii  # 返回使用的半径值
            })
        else:
            return jsonify({'status': 'error', 'message': 'Space syntax calculation failed'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calculate-space-syntax-single', methods=['POST'])
def api_calculate_space_syntax_single():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        radii = data.get('radii', "100")  # 获取前端传入的半径
        
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        input_file = str(input_dir / 'roadnetwork.geojson')
        if not os.path.exists(input_file):
            return jsonify({'status': 'error', 'message': 'Input GeoJSON file not found'}), 400
        
        output_folder = output_dir / '002_topology_calculation'
        output_folder.mkdir(parents=True, exist_ok=True)
        
        output_file = str(output_folder / 'out_network.geojson')
        
        success = calculate_space_syntax(
            input_file,
            output_file,
            radii=radii  # 使用前端传入的半径
        )
        
        if success:
            return jsonify({
                'status': 'success', 
                'message': 'Space syntax calculation completed',
                'radii': radii  # 返回使用的半径值
            })
        else:
            return jsonify({'status': 'error', 'message': 'Space syntax calculation failed'})
            
    except Exception as e:
        print(f"Error in calculate_space_syntax_single: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/generate-activity-chain', methods=['POST'])
def api_generate_activity_chain():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        success = generate_daily_activity_chain(
            input_dir=str(input_dir),
            output_dir=str(output_dir)
        )
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/run-matsim', methods=['POST'])
def api_run_matsim():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        success = run_matsim(str(output_dir / '003_matsim_calculation'))
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/convert-matsim-output', methods=['POST'])
def api_convert_matsim_output():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        success = process_matsim_output(str(output_dir))
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/merge-data', methods=['POST'])
def api_merge_data():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        topology_dir = data.get('topology_dir', str(output_dir / '002_topology_calculation'))
        traffic_file = data.get('traffic_file', str(output_dir / '004_merged_data' / 'traffic_flow_450s.csv'))
        start_time = data.get('start_time', "7:00")
        
        success = merge_data(
            topology_dir=topology_dir,
            traffic_file=traffic_file,
            output_dir=str(output_dir / '004_merged_data'),
            start_time=start_time
        )
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dtw-matching', methods=['POST'])
def api_dtw_matching():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        input_csv_path = data.get('input_csv_path', str(output_dir / '004_merged_data' / 'merged_output.csv'))
        output_csv_path = data.get('output_csv_path', str(output_dir / '004_merged_data' / 'dtw_matching_result.csv'))
        
        success = dtw_matching(
            input_csv_path=input_csv_path,
            output_csv_path=output_csv_path
        )
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calculate-vulnerability', methods=['POST'])
def api_calculate_vulnerability():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        input_file = data.get('input_file', str(output_dir / '004_merged_data' / 'merged_output.csv'))
        time_interval = data.get('time_interval', 450)
        output_filename = data.get('output_filename', 'road_vulnerability_index.csv')
        
        success = calculate_vulnerability(
            input_file=input_file,
            output_dir=str(output_dir / '004_merged_data'),
            time_interval=time_interval,
            output_filename=output_filename
        )
        return jsonify({'status': 'success' if success else 'error'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vulnerability/statistics', methods=['GET'])
def get_vulnerability_statistics():
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        # 读取vulnerability index文件
        vulnerability_file = output_dir / '004_merged_data' / 'road_vulnerability_index.csv'
        if not vulnerability_file.exists():
            return jsonify({'status': 'error', 'message': 'Vulnerability index file not found'}), 404
            
        df = pd.read_csv(vulnerability_file)
        
        # 计算统计数据
        total_segments = len(df) // 2  # 因为每个road segment有两条记录
        
        # 获取时间间隔
        time_columns = [col for col in df.columns if col.startswith('risk_level_')]
        max_time = max([int(col.split('_')[-1]) for col in time_columns])
        time_period_hours = max_time / 3600  # 转换为小时
        
        return jsonify({
            'status': 'success',
            'data': {
                'totalSegments': total_segments,
                'timePeriodHours': time_period_hours,
                'vulnerabilityData': df.to_dict(orient='records')
            }
        })
        
    except Exception as e:
        print(f"Error in get_vulnerability_statistics: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """检查计算服务状态"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        # 获取项目ID
        project_id = request.form.get('projectId')
        if not project_id:
            return jsonify({'success': False, 'message': 'Project ID is required'}), 400

        # 使用现有的目录结构
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)

        # 处理 GeoJSON 文件
        if 'geojson' in request.files:
            geojson_file = request.files['geojson']
            geojson_path = input_dir / 'roadnetwork.geojson'
            geojson_file.save(str(geojson_path))

        # 处理 ZIP 文件
        if 'inundation' in request.files:
            zip_file = request.files['inundation']
            zip_path = input_dir / 'flooding_output.zip'
            zip_file.save(str(zip_path))

        print(f"Project ID: {project_id}")
        print(f"Input Directory: {input_dir}")
        print(f"Output Directory: {output_dir}")

        return jsonify({
            'success': True,
            'message': 'Files uploaded successfully',
            'projectId': project_id,
            'paths': {
                'input': str(input_dir),
                'output': str(output_dir)
            }
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")  # 用于调试
        return jsonify({
            'success': False,
            'message': f'Failed to upload files: {str(e)}'
        }), 500

@app.route('/api/upload-building', methods=['POST'])
def upload_building():
    try:
        project_id = request.form.get('projectId')
        if not project_id:
            return jsonify({'success': False, 'message': 'Project ID is required'}), 400

        if 'building' not in request.files:
            return jsonify({'success': False, 'message': 'No building file provided'}), 400

        buildings_file = request.files['building']
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        # 保存 buildings 文件
        buildings_path = input_dir / 'building.geojson'
        buildings_file.save(str(buildings_path))

        return jsonify({
            'success': True,
            'message': 'Buildings file uploaded successfully'
        })

    except Exception as e:
        print(f"Upload buildings error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to upload buildings file: {str(e)}'
        }), 500

@app.route('/api/check-files/<project_id>', methods=['GET'])
def check_files(project_id):
    try:
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        return jsonify({
            'hasRoadNetworks': (input_dir / 'roadnetwork.geojson').exists(),
            'hasInundationMap': (input_dir / 'flooding_output.zip').exists(),
            'hasBuildings': (input_dir / 'building.geojson').exists()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-files-2/<project_id>', methods=['GET'])
def check_calculation_files(project_id):
    try:
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        return jsonify({
            'hasTopologyCalculation': (output_dir / '002_topology_calculation').exists(),
            'hasMatsimCalculation': (output_dir / '003_matsim_calculation').exists(),
            'hasMergedData': (output_dir / '004_merged_data').exists()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/network', methods=['GET'])
def get_topology_network():
    print("=== Starting get_topology_network ===")  # 添加这行
    try:
        project_id = request.args.get('project_id')
        print("Project ID from request:", project_id, file=sys.stderr)  # 修改这行
        
        if not project_id:
            print("No project ID provided", file=sys.stderr)  # 添加这行
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        geojson_path = output_dir / '002_topology_calculation' / 'out_network.geojson'
        
        print(f"File path: {geojson_path}", file=sys.stderr)  # 添加这行
        print(f"File exists: {geojson_path.exists()}", file=sys.stderr)  # 添加这行
        
        if not geojson_path.exists():
            print("File not found!", file=sys.stderr)  # 添加这行
            return jsonify({
                'status': 'error', 
                'message': f'Topology calculation result not found at {geojson_path}'
            }), 404
            
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
            
        return jsonify(geojson_data)
        
    except Exception as e:
        print(f"Error in get_topology_network: {str(e)}", file=sys.stderr)  # 修改这行
        import traceback  # 添加这行
        print(traceback.format_exc(), file=sys.stderr)  # 添加这行
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/topology/dynamic_networks', methods=['GET'])
def get_dynamic_networks():
    print("=== Starting get_dynamic_networks ===", file=sys.stderr)
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        topology_dir = output_dir / '002_topology_calculation'
        
        # 查找所有 out_network_{time}.geojson 文件
        network_files = list(topology_dir.glob('out_network_*.geojson'))
        
        # 提取时间点
        time_points = []
        for file in network_files:
            import re
            match = re.search(r'out_network_h_(\d+)\.geojson', file.name)
            if match:
                time_points.append(int(match.group(1)))
        
        time_points.sort()  # 确保时间点有序
        print(f"Found time points: {time_points}", file=sys.stderr)
        
        return jsonify({
            'status': 'success',
            'timePoints': time_points
        })
        
    except Exception as e:
        print(f"Error in get_dynamic_networks: {str(e)}", file=sys.stderr)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/topology/network_at_time', methods=['GET'])
def get_network_at_time():
    print("=== Starting get_network_at_time ===", file=sys.stderr)
    try:
        project_id = request.args.get('project_id')
        time_point = request.args.get('time')
        
        if not project_id or time_point is None:
            return jsonify({'status': 'error', 'message': 'Project ID and time point are required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        geojson_path = output_dir / '002_topology_calculation' / f'out_network_h_{time_point}.geojson'
        
        print(f"Loading file from: {geojson_path}", file=sys.stderr)
        
        if not geojson_path.exists():
            return jsonify({
                'status': 'error',
                'message': f'Network file not found for time point {time_point}'
            }), 404
        
        # 使用 geopandas 读取 GeoJSON
        gdf = gpd.read_file(geojson_path)
        # print(gdf.count_geometries())
        
        # 转换坐标系从 EPSG:27700 到 EPSG:4326
        gdf = gdf.to_crs(CRS.from_epsg(4326))
        
        # 转换回 GeoJSON
        geojson_data = gdf.__geo_interface__
        
        print("Coordinate conversion completed", file=sys.stderr)
        
        return jsonify(geojson_data)
        
    except Exception as e:
        print(f"Error in get_network_at_time: {str(e)}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/transportation/basic-stats', methods=['GET'])
def get_transportation_basic_stats():
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        # 读取 facilities.csv
        facilities_path = output_dir / '003_matsim_calculation' / 'facilities.csv'
        facilities_df = pd.read_csv(facilities_path)
        
        # 读取 population.csv
        population_path = output_dir / '003_matsim_calculation' / 'population.csv'
        population_df = pd.read_csv(population_path)
        
        # 1. 计算建筑物总数
        total_buildings = len(facilities_df)
        
        # 2. 计算土地利用分布
        land_use_distribution = facilities_df['siteType'].value_counts().to_dict()
        
        # 3. 计算交通方式分布
        transport_modes = []
        for col in ['trans01', 'trans02', 'trans03']:
            transport_modes.extend(population_df[col].tolist())
        transport_distribution = Counter(transport_modes)
        
        # 4. 计算年龄结构分布
        age_distribution = population_df['age'].value_counts().to_dict()
        
        return jsonify({
            'status': 'success',
            'data': {
                'totalBuildings': total_buildings,
                'landUseDistribution': [
                    {'name': k, 'value': v} 
                    for k, v in land_use_distribution.items()
                ],
                'vehicleTypeDistribution': [
                    {'name': k, 'value': v} 
                    for k, v in transport_distribution.items()
                ],
                'ageStructure': [
                    {'name': k, 'value': v} 
                    for k, v in age_distribution.items()
                ]
            }
        })
        
    except Exception as e:
        print(f"Error in get_transportation_basic_stats: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/transportation/simulation-stats', methods=['GET'])
def get_transportation_simulation_stats():
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        matsim_output_dir = output_dir / '003_matsim_calculation' / 'output_traffic'
        
        # 1. 读取 Iteration Score 数据
        scores_file = matsim_output_dir / 'scorestats.txt'
        scores_data = []
        with open(scores_file, 'r') as f:
            next(f)  # 跳过标题行
            for line in f:
                iteration, executed, worst, avg, best = line.strip().split('\t')
                scores_data.append({
                    'iteration': int(iteration),
                    'executed': float(executed),
                    'worst': float(worst),
                    'avg': float(avg),
                    'best': float(best)
                })
        
        # 2. 读取 Leg Duration 数据
        leg_duration_file = matsim_output_dir / 'ITERS' / 'it.5' / '5.legdurations.txt'
        leg_durations = []
        with open(leg_duration_file, 'r') as f:
            headers = next(f).strip().split('\t')  # 获取时间区间
            for line in f:
                data = line.strip().split('\t')
                pattern = data[0]
                values = [int(x) for x in data[1:]]
                leg_durations.append({
                    'pattern': pattern,
                    'durations': dict(zip(headers[1:], values))
                })
        
        # 3. 读取 Traffic Flow 数据
        traffic_file = matsim_output_dir / 'ITERS' / 'it.5' / '5.legHistogram.txt'
        traffic_flow = []
        with open(traffic_file, 'r') as f:
            next(f)  # 跳过标题行
            for line in f:
                data = line.strip().split('\t')
                time = data[1]  # 使用秒数而不是时间字符串
                traffic_flow.append({
                    'time': int(time),
                    'departures': int(data[2]),
                    'arrivals': int(data[3]),
                    'enRoute': int(data[5])
                })
        
        return jsonify({
            'status': 'success',
            'data': {
                'duration': '24 hours',
                'iterationScores': scores_data,
                'legDurations': leg_durations,
                'trafficFlow': traffic_flow
            }
        })
        
    except Exception as e:
        print(f"Error in get_transportation_simulation_stats: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/transportation/road-traffic', methods=['GET'])
def get_road_traffic_data():
    try:
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'status': 'error', 'message': 'Project ID is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(project_id)
        
        # 读取道路网络数据
        road_network_file = input_dir / 'roadnetwork.geojson'
        gdf = gpd.read_file(road_network_file)
        
        # 检查并打印当前坐标系统
        gdf.set_crs(epsg=27700, inplace=True, allow_override=True)
        print(gdf.crs)
        
        # 强制转换到EPSG:4326
        gdf = gdf.to_crs(epsg=4326)
        
        # 验证转换后的坐标系统
        print(f"Transformed CRS: {gdf.crs}")
        
        # 检查一些坐标值以确保转换正确
        print("Sample coordinates after transformation:")
        print(gdf.geometry.iloc[0])
        
        # 转换为GeoJSON并确保使用正确的坐标
        road_network = json.loads(gdf.to_json())
        
        # 验证GeoJSON中的坐标
        sample_coords = road_network['features'][0]['geometry']['coordinates']
        print(f"Sample coordinates in GeoJSON: {sample_coords}")
            
        # 读取交通流量数据
        traffic_file = output_dir / '004_merged_data' / 'traffic_flow_450s.csv'
        traffic_data = {}
        with open(traffic_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                link_id = int(row['link_id'])
                road_id = str(link_id * 2) if link_id > 0 else "0"
                traffic_data[road_id] = {
                    k: float(v) for k, v in row.items() 
                    if k.startswith('traffic_')
                }
        
        return jsonify({
            'status': 'success',
            'data': {
                'roadNetwork': road_network,
                'trafficData': traffic_data
            }
        })
        
    except Exception as e:
        print(f"Error in get_road_traffic_data: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # 确保数据根目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
