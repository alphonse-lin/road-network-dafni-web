import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional
import sys

def setup_logger(output_dir: str) -> logging.Logger:
    """
    设置日志记录器
    
    Parameters:
    -----------
    output_dir : str
        输出目录路径
    
    Returns:
    --------
    logging.Logger
        配置好的日志记录器
    """
    log_dir = Path(output_dir) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'merge_data_{timestamp}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def merge_data(matsim_file: str, 
               choice_dir: str, 
               output_dir: str, 
               output_filename: Optional[str] = None) -> bool:
    """
    合并MATSim输出数据和Space Syntax计算结果
    
    Parameters:
    -----------
    matsim_file : str
        MATSim输出的linkstats.csv文件路径
    choice_dir : str
        包含Space Syntax计算结果的目录路径
    output_dir : str
        输出目录路径
    output_filename : str, optional
        输出文件名，如果不指定则根据输入文件自动生成
        
    Returns:
    --------
    bool
        合并是否成功
    """
    try:
        logger = setup_logger(output_dir)
        logger.info("开始合并数据")
        
        # 创建输出目录
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取MATSim数据
        logger.info(f"读取MATSim数据: {matsim_file}")
        excel_data = pd.read_csv(matsim_file)
        
        # 读取Space Syntax数据
        logger.info(f"读取Space Syntax数据目录: {choice_dir}")
        choice_files = sorted(
            Path(choice_dir).glob('*.csv'),
            key=lambda f: int(''.join(filter(str.isdigit, f.name)))
        )
        
        if not choice_files:
            raise FileNotFoundError(f"在目录中未找到CSV文件: {choice_dir}")
            
        # 处理每个Space Syntax结果文件
        csv_data_list = []
        for file in choice_files:
            logger.info(f"处理文件: {file.name}")
            temp_df = pd.read_csv(file)[['id',
                'M_h_0_depth', 'M_h_450_depth','M_h_900_depth', 'M_h_1350_depth',
                'M_h_1800_depth', 'M_h_2250_depth','M_h_2700_depth','M_h_3150_depth','M_h_3600_depth',
                'M_h_4050_depth', 'M_h_4500_depth','M_h_4950_depth', 'M_h_5400_depth',
                'M_h_5850_depth', 'M_h_6300_depth','M_h_6750_depth','M_h_7200_depth']]
            
            tag = file.stem.split('_')[0]
            csv_data = temp_df.add_prefix(f'{tag}_')
            
            # 复制数据以匹配MATSim输出
            csv_data_duplicated = pd.concat([csv_data, csv_data]).sort_index().reset_index(drop=True)
            csv_data_list.append(csv_data_duplicated)
        
        # 合并所有数据
        logger.info("合并数据集")
        merged_data = excel_data
        for i, csv_data in enumerate(csv_data_list):
            columns_to_drop = [col for col in csv_data.columns if 'id' in col]
            csv_data_2 = csv_data.drop(columns=columns_to_drop)
            merged_data = pd.concat([merged_data, csv_data_2], axis=1)
        
        # 生成输出文件名
        if output_filename is None:
            output_filename = f"merged_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 保存结果
        output_path = output_dir / output_filename
        merged_data.to_csv(output_path, index=False)
        logger.info(f"数据合并完成，已保存到: {output_path}")
        
        return True
        
    except Exception as e:
        logger.exception(f"合并数据时发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    # 命令行参数处理
    if len(sys.argv) < 4:
        print("Usage: python mergeData.py <matsim_file> <choice_dir> <output_dir> [output_filename]")
        print("Example: python mergeData.py linkstats.csv ./choice_data ./output merged_result.csv")
        sys.exit(1)
        
    matsim_file = sys.argv[1]
    choice_dir = sys.argv[2]
    output_dir = sys.argv[3]
    output_filename = sys.argv[4] if len(sys.argv) > 4 else None
    
    # 执行合并
    success = merge_data(matsim_file, choice_dir, output_dir, output_filename)
    
    sys.exit(0 if success else 1)
