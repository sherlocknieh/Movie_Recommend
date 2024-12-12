import pandas as pd
import requests
import time

# TMDB API配置
API_KEY = "YOUR_API_KEY"  # 替换成您的TMDB API密钥
BASE_URL = "https://api.themoviedb.org/3"

def get_movie_details(tmdb_id):
    """获取电影详细信息"""
    endpoint = f"{BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": API_KEY,
        "language": "zh-CN"  # 获取中文信息
    }
    
    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title'),
                'overview': data.get('overview'),
                'release_date': data.get('release_date'),
                'poster_path': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else None,
                'vote_average': data.get('vote_average')
            }
        else:
            print(f"获取电影ID {tmdb_id} 失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"处理电影ID {tmdb_id} 时发生错误: {str(e)}")
        return None

def main():
    # 读取CSV文件
    df = pd.read_csv('movies.csv')
    
    # 创建新的列来存储电影信息
    movie_details = []
    
    # 遍历每个电影ID
    for tmdb_id in df['tmdbId']:
        details = get_movie_details(tmdb_id)
        movie_details.append(details)
        time.sleep(0.25)  # 添加延迟以避免超过API速率限制
    
    # 将获取的信息添加到数据框
    movie_info_df = pd.DataFrame(movie_details)
    
    # 合并原始数据框和新信息
    result_df = pd.concat([df, movie_info_df], axis=1)
    
    # 保存结果到新的CSV文件
    result_df.to_csv('movies_with_details.csv', index=False)
    print("处理完成！结果已保存到 movies_with_details.csv")

if __name__ == "__main__":
    main()
