from flask import Flask, render_template, abort, request
import pandas as pd
import sqlite3
import json
import os

# 文件路径
movies_path       = '数据库/output/movies.db'
similarities_path = '数据库/output/similarities.db'

app = Flask(__name__)

# 加载电影数据
conn = sqlite3.connect(movies_path)
df1 = pd.read_sql_query(f'SELECT * FROM movies_basic', conn)  # movieId,imdbId,tmdbId,title,genres
df2 = pd.read_sql_query(f'SELECT * FROM movies_detail', conn) # movieId,title_CN,release_date,vote_average,vote_count,poster_path,overview
df_movies = pd.merge(df1, df2, on='movieId')
conn.close()


# 主页: 展示热门电影, 最新电影, 高分电影, 随机推荐
number_of_movies = 54  # 显示的电影数量
@app.route('/')
@app.route('/<category>')       # 分类查看
def index(category='popular'):  # 默认显示热门电影
    
    if category == 'top_rated':     # 从大于 8 分的电影中随机选取 number_of_movies 部
        title = "高分电影"
        movies = df_movies[df_movies['vote_average'] >= 8].sample(number_of_movies).reset_index().to_dict('records')
    elif category == 'latest':     # 从日期最新的 100 部电影中随机选取 number_of_movies 部
        movies = df_movies.sort_values(by='release_date', ascending=False).head(100).head(number_of_movies).reset_index().to_dict('records')
        title = "最新电影"
    elif category == 'popular':      # 从打分人数最多的 100 部电影中随机选取 number_of_movies 部
        movies = df_movies.sort_values(by='vote_count', ascending=False).head(100).sample(number_of_movies).reset_index().to_dict('records')
        title = "热门电影"
    else :  # category == 'random'
        movies = df_movies.sample(number_of_movies).reset_index().to_dict('records')
        title = "随机推荐"
    
    return render_template('index.html', movies=movies, category=category, title=title)  # 渲染模板

# 电影详情页: 展示电影信息,相似电影列表
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):

    try:
        # 查找指定ID的电影
        movie = df_movies.loc[df_movies['movieId'] == movie_id].to_dict('records')[0]
    except KeyError:
        # 如果电影ID不存在，返回404
        abort(404, description=f"未找到ID为 {movie_id} 的电影")

    # 在数据库中获取最相似的 number_of_movies 部电影
    similar_movies = []

    conn = sqlite3.connect(similarities_path)    # 连接相似度数据库
    df = pd.read_sql_query(f"SELECT * FROM similarities WHERE movieId1={movie_id} or movieId2={movie_id} ORDER BY similarity DESC LIMIT {number_of_movies}", conn)
    results = df.to_dict('records')  # 获取结果并转换为字典列表
    conn.close()

    for result in results:          # 遍历结果 [{MovieID1,MovieID2,Similarity}]
        if result['MovieID1'] == movie_id: # 如果本电影ID在第一列，则取第二列的电影
            similar_movie = df_movies.loc[df_movies['movieId'] == result['MovieID2']].to_dict('records')
        else:                         # 如果本电影ID在第二列，则取第一列的电影
            similar_movie = df_movies.loc[df_movies['movieId'] == result['MovieID1']].to_dict('records')
        if not similar_movie:        # 如果找不到电影，跳过
            continue
        similar_movie = similar_movie[0]    # 取第一条记录
        similar_movies.append(similar_movie)  # 添加到列表
        similar_movie['Similarity'] = result['Similarity']  # 添加相似度数据
    # 降序排列
    similar_movies = sorted(similar_movies, key=lambda x: x['Similarity'], reverse=True)
    # 发送给网页
    return render_template('detail.html', movie=movie, similar_movies=similar_movies)

# 搜索页: 展示搜索结果
@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('index.html', movies=[], category='search', title="搜索结果", query='')
    
    # 在 title 和 title_CN 列中各搜索一遍
    results = df_movies[(df_movies['title'].str.contains(query, case=False)) | (df_movies['title_CN'].str.contains(query, case=False))]
    # 去掉重复的电影
    results = results.drop_duplicates(subset='movieId')
    # 选取 24 部, 转换为字典列表
    movies = results.head(24).reset_index().to_dict('records')
    # 发送给网页
    return render_template('index.html', movies=movies, category='search', title=f"搜索结果: {query}", query=query)

# 错误页面: 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error=error), 404


if __name__ == '__main__':
    app.run(debug=True)
