import pandas as pd
import requests
import sqlite3
import time
import json
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
                print(f"[*获取失败] TMDB库中没有该影片 [访问IMDB查看详情]: https://www.imdb.com/title/tt{imdb_id}/")
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
            print(f"[+获取成功] [movieid: {movieid}]《{details['title_CN']}》({details['release_date'][:4]})\t评分: {details['vote_average']}")
            return result
        else:
            return None
    except Exception as e:
        print(f"[*获取失败] 网络错误: {str(e)}")
        return None



if __name__ == "__main__":

    conn = sqlite3.connect(data_base_path)  # 连接数据库

    # 根据 movieId 筛选出未爬取的电影, 即在 movies_basic 中有, 但 movies_detail 没有的数据
    df_todo = pd.read_sql_query("SELECT * FROM movies_basic WHERE movieId NOT IN (SELECT movieId FROM movies_detail)", conn)

    # 遍历 df_todo 表, 调用爬虫获取详细信息, 保存到数据库
    print(f"还剩 {len(df_todo)} 部影片未获取")
    for _, item in df_todo.iterrows():
        movieid = item['movieId']
        print(f"[movieid: {movieid:<6} 获取中]", end=' ')   # 打印进度, 6位数movieid,左对齐
        details = get_movie_details(item['imdbId']) # 调用爬虫获取详细信息
        if details:                                 # 保存详细信息到数据库
            df = pd.DataFrame([details], columns=list(details.keys()))           # 转换为 DataFrame
            df['movieId'] = movieid                                              # 增加 movieId 列
            df.to_sql('movies_detail', conn, if_exists='append', index=False)    # 添加到 movies_detail 表
        time.sleep(0.25)   # 避免请求过快, TMDB_API 限制每10秒钟请求不超过40次
    conn.close()
    print("全部完成")