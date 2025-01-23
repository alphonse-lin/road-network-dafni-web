from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np
import pandas as pd
import os
from collections import Counter

#TODO: 需要验证
def dtw_matching(input_csv_path, output_csv_path=None):
    """
    对交通流数据进行DTW匹配分析
    
    Parameters:
    -----------
    input_csv_path : str
        输入CSV文件的路径，文件应包含link_id和计数数据
    output_csv_path : str, optional
        输出CSV文件的路径，如果不指定则使用输入文件路径加上"_dtw_matching.csv"
    
    Returns:
    --------
    pd.DataFrame
        包含匹配结果的DataFrame
    """
    try:
        # 读取csv文件
        data = pd.read_csv(input_csv_path)
        
        if output_csv_path is None:
            # 自动生成输出文件路径
            file_base = os.path.splitext(input_csv_path)[0]
            output_csv_path = f"{file_base}_dtw_matching.csv"

        results = []
        idx_list = []
        match_list = []
        best_sequences_df = pd.DataFrame()
        reference_sequence_df = pd.DataFrame()

        # 循环遍历每一行数据
        for row_index in range(data.shape[0]):
            # 获取当前行的参考序列和待匹配的序列
            reference_data = data.iloc[row_index, list(range(1, 18))]
            reference_sequence = reference_data.values
            
            sequences_indices = [
                list(range(18, 35)),
                list(range(35, 52)),
                list(range(52, 69)),
                list(range(69, 86)),
                list(range(86, 103)),
            ]

            sequences = [data.iloc[row_index, indices].values for indices in sequences_indices]

            # 寻找最佳匹配
            min_distance = float('inf')
            best_match_index = -1
            best_sequence = None
            
            for idx, seq in enumerate(sequences):
                distance, _ = fastdtw(reference_sequence, seq, dist=euclidean)
                if distance < min_distance:
                    min_distance = distance
                    best_match_index = idx
                    best_sequence = seq

            idx_list.append(data.iloc[row_index]['link_id'])
            match_list.append(best_match_index)
            
            # 保存最佳匹配序列和参考序列
            temp_df = pd.DataFrame(best_sequence).T
            best_sequences_df = pd.concat([best_sequences_df, temp_df], ignore_index=True)
            reference_sequence_df = pd.concat([reference_sequence_df, pd.DataFrame(reference_sequence).T], ignore_index=True)

        # 创建输出DataFrame
        export_data = pd.DataFrame({
            'link_id': idx_list,
            'match_idx': match_list
        })

        # 设置参考序列的列名
        reference_sequence_df.columns = data.columns[1:18]
        
        # 合并所有结果
        final_export_data = pd.concat([export_data, reference_sequence_df, best_sequences_df], axis=1)

        # 保存结果
        final_export_data.to_csv(output_csv_path, index=False)
        print(f'DTW匹配分析完成，结果已保存至: {output_csv_path}')
        
        return final_export_data

    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return None

if __name__ == '__main__':
    # 使用示例
    input_file = "path/to/your/input/link_count.csv"
    output_file = "path/to/your/output/dtw_matching_result.csv"  # 可选
    
    # 方式1：指定输入和输出路径
    result_df = dtw_matching(input_file, output_file)
    
    # 方式2：只指定输入路径，输出文件将自动生成
    # result_df = dtw_matching(input_file)
