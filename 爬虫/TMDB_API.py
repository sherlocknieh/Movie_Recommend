import pandas as pd
import requests
import sqlite3
import time


data_base_path = "数据库/output/movies.db"
BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "49b0d7cb820dde8476b350f3bd577342"


# 通过 TMDB_API 获取电影信息 (但是是通过 IMDB_ID 进行搜索)
def get_movie_details(imdb_id):

    endpoint = f"{BASE_URL}/find/tt{imdb_id}"
    params = {
        "api_key": API_KEY,
        "language": "zh-CN",
        "external_source": "imdb_id"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()['movie_results'][0]
            return {
                'title_CN': data.get('title'),
                'release_date': data.get('release_date'),
                'vote_average': data.get('vote_average'),
                'vote_count': data.get('vote_count'),
                'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
                'overview': data.get('overview')
            }
        else:
            print(f"IMDB {imdb_id} 获取失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"IMDB {imdb_id} 发生错误: {str(e)}")
        return None



if __name__ == "__main__":

    # 1. 遍历所有电影ID
    # 2. 获取电影详细信息 (跳过已爬取的电影)
    # 3. 保存到数据库

    conn = sqlite3.connect(data_base_path)  # 连接数据库

    df1 = pd.read_sql_query("SELECT * FROM movies_basic", conn)    # 读取 movies_basic 表, 获取所有电影ID和TMDBID
    df2 = pd.read_sql_query("SELECT * FROM movies_detail", conn)   # 读取 movies_detail 表, 获取已完成的电影信息
    
    # 遍历 df1 中的每一行
    for _, item in df1.iterrows():
        movieid = item['movieId']
        if item['movieId'] in df2['movieId'].values:    # 已有详细信息, 跳过
            continue
        else:
            details = get_movie_details(item['imdbId']) # 调用爬虫获取详细信息
            if details:
                # 保存详细信息到数据库
                df = pd.DataFrame([details], columns=list(details.keys()))           # 转换为 DataFrame
                df['movieId'] = movieid                                              # 增加 movieId 列
                df.to_sql('movies_detail', conn, if_exists='append', index=False)    # 保存到 movies_detail 表
                print(f"[+保存成功] [movieid: {movieid}]《{details['title_CN']}》({details['release_date'][:4]})\t评分: {details['vote_average']}")
            else:
                print(f"[*保存失败] [movieid: {movieid}] IMDB网址: https://www.imdb.com/title/tt{item['imdbId']}/")
                continue
            time.sleep(0.25)   # 避免请求过快, TMDB_API 限制每10秒钟请求不超过40次
    conn.close()
    print("全部完成")