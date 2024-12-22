# 相似电影推荐系统

使用 Item-CF (Item-based Collaborative Filtering) 基于物品的协同过滤


# 项目结构


## 数据库模块

- 作用: 存储电影信息和用户评分数据

- 输入: MovieLens 的 ml-latest-small 数据集
    - 网址: https://grouplens.org/datasets/movielens/
    - 文件: 
        - ratings.csv
        - movies.csv
        - links.csv
    - 说明: 包含 610 个用户对 9742 部电影的 100836 条评分数据

- 输出:
    - movies.db
        - movies_basic 表 (电影ID, IMDbID, TMDBID, 电影名称, 类型)
        - movies_detail 表 (电影ID, 上映日期, 评分, 评分人数, 海报, 电影简介)
    - similarities.db
        - similarities 表 (电影ID1, 电影ID2, 相似度)


## 爬虫模块

- 作用: 爬取TMDB网站获取电影详细信息, 用于后续展示
    
- 输入: links.csv 文件

- 输出: movies_detail 表


## 协同过滤模块: 

- 作用: 根据用户评分数据, 计算相似度矩阵

- 输入: ratings.csv

- 输出: similarities 表


## 网页前端模块: 

- 作用: 展示电影信息和推荐结果

1. 主页: 
    - 输入: movies.db
    - 输出: 随机推荐电影列表

2. 电影详情页: 
    - 输入: movies.db, similarities.db
    - 输出: 电影详情和相似电影推荐


# 运行

## 环境准备

1. 安装 Python 3.6+

2. 打开命令行, 定位到项目文件夹

3. 安装依赖包: ```pip install -r requirements.txt```

## 运行步骤

1. 运行数据库模块: ```python ./数据库/SQLite.py ```

2. 运行爬虫模块: ```python ./爬虫/TMDB_API.py ```

    (注: 爬虫模块使用的 API_KEY 属于个人私密信息, 请勿滥用或泄露)

3. 运行协同过滤模块: ```python ./协同过滤/CF-Item.py ```

4. 启动服务: ```python ./WEB/App.py ```

5. 访问网页: http://127.0.0.1:5000/
