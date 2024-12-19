from flask import Flask, render_template, abort, request
import pandas as pd
import random
from functools import lru_cache

# 文件路径
movie_details_path = 'data/movies_details.csv'
movie_similarities_path = 'data/similarities.csv'

app = Flask(__name__)

# 读取数据并创建索引以加快查找
df = pd.read_csv(
    movie_details_path,
    dtype={'movieId': int}  # 确保 movieId 列为整数类型
)
df.set_index('movieId', inplace=True)
similarities_df = pd.read_csv(
    movie_similarities_path, 
    skiprows=1,
    names=['ID1', 'ID2', 'Similarity'],
    dtype={'ID1': int, 'ID2': int}
)


@app.route('/')
@app.route('/<category>')
def index(category='popular'):
    # 根据类别获取电影列表
    if category == 'top_rated':
        movies = df.nlargest(12, 'vote_average').reset_index().to_dict('records')
        title = "高分电影"
    elif category == 'latest':
        movies = df.sort_values('release_date', ascending=False).head(12).reset_index().to_dict('records')
        title = "最新电影"
    elif category == 'random':
        movies = df.sample(n=min(12, len(df))).reset_index().to_dict('records')
        title = "随机推荐"
    else:  # popular
        movies = df.sample(n=min(12, len(df))).reset_index().to_dict('records')
        title = "热门电影"
    
    return render_template('index.html', 
                         movies=movies,
                         category=category,
                         title=title)


@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    # 调试信息
    with open('debug.txt', 'w', encoding='utf-8') as f:
        f.write(f"Movie ID: {movie_id} (type: {type(movie_id)})\n")
        f.write(f"DataFrame Index Info:\n")
        f.write(str(df.index.dtype) + "\n")
        f.write(f"DataFrame Index Values:\n{df.index.values[:5]}\n")  # 只显示前5个索引值
    
    try:
        # 查找指定ID的电影
        movie_dict = df.loc[movie_id].to_dict()
    except KeyError:
        # 如果电影ID不存在，返回404
        abort(404, description=f"未找到ID为 {movie_id} 的电影")
    
    # 获取相似电影
    similar_movies = []
    
    # 调试信息：打印相似度数据
    with open('debug.txt', 'a', encoding='utf-8') as f:  # 使用 'a' 模式追加内容
        f.write(f"\nSimilarities DataFrame Info:\n")
        f.write(str(similarities_df.dtypes) + "\n")
        f.write(f"Similarities DataFrame Head:\n{similarities_df.head()}\n")
        
        # 检查筛选条件，排除当前电影自身
        filtered_df = similarities_df[
            (similarities_df['ID1'] == movie_id) & 
            (similarities_df['ID2'] != movie_id)  # 添加这个条件
        ]
        f.write(f"\nFiltered DataFrame:\n{filtered_df}\n")
        
        if not filtered_df.empty:
            # 检查排序结果
            sorted_df = filtered_df.sort_values(by='Similarity', ascending=False)
            f.write(f"\nSorted DataFrame:\n{sorted_df}\n")
            
            # 检查最终选择的电影
            similar_ids = sorted_df[:6]
            f.write(f"\nSelected Similar Movies:\n{similar_ids}\n")
    
    # 获取相似电影
    for _, row in similar_ids.iterrows():
        try:
            similar_movie = df.loc[row['ID2']].to_dict()
            similar_movie['ID'] = row['ID2']
            similar_movie['Similarity'] = f"{row['Similarity']*100:.1f}%"
            similar_movies.append(similar_movie)
        except KeyError:
            continue  # 如果推荐的电影不存在，跳过这部电影
    
    with open('similar_movies.txt', 'w', encoding='utf-8') as f:
        f.write(str(similar_movies))
    
    return render_template('detail.html', movie=movie_dict, similar_movies=similar_movies)

@app.errorhandler(404)
def not_found_error(error):
    # 将错误对象传递给模板
    return render_template('404.html', error=error), 404

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('index.html', 
                             movies=[],
                             category='search',
                             title="搜索结果",
                             query='')
    
    # 在标题中搜索（不区分大小写）
    results = df[df['title'].str.contains(query, case=False, na=False)]
    movies = results.head(12).reset_index().to_dict('records')
    
    return render_template('index.html', 
                         movies=movies,
                         category='search',
                         title=f"搜索结果: {query}",
                         query=query)

if __name__ == '__main__':
    app.run()
