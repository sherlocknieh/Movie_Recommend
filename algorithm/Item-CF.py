# 基于物品的协同过滤算法
# 输入：用户-电影-评分数据集: data/ratings.csv
# 输出：电影-电影-相似度数据: data/similarity.csv

import numpy as np
import pandas as pd
from itertools import combinations
from operator import itemgetter
import pymysql
from sqlalchemy import create_engine

def trans_df2dict(df):
    user_rating = {}
    for row in df.values:
        user_id, movie_id, rating = row[0],row[1],row[2]
        if user_id not in user_rating:
            user_rating[user_id] = {}
        user_rating[user_id][movie_id] = rating
    return user_rating


def create_movie_id_map(df):
    # 创建电影ID到连续索引的映射
    movie_ids = df['movieId'].unique()
    movie_id_map = {old_id: new_id + 1 for new_id, old_id in enumerate(movie_ids)}
    return movie_id_map


def get_items_similarity(df, item_num):
    movie_id_map = create_movie_id_map(df)
    inverted_table = df.groupby('userId')['movieId'].agg(lambda x: [movie_id_map[i] for i in x]).to_dict()
    print(item_num)
    # 创建反向映射，用于后续查找
    movie_id_map_inv = {v: k for k, v in movie_id_map.items()}

    W = np.zeros((item_num, item_num))
    count_item_users_num = {movie_id_map[id]: count for id, count in
                            df.groupby('movieId')['userId'].count().to_dict().items()}

    for key, val in inverted_table.items():
        for per in combinations(val, 2):
            W[per[0] - 1][per[1] - 1] += 1
            W[per[1] - 1][per[0] - 1] += 1

    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            W[i][j] /= np.sqrt(count_item_users_num.get(i + 1) * count_item_users_num.get(j + 1))
    #W_df = pd.DataFrame(W, index=movie_id_map.values(), columns=movie_id_map.values())
    W_df = pd.DataFrame(W, index=list(movie_id_map_inv.values()), columns=list(movie_id_map_inv.values()))
    W_df.to_csv('/home/hadoop/similarity_matrix.csv')
    print(W)
    # 将稀疏矩阵转换为长格式数据框
    long_format_df = W_df.stack().reset_index()
    long_format_df.columns = ['MovieID1', 'MovieID2', 'Similarity']

    # 过滤掉相似度为0的行
    long_format_df = long_format_df[long_format_df['Similarity'] != 0]

    # 由于MovieID1和MovieID2是对称的，我们只需要保留一半的数据（避免重复）
    # 这里我们保留MovieID1 < MovieID2的情况
    # long_format_df = long_format_df[long_format_df['MovieID1'] < long_format_df['MovieID2']]

    # 重置索引（可选，但通常是个好习惯）
    long_format_df.reset_index(drop=True, inplace=True)

    # （可选）根据相似度排序
    long_format_df.sort_values(by='Similarity', ascending=False, inplace=True)

    # 查看结果
    print(long_format_df)

    # 如果需要，可以将结果保存到CSV文件
    long_format_df.to_csv('/home/hadoop/movie_similarity_pairs.csv', index=False)


    return long_format_df, movie_id_map, movie_id_map_inv


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

    df = pd.read_csv('../data/ratings.csv')
    item_num = df.movieId.nunique()
    user_rating = trans_df2dict(df)
    W, movie_id_map, movie_id_map_inv = get_items_similarity(df, item_num)
    print(movie_id_map)
    print(movie_id_map_inv)
    db_config = {
        'user': 'root',
        'password': '123456',
        'host': 'localhost',
        'port':3306 ,  # 通常是3306
        'database': 'Similarity'
    }

    # 创建数据库连接引擎
    engine = create_engine(
        f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}')

    # 将DataFrame上传到MySQL表（如果表不存在，则创建它）
    table_name = 'movie_similarity'
    W.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

    print(f"Data has been uploaded to the '{table_name}' table in the '{db_config['database']}' database.")