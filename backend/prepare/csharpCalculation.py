import subprocess
import os
import sys

def calculate_space_syntax(input_geojson, output_csv, radii="500,1000,1500,-1"):
    """
    调用C#编写的SpaceSyntaxApp.exe进行空间句法计算
    
    Parameters:
    -----------
    input_geojson : str
        输入GeoJSON文件的路径
    output_csv : str
        输出CSV文件的路径
    radii : str, optional
        计算半径，默认为"500,1000,1500,-1"，其中-1表示全局范围
        
    Returns:
    --------
    bool
        计算是否成功
    """
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # SpaceSyntaxApp.exe的路径（假设在同一目录下）
        exe_path = os.path.join(current_dir, "SpaceSyntaxApp.exe")
        
        # 确保exe文件存在
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"找不到执行文件: {exe_path}")
            
        # 构建命令
        command = [exe_path, input_geojson, output_csv, radii]
        
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

if __name__ == "__main__":
    # 命令行参数处理
    if len(sys.argv) < 3:
        print("Usage: python csharpCalculation.py <input_geojson> <output_csv> [radii]")
        print("Example: python csharpCalculation.py input.geojson output.csv \"500,1000,1500,-1\"")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    radii = sys.argv[3] if len(sys.argv) > 3 else "500,1000,1500,-1"
    
    # 执行计算
    success = calculate_space_syntax(input_file, output_file, radii)
    
    if success:
        print("calculation success")
    else:
        print("calculation failed")
