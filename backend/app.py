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

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'  # 所有计算任务的根目录

def ensure_task_directories(task_id):
    """确保任务相关的目录存在"""
    task_dir = DATA_DIR / str(task_id)
    input_dir = task_dir / 'input'
    output_dir = task_dir / 'output'
    
    # 创建目录
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
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        input_dir = data.get('input_dir', str(output_dir / '001_inundate_roadnetwork'))
        radii = data.get('radii', "100")
        
        success = calculate_space_syntax_for_each_file(
            input_dir=input_dir,
            output_base_folder=str(output_dir),
            radii=radii
        )
        print(success)
        if success:
            return jsonify({'status': 'success', 'message': 'Space syntax calculation completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Space syntax calculation failed'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/calculate-space-syntax-single', methods=['POST'])
def api_calculate_space_syntax_single():
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        if not task_id:
            return jsonify({'status': 'error', 'message': 'task_id is required'}), 400
            
        task_dir, input_dir, output_dir = ensure_task_directories(task_id)
        
        # 使用上传的原始 GeoJSON 文件路径
        input_file = str(input_dir / 'roadnetwork.geojson')
        if not os.path.exists(input_file):
            return jsonify({'status': 'error', 'message': 'Input GeoJSON file not found'}), 400
        
        # 创建输出目录
        output_folder = output_dir / '002_topology_calculation'
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # 设置输出文件路径
        output_file = str(output_folder / 'out_network.geojson')
        
        # 执行计算
        success = calculate_space_syntax(
            input_file,  # 直接使用输入文件路径
            output_file, # 直接使用输出文件路径
            radii="100"
        )
        
        if success:
            return jsonify({'status': 'success', 'message': 'Space syntax calculation completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Space syntax calculation failed'})
            
    except Exception as e:
        print(f"Error in calculate_space_syntax_single: {str(e)}")  # 添加错误日志
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

if __name__ == '__main__':
    # 确保数据根目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
