from flask import Flask, render_template, abort, request
import pandas as pd
import sqlite3
import json

# 文件路径
movies_path       = '数据库/output/movies.db'
similarities_path = '.test/similarities.db'

app = Flask(__name__)

# 加载电影数据
conn = sqlite3.connect(movies_path)
df1 = pd.read_sql_query(f'SELECT * FROM movies_basic', conn)  # movieId,imdbId,tmdbId,title,genres
df2 = pd.read_sql_query(f'SELECT * FROM movies_detail', conn) # movieId,title_CN,release_date,vote_average,vote_count,poster_path,overview
df_movies = pd.merge(df1, df2, on='movieId')
conn.close()
# 加载相似度数据
conn = sqlite3.connect(similarities_path)
df_similarities = pd.read_sql_query(f'SELECT * FROM similarities', conn) # movieId1,movieId2,similarity
conn.close()

# 主页
number_of_movies = 50  # 显示的电影数量
@app.route('/')
@app.route('/<category>')       # 分类查看
def index(category='popular'):  # 默认显示热门电影
    if category == 'top_rated':     # 从大于 7.5 分的电影中随机选取 12 部
        title = "高分电影"
        movies = df_movies[df_movies['vote_average'] >= 7.5].sample(number_of_movies).reset_index().to_dict('records')
    elif category == 'latest':     # 从日期最新的 100 部电影中随机选取 12 部
        movies = df_movies.sort_values(by='release_date', ascending=False).head(100).sample(number_of_movies).reset_index().to_dict('records')
        title = "最新电影"
    elif category == 'popular':      # 从打分人数最多的 100 部电影中随机选取 12 部
        movies = df_movies.sort_values(by='vote_count', ascending=False).head(100).sample(number_of_movies).reset_index().to_dict('records')
        title = "热门电影"
    else :  # category == 'random'
        movies = df_movies.sample(number_of_movies).reset_index().to_dict('records')
        title = "随机推荐"
    
    return render_template('index.html', movies=movies, category=category, title=title)  # 渲染模板

# 电影详情页, 显示电影信息和最相似的20部电影
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):

    try:
        # 查找指定ID的电影
        movie = df_movies.loc[df_movies['movieId'] == movie_id].to_dict('records')[0]
        # 存到本地
        with open(f'.test\/{movie_id}.json', 'w', encoding='utf-8') as f:
            json.dump(movie, f, ensure_ascii=False, indent=4)
    except KeyError:
        # 如果电影ID不存在，返回404
        abort(404, description=f"未找到ID为 {movie_id} 的电影")

    # 获取最相似的20部电影
    
    similar_movies = []
    # 渲染模板
    return render_template('detail.html', movie=movie, similar_movies=similar_movies)

# 搜索页, 显示搜索结果
@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('index.html', 
                             movies=[],
                             category='search',
                             title="搜索结果",
                             query='')
    
    # 在 title 和 title_CN 列中搜索
    mn = df_movies.apply(lambda x: x['title'] + x['title_CN'], axis=1)
    results = df_movies[mn.str.contains(query, case=False)]
    
    movies = results.head(12).reset_index().to_dict('records')
    
    return render_template('index.html', 
                         movies=movies,
                         category='search',
                         title=f"搜索结果: {query}",
                         query=query)

# 错误页面
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', error=error), 404


if __name__ == '__main__':
    app.run(debug=True)
