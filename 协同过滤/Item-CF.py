# 基于物品的协同过滤算法

import numpy as np
import pandas as pd
import sqlite3
from tqdm import tqdm
from itertools import combinations
from operator import itemgetter


input_path  = '数据库/input/ratings.csv'
output_path = '数据库/output/similarities.db'


# DataFram转换为字典
def trans_df2dict(df):
    user_rating = {}
    for row in df.values:
        user_id, movie_id, rating = row[0],row[1],row[2]
        if user_id not in user_rating:
            user_rating[user_id] = {}
        user_rating[user_id][movie_id] = rating
    return user_rating

# 创建电影ID到连续索引的映射
def create_movie_id_map(df):
    
    movie_ids = df['movieId'].unique()  # 所有电影ID列表
    movie_id_map = {old_id: new_id + 1 for new_id, old_id in enumerate(movie_ids)}  # 电影ID映射
    return movie_id_map # 电影ID到连续索引的映射

# 计算物品相似度
def get_items_similarity(df, item_num):

    print(f'物品数量: {item_num}')

    movie_id_map = create_movie_id_map(df)      # 创建电影ID到连续索引的映射
    inverted_table = df.groupby('userId')['movieId'].agg(lambda x: [movie_id_map[i] for i in x]).to_dict()  # 反转数据集，以用户ID为键，电影ID列表为值

    movie_id_map_inv = {v: k for k, v in movie_id_map.items()}  # 电影ID到原始ID的映射

    W = np.zeros((item_num, item_num))  # 相似度矩阵
    count_item_users_num = {movie_id_map[id]: count for id, count in
                            df.groupby('movieId')['userId'].count().to_dict().items()}  # 物品被用户观看的次数

    # 数据准备
    print('正在准备数据...')
    for key, val in tqdm(inverted_table.items()):
        for per in combinations(val, 2):
            W[per[0] - 1][per[1] - 1] += 1 
            W[per[1] - 1][per[0] - 1] += 1 

    # 计算相似度矩阵
    print('正在计算相似度矩阵...')
    for i in tqdm(range(W.shape[0])):
        for j in range(W.shape[1]):
            W[i][j] /= np.sqrt(count_item_users_num.get(i + 1) * count_item_users_num.get(j + 1))

    print('相似度矩阵计算完成！')

    # 转换为DataFrame格式
    print('正在转换为DataFrame格式...')
    W_df = pd.DataFrame(W, index=list(movie_id_map_inv.values()), columns=list(movie_id_map_inv.values()))  # 转换为DataFrame格式

    # 将稀疏矩阵转换为长格式数据框
    print('正在转换为长格式数据框...')
    long_format_df = W_df.stack().reset_index()
    long_format_df.columns = ['MovieID1', 'MovieID2', 'Similarity']

    # 只保留 MovieID1 < MovieID2 的情况
    print('正在消除对称重复数据')
    long_format_df = long_format_df[long_format_df['MovieID1'] < long_format_df['MovieID2']]

    # 过滤掉相似度过低的行
    print('正在过滤掉相似度 < 0.4 的数据')
    long_format_df = long_format_df[long_format_df['Similarity'] >= 0.4]

    # 重置索引（可选，但通常是个好习惯）
    print('正在重置索引...')
    long_format_df.reset_index(drop=True, inplace=True)

    return long_format_df, movie_id_map, movie_id_map_inv

# 计算用户对物品的兴趣度
def user_interest_with_items(user_id, item_id, K, user_rating, w_dict, movie_id_map):
    item_id_mapped = movie_id_map[item_id]
    interest = 0
    print(f"Processing item ID: {item_id} -> Mapped ID: {item_id_mapped}")
    for i in sorted(w_dict[item_id_mapped], key=itemgetter(1), reverse=True)[:K]:
        item_index, item_simi = i
        original_item_index = movie_id_map_inv[item_index]
        if item_index in user_rating[user_id]:
            print(f"  Similar Item ID: {original_item_index}, Similarity: {item_simi}, User Rating: {user_rating[user_id][item_index]}")
            interest += item_simi * user_rating[user_id][item_index]
    # 调试输出：打印计算出的兴趣度
    print(f"Calculated interest for user {user_id} and item {item_id}: {interest}")

    return interest

# 计算用户兴趣列表
def get_user_interest_list(user_id, K, user_rating, w_dict, movie_id_map_inv):
    rank = []
    for item_id_mapped in w_dict.keys():
        item_id = movie_id_map_inv[item_id_mapped]
        print(item_id)
        if item_id in user_rating[user_id]:
            continue
        interest = user_interest_with_items(user_id, item_id, K, user_rating, w_dict, movie_id_map)
        rank.append((item_id, interest))
    return sorted(rank, key=itemgetter(1), reverse=True)


if __name__ == '__main__':

    df = pd.read_csv(input_path)        # 读取数据集
    item_num = df.movieId.nunique()     # 物品数量
    user_rating = trans_df2dict(df)     # 转换为字典格式
    long_format_df, movie_id_map, movie_id_map_inv = get_items_similarity(df, item_num)      # 计算物品相似度
    print('正在写入数据库...')
    conn = sqlite3.connect(output_path)                                                      # 连接SQLite数据库
    long_format_df.to_sql(name='similarities', con=conn, if_exists='replace', index=False)   # 保存相似度矩阵到数据库
    print('\n[similarities]\n')
    print(long_format_df)
    conn.close()
    