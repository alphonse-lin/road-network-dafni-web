import subprocess
import os
import sys

def calculate_space_syntax(input_geojson, output_file_path, radii="1000,2000"):
    """
    调用C#编写的TopologyCalculation.exe进行空间句法计算
    
    Parameters:
    -----------
    input_geojson : str
        输入GeoJSON文件的路径
    output_folder : str
        输出文件夹的路径
    radii : str, optional
        计算半径，默认为"1000,2000"
        
    Returns:
    --------
    bool
        计算是否成功
    """
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"topology_calc_csharp",'topology_calc')
        
        # TopologyCalculation.exe的路径
        exe_path = os.path.join(current_dir, "TopologyCalculation.exe")
        
        # 确保exe文件存在
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"找不到执行文件: {exe_path}")
            
        # 构建命令
        command = [exe_path, input_geojson, output_file_path, radii]
        print(command)

        # 执行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 打印输出信息
        print(result.stdout)
        
        # 检查是否有错误
        if result.returncode != 0:
            print("错误输出:", result.stderr)
            return False
            
        return True
        
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")
        return False

def calculate_space_syntax_for_each_file(input_dir, output_base_folder, radii):
    """
    处理目录中的所有geojson文件
    """
    # 创建输出目录
    output_folder = os.path.join(output_base_folder, "002_topology_calculation")
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历输入目录中的所有geojson文件
    for input_file in os.listdir(input_dir):
        if input_file.endswith('.geojson'):
            # 构建完整的输入文件路径
            full_input_path = os.path.join(input_dir, input_file)
            
            # 从文件名中提取水位高度信息（例如：从 network_h_450.geojson 提取 450）
            height = input_file.split('_h_')[1].split('.')[0]
            
            output_file_path = os.path.join(output_folder, f"out_{input_file}")
            print(f"Processing file: {input_file}")
            print(f"Output folder: {output_folder}")
            
            # 执行计算
            success = calculate_space_syntax(full_input_path, output_file_path, radii)
            
            if success:
                print(f"Calculation success for height {height}")
            else:
                print(f"Calculation failed for height {height}")
            
            print("-" * 50)  # 分隔线，使输出更清晰

if __name__ == "__main__":
    # 设置输入输出路径
    input_dir = r'src\assets\sample_data\output\001_inundate_roadnetwork'
    output_base_folder = r'src\assets\sample_data\output'
    radii = "1000,2000"

    calculate_space_syntax_for_each_file(input_dir, output_base_folder, radii)

