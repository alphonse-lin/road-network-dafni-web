import subprocess
import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import shutil

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
    log_file = log_dir / f'matsim_simulation_{timestamp}.log'
    
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

def run_matsim(input_dir):
    """
    运行MATSim交通模拟
    
    Parameters:
    -----------
    input_dir : str
        输入目录路径，配置文件将被复制到此目录
        
    Returns:
    --------
    bool
        模拟是否成功
    """
    try:
        # 设置日志记录器
        logger = setup_logger(input_dir)
        logger.info("开始运行MATSim模拟")
        
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent.absolute()
        
        # 获取jar文件和默认配置文件的路径
        jar_path = current_dir / "matsim_preparation_jar" / "traffic_sim" / "matsim_preparation.jar"
        default_config_path = current_dir / "matsim_preparation_jar" / "config.xml"
        
        # 确保文件存在
        if not jar_path.exists():
            raise FileNotFoundError(f"找不到jar文件: {jar_path}")
        if not default_config_path.exists():
            raise FileNotFoundError(f"找不到默认配置文件: {default_config_path}")
            
        # 创建输入目录（如果不存在）
        input_dir = Path(input_dir)
        input_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制配置文件到输入目录
        config_path = input_dir / "config_tran_sim.xml"
        shutil.copy2(default_config_path, config_path)
        logger.info(f"配置文件已复制到: {config_path}")
        
        # 构建命令
        command = [
            "java",
            "-jar",
            str(jar_path),
            str(config_path)
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
            logger.info("MATSim模拟完成")
            return True
        else:
            logger.error(f"MATSim模拟失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        logger.exception(f"执行过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # # 命令行参数处理
    # if len(sys.argv) < 2:
    #     print("Usage: python runMatsim.py <input_dir>")
    #     print("Example: python runMatsim.py ./simulation_input")
    #     sys.exit(1)
        
    # input_dir = sys.argv[1]
    input_dir = r'src\assets\sample_data\output\003_matsim_calculation'
    
    # 执行模拟
    success = run_matsim(input_dir)
    
    sys.exit(0 if success else 1)
