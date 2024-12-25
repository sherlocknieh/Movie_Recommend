import pandas as pd
import requests
import sqlite3
import time
import json
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


data_base_path = "数据库/output/movies.db"
BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "49b0d7cb820dde8476b350f3bd577342"


# 通过 TMDB_API 获取电影信息 (用 IMDB_ID 进行搜索)
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
            data = response.json()
            # 处理不同类型的数据
            if data.get('movie_results'):  # 电影
                data = data['movie_results'][0]
                release_date = data.get('release_date')
                title_name = data.get('title')
                poster_path = data.get('poster_path')
            elif data.get('tv_results'):  # 电视剧
                data = data['tv_results'][0]
                release_date = data.get('first_air_date')
                title_name = data.get('name')
                poster_path = data.get('poster_path')
            elif data.get('tv_episode_results'):  # 电视剧的某一集
                data = data['tv_episode_results'][0]
                release_date = data.get('air_date')
                title_name = data.get('name')
                poster_path = data.get('still_path')
            else:                               # TMDB库中没有该影片
                print(f"[*获取失败]\t[影片不在TMDB库中]\t[访问IMDB查看详情]: https://www.imdb.com/title/tt{imdb_id}/")
                return None
            
            # 提取需要的数据
            result = {
                'title_CN': title_name,
                'release_date': release_date,
                'vote_average': data.get('vote_average'),
                'vote_count': data.get('vote_count'),
                'poster_path': f"https://image.tmdb.org/t/p/w500{poster_path}",
                'overview': data.get('overview')
            }
            return result
    
        else:
            print(f"[*获取失败]\t[网络错误]\t{response.status_code}")
            return None
    except Exception as e:
        print(f"[*获取失败]\t[网络错误]\t{str(e)}")
        return None


def fetch_and_save_movie(item):
    conn = sqlite3.connect(data_base_path)  # 连接数据库
    movieid = item['movieId']
    details = get_movie_details(item['imdbId'])  # 调用爬虫获取详细信息
    if details:                           # 保存详细信息到数据库
        df = pd.DataFrame([details], columns=list(details.keys()))           # 转换为 DataFrame
        df['movieId'] = movieid                                              # 增加 movieId 列
        df.to_sql('movies_detail', conn, if_exists='append', index=False)    # 保存到数据库
        #print(f"[获取成功]\t《{details['title_CN']}》({details['release_date'][:4]})\t评分: {details['vote_average']}")
    #time.sleep(1/50)     # API 请求频率限制, 50次/s
    conn.close()         # 关闭连接


if __name__ == "__main__":

    conn = sqlite3.connect(data_base_path)  # 连接数据库
    # 根据 movieId 筛选出未爬取的电影
    df = pd.read_sql_query("SELECT * FROM movies_basic WHERE movieId NOT IN (SELECT movieId FROM movies_detail)", conn)
    items = df.to_dict("records")    # 转换为字典列
    conn.close()  # 关闭数据库

    print(f"还剩 {len(items)} 部影片未获取")

    # 使用单进程爬取
    # for item in items:
    #     print(f"[imdb: {imdb_id} 正在获取...]", end=' ', flush=True)
    #     fetch_and_save_movie(item)
    
    # 使用多进程爬取
    with Pool(processes=cpu_count()) as pool:    # 开启进程池
        list(tqdm(pool.imap(fetch_and_save_movie, items), total=len(items)))  # 并行处理

    print("全部完成")
