import pandas as pd
import geopandas as gpd
import os
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional
import json

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

def process_topology_data(topology_dir: str) -> pd.DataFrame:
    """
    处理拓扑数据，使用geopandas读取geojson文件并合并所有水位情况下的数据
    """
    all_data = {}  # 使用字典存储，key为CurveID
    metrics = set()
    
    # 首先收集所有可能的度量指标
    for file in sorted(Path(topology_dir).glob('out_network_h_*.geojson')):
        gdf = gpd.read_file(file)
        metrics.update(gdf.columns)
    
    # 过滤出MC_相关的指标并排序
    mc_metrics = sorted([m for m in metrics if m.startswith('MC_')])
    
    # 处理每个水位的文件
    for file in sorted(Path(topology_dir).glob('out_network_h_*.geojson')):
        height = file.stem.split('_h_')[1]  # 提取水位高度
        gdf = gpd.read_file(file)
        
        for _, row in gdf.iterrows():
            curve_id = row.get('CurveId', -1)
            
            if curve_id not in all_data:
                all_data[curve_id] = {'CurveId': curve_id}
            
            # 为每个MC指标添加时间前缀，使用get方法并设置默认值为0
            for metric in mc_metrics:
                metric_value = row.get(metric, 0)  # 如果值不存在，默认为0
                all_data[curve_id][f"{metric}_{height}"] = metric_value if pd.notna(metric_value) else 0  # 确保NaN也被转换为0

    # 转换为DataFrame
    df = pd.DataFrame(list(all_data.values()))
    
    # 获取所有MC列名并按照水位高度数值排序
    mc_columns = [col for col in df.columns if col.startswith('MC_')]
    mc_columns = sorted(mc_columns, key=lambda x: float(x.split('_')[-1]))
    
    # 重新排列列顺序：先是CurveId，然后是排序后的MC列，最后是其他列
    other_columns = [col for col in df.columns if not col.startswith('MC_') and col != 'CurveId']
    new_column_order = ['CurveId'] + mc_columns + other_columns
    
    # 按新的列顺序重排DataFrame
    df = df[new_column_order]
    
    # 填充所有NaN值为0
    df = df.fillna(0)
    
    return df

def process_traffic_data(traffic_file: str, start_time: str = "7:00") -> pd.DataFrame:
    """
    处理交通流量数据，截取指定时间段的数据
    
    Parameters:
    -----------
    traffic_file : str
        交通流量CSV文件路径
    start_time : str
        开始时间，格式为"HH:MM"
    
    Returns:
    --------
    pd.DataFrame
        处理后的交通流量数据
    """
    # 读取交通流量数据
    df = pd.read_csv(traffic_file)
    
    # 将开始时间转换为秒数
    hours, minutes = map(int, start_time.split(':'))
    start_seconds = (hours * 3600 + minutes * 60)
    
    # 选择开始时间后的2小时数据
    time_columns = [col for col in df.columns if col != 'link_id']
    # 从列名中移除 'traffic_' 前缀并转换为整数
    time_columns = [int(col.replace('traffic_', '')) for col in time_columns]
    selected_columns = [col for col in time_columns 
                       if start_seconds <= int(col) <= start_seconds + 7200]
    
    # 选择相关列，添加回 'traffic_' 前缀
    result_df = df[['link_id'] + [f'traffic_{str(col)}' for col in selected_columns]]
    
    return result_df

def merge_data(topology_dir: str, 
               traffic_file: str, 
               output_dir: str,
               start_time: str = "7:00",
               output_filename: Optional[str] = None) -> bool:
    """
    合并拓扑数据和交通流量数据
    """
    try:
        logger = setup_logger(output_dir)
        logger.info("开始合并数据")
        
        # 创建输出目录
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理拓扑数据
        logger.info("处理拓扑数据")
        topology_df = process_topology_data(topology_dir)
        topology_df.to_csv(os.path.join(output_dir, 'processed_topology_data.csv'), index=False)
        
        # 处理交通流量数据
        logger.info("处理交通流量数据")
        traffic_df = process_traffic_data(traffic_file, start_time)
        traffic_df.to_csv(os.path.join(output_dir, 'processed_traffic_data.csv'), index=False)

        # 转换traffic_df的link_id为对应的CurveID
        traffic_df['CurveId'] = traffic_df['link_id'] // 2
        
        # 合并数据
        logger.info("合并数据集")
        merged_df = pd.merge(
            topology_df,
            traffic_df,
            on='CurveId',
            how='left'
        )
        
        # 生成输出文件名
        if output_filename is None:
            output_filename = f"merged_output.csv"
        
        # 保存结果
        output_path = output_dir / output_filename
        merged_df.to_csv(output_path, index=False)
        logger.info(f"数据合并完成，已保存到: {output_path}")
        
        return True
        
    except Exception as e:
        logger.exception(f"合并数据时发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    # 示例使用
    topology_dir = r'src/assets/sample_data/output/002_topology_calculation'
    traffic_file = r'src/assets/sample_data/output/004_merged_data/traffic_flow_450s.csv'
    output_dir = r'src/assets/sample_data/output/004_merged_data'
    
    success = merge_data(
        topology_dir=topology_dir,
        traffic_file=traffic_file,
        output_dir=output_dir,
        start_time="7:00"
    )
    
    if success:
        print("数据处理完成")
    else:
        print("数据处理失败")
