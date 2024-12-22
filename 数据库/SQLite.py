import pandas as pd
import sqlite3


# 相关文件路径
demo_data = '.TEST/demo.db'
movies_data = '数据库/movies.db'
similarity_data = '数据库/similarities.db'


# SQLite 用法示例
def sqlite_demo():

    # 打开/创建数据库
    conn = sqlite3.connect(demo_data)
    
    # 删除名为 table1 的表格
    conn.execute('DROP TABLE IF EXISTS table1')

    # 创建名为 table1 的表格
    conn.execute('''CREATE TABLE IF NOT EXISTS table1 (
                   id     INT,
                   name   TEXT,
                   age    INT
                   )''')  # table1 表格包含 id, name, age 三列数据
    
    # 批量插入数据 (使用 pandas)
    data = [{'id': 1, 'name': 'John', 'age': 20},
            {'id': 2, 'name':  None,  'age': 25}]               # 使用字典列表传递数据, 键名要与表格列名一致
    df = pd.DataFrame(data)                                     # 转换为 DataFrame 对象
    df.to_sql('table1', conn, if_exists='append', index=False)  # 插入数据到表格

    # 创建游标, 用于逐行处理数据
    cursor = conn.cursor()

    # 插入数据
    cursor.execute("INSERT INTO table1 (id, name, age) VALUES (3, 'Mary', 22)")  # 插入 id 为 3 的数据

    # 修改数据
    cursor.execute('UPDATE table1 SET age = 19 WHERE id = 1')  # 修改 id 为 1 的 age 为 19

    # 删除数据
    cursor.execute('DELETE FROM table1 WHERE name is NULL')  # 删除 name 列为 NULL 的数据

    # 提交修改
    conn.commit()

    # 读取数据
    cursor.execute('SELECT * FROM table1')  # 选中所有行
    rows = cursor.fetchall()                # 获取所有行
    for row in rows:  print(row)            # 打印所有行

    # 读取数据 (使用 pandas)
    df = pd.read_sql_query('SELECT * FROM table1', conn)  # 读取所有数据
    print(df)

    # 关闭数据库
    conn.close()


# 建立 similarities.db 数据库
def creat_similarities_sqlite():

    # 打开/创建数据库
    conn = sqlite3.connect(similarity_data)
    
    # 创建 similarities 表格(如果不存在则创建)
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
def creat_movies_sqlite():

    # 相关文件路径
    input_file1 = '数据库/input/links.csv'
    input_file2 = '数据库/input/movies.csv'

    # 创建 movies.db 数据库并打开
    conn = sqlite3.connect(movies_data)      

    # 读取 links.csv 和 movies.csv 文件
    df1 = pd.read_csv(input_file1, dtype={'imdbId': str, 'tmdbId': str}) # imdbId, tmdbId 读取为字符串类型
    df2 = pd.read_csv(input_file2)

    # 合并两张表
    df = pd.merge(df1, df2, on='movieId')

    # 写入 movies_basic 表
    df.to_sql('movies_basic', conn, if_exists='replace', index=False)


    # 新建 movies_detail 表
    conn.execute('''CREATE TABLE IF NOT EXISTS movies_detail (
                   movie_id     INT,
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
    

# 查看数据库中的表格
def print_table(file_path,table_name):
    
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor() # 创建游标, 用于逐行处理数据

    df = pd.read_sql_query(f'SELECT * FROM {table_name} LIMIT 10', conn)  # 读取前 10 条
    print(df)

    # 关闭数据库
    conn.close()


if __name__ == '__main__':

    sqlite_demo()  # SQLite 用法示例
    print()

    creat_similarities_sqlite()  # 建立 similarities.db 数据库
    print_table(similarity_data,'similarities')  # 查看 similarities 表格
    print()

    creat_movies_sqlite()  # 建立 movies.db 数据库
    print_table(movies_data,'movies_basic')  # 查看 movies_basic 表格
    print_table(movies_data,'movies_detail')  # 查看 movies_detail 表格