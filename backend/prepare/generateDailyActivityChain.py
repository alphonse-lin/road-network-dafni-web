import subprocess
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

def setup_logger(output_dir):
    """
    设置日志记录器
    
    Parameters:
    -----------
    output_dir : str or Path
        输出目录路径，日志文件将保存在此目录下
    """
    # 创建logs目录
    log_dir = Path(output_dir) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成带时间戳的日志文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'activity_chain_generation_{timestamp}.log'
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    return logging.getLogger(__name__)

def generate_daily_activity_chain(input_dir, output_dir):
    """
    生成日常活动链
    
    Parameters:
    -----------
    input_dir : str
        输入目录路径，需包含building.geojson和network.geojson
    output_dir : str
        输出目录路径
        
    Returns:
    --------
    bool
        计算是否成功
    """
    try:
        # 设置日志记录器
        logger = setup_logger(output_dir)
        logger.info("开始生成日常活动链")
        
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent.absolute()
        
        # 获取jar文件和index文件的路径
        jar_path = current_dir / "matsim_preparation_jar" / "generate_demand" / "matsim_preparation.jar"
        index_path = current_dir / "data" / "indexCalculation.xml"
        
        # 确保文件存在
        if not jar_path.exists():
            raise FileNotFoundError(f"找不到jar文件: {jar_path}")
        if not index_path.exists():
            raise FileNotFoundError(f"找不到index文件: {index_path}")
            
        # 确保输入文件存在
        input_dir = Path(input_dir)
        if not (input_dir / "building.geojson").exists():
            raise FileNotFoundError(f"找不到building.geojson文件: {input_dir / 'building.geojson'}")
        if not (input_dir / "network.geojson").exists():
            raise FileNotFoundError(f"找不到network.geojson文件: {input_dir / 'network.geojson'}")
            
        # 确保输出目录存在
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建命令
        command = [
            "java",
            "-jar",
            str(jar_path),
            str(input_dir) + os.path.sep,
            str(output_dir) + os.path.sep,
            str(index_path)
        ]
        
        logger.info(f"执行命令: {' '.join(command)}")
        
        # 执行命令
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # 读取输出
        stdout, stderr = process.communicate()
        
        # 记录输出
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    logger.info(f"[OUTPUT] {line.strip()}")
        
        # 记录错误
        if stderr:
            for line in stderr.split('\n'):
                if line.strip():
                    logger.error(f"[ERROR] {line.strip()}")
        
        # 检查执行结果
        if process.returncode == 0:
            logger.info("日常活动链生成完成")
            return True
        else:
            logger.error(f"日常活动链生成失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        logger.exception(f"执行过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 命令行参数处理
    if len(sys.argv) < 3:
        print("Usage: python generateDailyActivityChain.py <input_dir> <output_dir>")
        print("Example: python generateDailyActivityChain.py ./input ./output")
        sys.exit(1)
        
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 执行计算
    success = generate_daily_activity_chain(input_dir, output_dir)
    
    sys.exit(0 if success else 1)
