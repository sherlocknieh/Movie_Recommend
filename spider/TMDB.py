# 电影信息爬取脚本

# 文件路径
input_file   = "data/links.csv"
output_file  = ("data/movies_inf.csv")

from bs4 import BeautifulSoup
import pandas as pd
import requests
import random
import time

def get_movie_details_bs4(tmdb_id):
    url = f"https://www.themoviedb.org/movie/{tmdb_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN, en;q=0.8'
    }
    proxies = {
        "http": "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897",
    }

    
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取标题
            title = soup.find('h2').text.strip() if soup.find('h2') else None
            
            # 获取发布日期
            release_date = soup.find('span', class_='release_date').text.strip() if soup.find('span', class_='release_date') else None
            
            # 获取评分
            vote_average = soup.find('div', class_='user_score_chart')['data-percent'] if soup.find('div', class_='user_score_chart') else None
            
            # 获取简介
            #overview = soup.find('div', class_='overview').text.strip() if soup.find('div', class_='overview') else None
            
            # 获取海报URL
            poster_div = soup.find('div', class_='poster')
            poster_path = None
            if poster_div and poster_div.find('img'):
                poster_path = 'https://image.tmdb.org/t/p/w500' + poster_div.find('img')['src']
            
            return {
                'title': title,
                #'overview': overview,
                'release_date': release_date,
                'poster_path': poster_path,
                'vote_average': vote_average
            }
        else:
            print(f"获取电影ID {tmdb_id} 失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"处理电影ID {tmdb_id} 时发生错误: {str(e)}")
        return None

def main():
    # 读取CSV文件
    df = pd.read_csv('links.csv')
    total_movies = len(df)
    print(f"开始处理 {total_movies} 部电影的信息...")
    
    # 创建新的列来存储电影信息
    movie_details = []
    
    # 遍历每个电影ID
    for index, tmdb_id in enumerate(df['tmdbId'], 1):
        print(f"正在处理第 {index}/{total_movies} 部电影 (ID: {tmdb_id})...")
        details = get_movie_details_bs4(tmdb_id)
        if details:
            print(f"成功获取电影信息: {details['title']}")
        movie_details.append(details)
        # 随机延迟1-3秒，避免请求过于频繁
        delay = random.uniform(1, 3)
        print(f"等待 {delay:.1f} 秒...\n")
        time.sleep(delay)
    
    # 将获取的信息添加到数据框
    movie_info_df = pd.DataFrame(movie_details)
    
    # 合并原始数据框和新信息
    result_df = pd.concat([df, movie_info_df], axis=1)
    
    # 保存结果到新的CSV文件
    result_df.to_csv('movies_with_details_bs4.csv', index=False)
    print(f"\n处理完成！共处理 {total_movies} 部电影")
    print(f"结果已保存到 movies_with_details_bs4.csv")

if __name__ == "__main__":
    main()
