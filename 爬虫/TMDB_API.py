import pandas as pd
import requests
import sqlite3
import time


data_base_path = "数据库/output/movies.db"
BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "49b0d7cb820dde8476b350f3bd577342"


# 获取电影详细信息
def get_movie_details(tmdb_id):
    """获取电影详细信息"""
    endpoint = f"{BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": API_KEY,
        "language": "zh-CN"  # 获取中文信息
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                'title_CN': data.get('title'),
                'release_date': data.get('release_date'),
                'vote_average': data.get('vote_average'),
                'vote_count': data.get('vote_count'),
                'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
                'overview': data.get('overview')
            }
        else:
            print(f"获取电影ID {tmdb_id} 失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"处理电影ID {tmdb_id} 时发生错误: {str(e)}")
        return None

def main():

    # 加载数据库
    conn = sqlite3.connect(data_base_path)
    cursor = conn.cursor()

    df1 = pd.read_sql_query("SELECT * FROM movies_basic", conn)    # 读取 movies_basic 表, 获取所有电影ID和TMDBID
    df2 = pd.read_sql_query("SELECT * FROM movies_detail", conn)   # 读取 movies_detail 表, 获取已完成的电影信息
    
    # 遍历 df1 中的每一行
    for _, row in df1.iterrows():
        tmdb_id = row['tmdbId']
        movieid = row['movieId']
        if movieid in df2['movieId'].values:  # 已有详细信息, 跳过
            continue
        else:
            # 获取详细信息
            details = get_movie_details(tmdb_id)
            if details:
                # 保存详细信息到数据库
                df = pd.DataFrame([details], columns=list(details.keys()))
                df['movieId'] = movieid
                df.to_sql('movies_detail', conn, if_exists='append', index=False)
                print(f"[+保存成功] [ID:{movieid}]《{details['title_CN']}》({details['release_date'][:4]})\t评分: {details['vote_average']}")
            else:
                print(f"[*保存失败] [ID:{movieid}] ")
                continue
            time.sleep(0.25)   # 避免请求过快, TMDB_API 限制每10秒钟请求不超过40次
    conn.close()

if __name__ == "__main__":
    main()
