from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np
import pandas as pd
import os
from collections import Counter
from itertools import product
from tqdm import tqdm  # 用于进度条
from joblib import Parallel, delayed  # 用于并行计算

def dtw_matching(input_csv_path, output_csv_path=None, n_jobs=-1):
    """
    对交通流数据进行DTW匹配分析，支持多MC序列组合匹配
    
    Parameters:
    -----------
    input_csv_path : str
        输入CSV文件的路径
    output_csv_path : str, optional
        输出CSV文件的路径
    n_jobs : int, optional
        并行计算的线程数，-1表示使用所有可用的CPU核心
    
    Returns:
    --------
    pd.DataFrame
        包含匹配结果的DataFrame
    """
    # 读取csv文件
    data = pd.read_csv(input_csv_path)
    
    if output_csv_path is None:
        file_base = os.path.splitext(input_csv_path)[0]
        output_csv_path = f"{file_base}_dtw_matching.csv"

    # 获取所有MC前缀（1000, 2000, 3000, -1）
    mc_prefixes = sorted(list(set([col.split('_')[1] for col in data.columns if col.startswith('MC_')])))
    
    # 获取所有时间点
    time_points = sorted(list(set([int(col.split('_')[2]) for col in data.columns if col.startswith('MC_')])))
    
    # 获取目标序列的列名（25200-32400）
    target_columns = [col for col in data.columns if col.startswith('traffic_')]

    results = []
    
    # 对每一行数据进行处理
    def process_row(row_index):
        target_sequence = data.iloc[row_index][target_columns].values
        link_id = data.iloc[row_index]['link_id']
        
        # 为每个时间点创建可能的MC值列表
        time_series_combinations = []
        for time_point in time_points:
            mc_values = []
            for prefix in mc_prefixes:
                col_name = f'MC_{prefix}_{time_point}'
                if col_name in data.columns:
                    mc_values.append(data.iloc[row_index][col_name])
            time_series_combinations.append(mc_values)
        
        # 使用动态规划方法查找最佳组合
        dp = [{} for _ in range(len(time_points))]
        
        # 初始化第一个时间点
        for i, value in enumerate(time_series_combinations[0]):
            sequence = np.asarray([float(value)], dtype=np.float64)  # 明确指定类型和格式
            target = np.asarray([float(target_sequence[0])], dtype=np.float64)
            distance, _ = fastdtw(sequence, target, dist=2)
            dp[0][i] = (distance, [value])
        
        # 动态规划填充
        for t in range(1, len(time_points)):
            for curr_idx, curr_value in enumerate(time_series_combinations[t]):
                min_prev_distance = float('inf')
                best_prev_sequence = None
                
                for prev_idx in dp[t-1]:
                    prev_distance, prev_sequence = dp[t-1][prev_idx]
                    new_sequence = np.array(prev_sequence + [curr_value]).reshape(-1)  # 确保是1维数组
                    target = target_sequence[:t+1].reshape(-1)  # 确保是1维数组
                    distance, _ = fastdtw(new_sequence, target, dist=2)
                    
                    if distance < min_prev_distance:
                        min_prev_distance = distance
                        best_prev_sequence = new_sequence.tolist()
                
                if best_prev_sequence is not None:
                    dp[t][curr_idx] = (min_prev_distance, best_prev_sequence)
        
        # 找到最佳组合
        final_min_distance = float('inf')
        best_sequence = None
        
        for idx in dp[-1]:
            distance, sequence = dp[-1][idx]
            if distance < final_min_distance:
                final_min_distance = distance
                best_sequence = sequence
        
        # 保存结果
        result_dict = {
            'link_id': link_id,
            'dtw_distance': final_min_distance
        }
        
        # 添加最佳匹配序列
        for i, value in enumerate(best_sequence):
            result_dict[f'MC_{time_points[i]}'] = value
            
        # 添加目标序列
        for i, value in enumerate(target_sequence):
            result_dict[f'traffic_{target_columns[i]}'] = value
            
        return result_dict
    
    # 使用并行计算处理每一行数据
    results = Parallel(n_jobs=n_jobs)(delayed(process_row)(row_index) for row_index in tqdm(range(len(data)), desc="Processing rows"))
    
    # 创建结果DataFrame并保存
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv_path, index=False)
    print(f'DTW匹配分析完成，结果已保存至: {output_csv_path}')
    
    return result_df

if __name__ == '__main__':
    # 使用示例
    input_file = r"src\assets\sample_data\output\004_merged_data\merged_output.csv"
    output_file = r"src\assets\sample_data\output\004_merged_data\dtw_matching_result.csv"  # 可选
    
    # 方式1：指定输入和输出路径
    result_df = dtw_matching(input_file, output_file, n_jobs=-1)