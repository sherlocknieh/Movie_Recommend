from flask import Flask, render_template, abort
import pandas as pd
import random
from functools import lru_cache

# 文件路径
movie_details_path = 'data/details.csv'
movie_similarities_path = 'data/similarities.csv'

app = Flask(__name__)

# 读取数据并创建索引以加快查找
df = pd.read_csv(movie_details_path)
df.set_index('movieId', inplace=True)
similarities_df = pd.read_csv(movie_similarities_path, names=['ID1', 'ID2', 'Similarity'])

@lru_cache(maxsize=20)
def get_movie_by_id(movie_id):
    """获取电影信息，使用缓存提高性能"""
    try:
        return df.loc[movie_id].to_dict()
    except KeyError:
        return None

def clean_poster_url(url):
    """清理海报URL"""
    if url and 'https://image.tmdb.org/t/p/w500https://' in str(url):
        return url.replace('https://image.tmdb.org/t/p/w500https://', 'https://')
    return url

@app.route('/')
def index():
    try:
        movies = df.sample(n=min(8, len(df))).reset_index().to_dict('records')
        return render_template('index.html', movies=movies)
    except Exception as e:
        app.logger.error(f"首页加载错误: {str(e)}")
        return "服务器错误", 500

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # 查找指定ID的电影
    movie_dict = get_movie_by_id(movie_id)
    if not movie_dict:
        abort(404, description="电影未找到")
    
    # 获取相似电影
    similar_movies = []
    similar_pairs = similarities_df[
        (similarities_df['ID1'] == movie_id) | 
        (similarities_df['ID2'] == movie_id)
    ].sort_values('Similarity', ascending=False).head(4)
    
    for _, row in similar_pairs.iterrows():
        similar_id = row['ID2'] if row['ID1'] == movie_id else row['ID1']
        similar_movie = get_movie_by_id(similar_id)
        if similar_movie:
            similar_movie['Similarity'] = f"{row['Similarity']*100:.1f}%"
            similar_movie['poster_path'] = clean_poster_url(similar_movie['poster_path'])
            similar_movies.append(similar_movie)
    
    # 清理当前电影的海报URL
    movie_dict['poster_path'] = clean_poster_url(movie_dict['poster_path'])
    
    return render_template('detail.html', movie=movie_dict, similar_movies=similar_movies)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
