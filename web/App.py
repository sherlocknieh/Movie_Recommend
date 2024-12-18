from flask import Flask, render_template
import pandas as pd
import random

app = Flask(__name__)

df = pd.read_csv('data/movie_details.csv')
similarities_df = pd.read_csv('data/movie_similarities.csv', names=['ID1', 'ID2', 'Similarity'])


@app.route('/')
def show_movies():
    movies = df.to_dict('records')
    random_movies = random.sample(movies, min(5, len(movies)))
    # 清理海报URL中的重复部分
    for movie in random_movies:
        if movie['poster_path'] and 'https://image.tmdb.org/t/p/w500https://' in str(movie['poster_path']):
            movie['poster_path'] = movie['poster_path'].replace('https://image.tmdb.org/t/p/w500https://', 'https://')
    return render_template('index.html', movies=random_movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # 查找指定ID的电影
    movie = df[df['ID'] == movie_id].iloc[0] if len(df[df['ID'] == movie_id]) > 0 else None
    if movie is None:
        return "电影未找到", 404
    
    # 获取相似电影
    similar_movies = []
    # 查找当前电影作为ID1或ID2的所有相似关系
    similar_pairs = similarities_df[
        (similarities_df['ID1'] == movie_id) | 
        (similarities_df['ID2'] == movie_id)
    ].sort_values('Similarity', ascending=False)
    
    # 获取前两个最相似的电影
    for _, row in similar_pairs.head(2).iterrows():
        similar_id = row['ID2'] if row['ID1'] == movie_id else row['ID1']
        similar_movie = df[df['ID'] == similar_id].iloc[0] if len(df[df['ID'] == similar_id]) > 0 else None
        if similar_movie is not None:
            # 转换为字典并添加相似度分数
            similar_movie_dict = similar_movie.to_dict()
            similar_movie_dict['Similarity'] = f"{row['Similarity']:.2f}"
            similar_movies.append(similar_movie_dict)
    
    # 转换电影对象为字典
    movie_dict = movie.to_dict()
    
    # 清理海报URL中的重复部分
    if movie_dict['poster_path'] and 'https://image.tmdb.org/t/p/w500https://' in str(movie_dict['poster_path']):
        movie_dict['poster_path'] = movie_dict['poster_path'].replace('https://image.tmdb.org/t/p/w500https://', 'https://')
    
    for similar_movie in similar_movies:
        if similar_movie['poster_path'] and 'https://image.tmdb.org/t/p/w500https://' in str(similar_movie['poster_path']):
            similar_movie['poster_path'] = similar_movie['poster_path'].replace('https://image.tmdb.org/t/p/w500https://', 'https://')
    
    return render_template('detail.html', movie=movie_dict, similar_movies=similar_movies)

if __name__ == '__main__':
    app.run(debug=True)
