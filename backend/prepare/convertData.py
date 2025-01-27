import gzip
from lxml import etree
import pandas as pd
from collections import defaultdict
import os

def extract_traffic_flow(events_file_path, time_step=450):
    """
    从Matsim事件文件中提取交通流量数据
    
    Parameters:
    -----------
    events_file_path : str
        events.xml.gz文件的路径
    time_step : int, optional
        时间间隔（秒），默认450秒
        
    Returns:
    --------
    pandas.DataFrame
        包含每个时间间隔内每条道路的交通流量
    """
    try:
        # 读取压缩的XML文件
        with gzip.open(events_file_path, 'rb') as gz:
            events = etree.fromstring(gz.read())
            
        # 初始化交通流量计数器
        link_counts = defaultdict(lambda: defaultdict(int))
        
        # 遍历所有事件
        for event in events:
            attrib = event.attrib
            
            # 只处理"进入道路"事件
            if attrib['type'] == 'entered link':
                event_time = float(attrib['time'])
                time_interval = int(event_time // time_step) * time_step
                link_id = int(attrib['link'])
                
                # 计数加1
                link_counts[time_interval][link_id] += 1
        
        # 转换为DataFrame格式
        data = [
            [time_interval, link_id, count]
            for time_interval, links in link_counts.items()
            for link_id, count in links.items()
        ]
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=['time_interval', 'link_id', 'count'])
        
        # 转换为透视表格式
        pivot_df = df.pivot(
            index='link_id',
            columns='time_interval',
            values='count'
        ).fillna(0)
        
        # 确保所有link_id都存在
        all_links = range(0, pivot_df.index.max() + 1)
        pivot_df = pivot_df.reindex(all_links).fillna(0)
        
        return pivot_df
        
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")
        return None

def process_matsim_output(input_dir):
    matsim_dir = os.path.join(input_dir, "003_matsim_calculation")
    output_dir = os.path.join(input_dir, "004_merged_data")
    os.makedirs(output_dir, exist_ok=True)
    """
    处理Matsim输出目录中的所有迭代结果
    
    Parameters:
    -----------
    matsim_dir : str
        Matsim输出目录路径
    output_dir : str
        结果保存目录
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取最后一次迭代的events文件
        iters_dir = os.path.join(matsim_dir, 'output_traffic', 'ITERS')
        last_iter = max(int(x.split('.')[1]) for x in os.listdir(iters_dir) if x.startswith('it.'))
        events_file = os.path.join(iters_dir, f'it.{last_iter}', f'{last_iter}.events.xml.gz')
        
        # 提取交通流量数据
        traffic_flow_df = extract_traffic_flow(events_file)
        
        if traffic_flow_df is not None:
            # 保存结果
            output_file = os.path.join(output_dir, 'traffic_flow_450s.csv')
            traffic_flow_df.to_csv(output_file)
            print(f"交通流量数据已保存到: {output_file}")
            return True
            
        return False
        
    except Exception as e:
        print(f"处理Matsim输出时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    input_dir = r'src/assets/sample_data/output'
    
    success = process_matsim_output(input_dir)
    
    if success:
        print("数据处理完成")
    else:
        print("数据处理失败")
