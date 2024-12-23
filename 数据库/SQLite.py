import pandas as pd
import sqlite3


# 相关文件路径
input_file1 = '数据库/input/links.csv'
input_file2 = '数据库/input/movies.csv'
movies_data = '数据库/output/movies.db'
similarity_data = '数据库/output/similarities.db'


# 建立 similarities.db 数据库
def creat_similarities_sqlite():

    # 打开/创建数据库
    conn = sqlite3.connect(similarity_data)
    
    # 创建 similarities 空表 (如果已存在则不创建)
    conn.execute('''CREATE TABLE IF NOT EXISTS similarities (
                   movieId1     INT,
                   movieId2     INT,
                   Similarity   REAL
                   )''')  # similarities 表格包含 movieId1, movieId2, Similarity 三列数据
    
    # 提交修改
    conn.commit()

    # 关闭数据库
    conn.close()  

# 建立 movies.db 数据库
# 1. 创建 movies_basic 表
def creat_movies_basic_table():

    # 创建 movies.db 数据库并打开
    conn = sqlite3.connect(movies_data)      

    # 读取 links.csv 和 movies.csv 文件
    df1 = pd.read_csv(input_file1, dtype={'imdbId': str, 'tmdbId': str}) # imdbId, tmdbId 读取为字符串类型
    df2 = pd.read_csv(input_file2)

    # 合并两张表
    df = pd.merge(df1, df2, on='movieId')

    # 写入 movies_basic 表
    df.to_sql('movies_basic', conn, if_exists='replace', index=False)

    # 提交修改
    conn.commit()
    
    # 关闭数据库
    conn.close()

# 2. 创建 movies_detail 表
def creat_movies_detail_table():
    
    # 打开 movies.db 数据库
    conn = sqlite3.connect(movies_data)

    # 新建 movies_detail 表 (如果已存在则不创建)
    conn.execute('''CREATE TABLE IF NOT EXISTS movies_detail (
                   movieId      INT,
                   title_CN     TEXT,
                   release_date TEXT,
                   vote_average REAL,
                   vote_count   INT,
                   poster_path  TEXT,
                   overview     TEXT
                   )''')
    
    # 提交修改
    conn.commit()
    
    # 关闭数据库
    conn.close()


# 打印表格数据
def print_table(file_path,table_name):
    conn = sqlite3.connect(file_path)  # 打开数据库
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)  # 加载所有数据
    print(f'\n[{table_name}]: \n')  # 打印表格名称
    print(df.head(5))    #打印头 5 行数据
    print(df.tail(5))    #打印尾 5 行数据
    conn.close()    # 关闭数据库

# 保存表格数据到 csv 文件
def save_to_csv(file_path,table_name):
    conn = sqlite3.connect(file_path)  # 打开数据库
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)  # 加载所有数据
    df.to_csv(f'.test/{table_name}.csv', index=False)  # 保存到 csv 文件
    conn.close()    # 关闭数据库

if __name__ == '__main__':

    # 建立数据库
    #creat_movies_basic_table()   # 创建 movies_basic 表
    creat_movies_detail_table()  # 创建 movies_detail 表格
    creat_similarities_sqlite()  # 建立 similarities.db 数据库

    print_table(movies_data,'movies_basic')  # 查看 movies_basic 表格
    print_table(movies_data,'movies_detail')  # 查看 movies_detail 表格
    print_table(similarity_data,'similarities')  # 查看 similarities 表格
    