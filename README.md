# 相似电影推荐系统

使用基于物品的协同过滤算法构建的一个小小的电影推荐系统。


# 项目结构


## 数据库模块

- 作用: 初始化数据库, 集中储存各模块的输入输出数据

- 输入: 
    - ```ratings.csv```
    - ```movies.csv```
    - ```links.csv```

    (来自 [MovieLens](https://grouplens.org/datasets/movielens/) small 数据集, 包含 610 个用户对 9742 部电影的 100836 条评分数据)

- 输出:
    - ```movies.db```
        - 表1: ```movies_basic```  (电影基本信息表, 从 movies.csv 和 links.csv 导入)
        - 表2: ```movies_detail``` (电影扩展信息表, 由爬虫模块从 TMDB 网站获取)
    - similarities.db
        - 表1: ```similarities```  (电影相似度表, 由 CF 模块计算获得)


## 爬虫模块

- 作用: 爬取TMDB网站获取电影详细信息, 用于后续展示
    
- 输入: ```links.csv```
- 输出: ``` movies.db``` 的 ```movies_detail``` 表


## 协同过滤模块: 

- 作用: 根据用户评分数据, 计算物品相似度矩阵

- 输入: ```ratings.csv```

- 输出: ```similarities.db``` 的 ```similarities``` 表


## 网页前端模块: 

- 作用: 展示电影信息和推荐结果

1. 主页: 
    - 输入: ```movies.db```
    - 输出: 随机推荐电影列表

2. 电影详情页: 
    - 输入: ```movies.db```, ```similarities.db```
    - 输出: 电影详情和相似电影推荐


# 安装运行

## 环境准备

1. 安装 Python 3.6+

2. 打开命令行, 定位到项目文件夹

3. 安装依赖包: ```pip install -r requirements.txt```

## 运行步骤

    只想看看最终效果的话, 可直接从第4步开始运行

1. 运行数据库模块: ```python ./数据库/SQLite.py ```

2. 运行爬虫模块(需要翻墙): ```python ./爬虫/TMDB_API.py ```

    (爬虫模块能够跳过数据库中已有的数据, 每次运行只继续爬取上次未完成的任务)

    (数据集里有些条目是电视剧, 爬取时会显示 out of index 错误, 但程序仍能正常运行, 可以忽略)

3. 运行协同过滤模块: ```python ./协同过滤/CF-Item.py ```

4. 启动服务: ```python ./WEB/App.py ```

5. 访问网页: http://127.0.0.1:5000/
