from flask import Flask, render_template
import pandas as pd
import random

app = Flask(__name__)

# 将 DataFrame 读取移到全局，避免重复读取
df = pd.read_csv('movies.csv')
# 读取相似度数据
similarities_df = pd.read_csv('similarities.csv', names=['ID1', 'ID2', 'Similarity'])

@app.route('/')
def show_movies():
    # 将数据框转换为字典列表
    movies = df.to_dict('records')
    # 随机选择5部电影
    random_movies = random.sample(movies, min(5, len(movies)))
    return render_template('movies.html', movies=random_movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # 查找指定ID的电影
    movie = df[df['ID'] == movie_id].to_dict('records')
    if not movie:
        return "电影未找到", 404
    
    # 获取相似电影
    similar_movies = []
    # 查找当前电影作为ID1或ID2的所有相似关系
    similar_pairs = similarities_df[
        (similarities_df['ID1'] == movie_id) | 
        (similarities_df['ID2'] == movie_id)
    ].sort_values('Similarity', ascending=False)
    
    # 获取前两个最相似的电影ID和相似度
    similar_movies_with_score = []
    for _, row in similar_pairs.head(2).iterrows():
        similar_id = row['ID2'] if row['ID1'] == movie_id else row['ID1']
        similar_movie = df[df['ID'] == similar_id].to_dict('records')
        if similar_movie:
            similar_movie = similar_movie[0]
            similar_movie['Similarity'] = f"{row['Similarity']:.2f}"
            similar_movies_with_score.append(similar_movie)
    
    print(f"Movie ID: {movie_id}")  # 调试信息
    print(f"Similar movies: {similar_movies_with_score}")  # 调试信息
    
    return render_template('movie_detail.html', movie=movie[0], similar_movies=similar_movies_with_score)

if __name__ == '__main__':
    app.run(debug=True)
