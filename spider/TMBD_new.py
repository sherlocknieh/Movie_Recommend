import requests
from bs4 import BeautifulSoup
import csv
#request
User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0,';
headers = {'User-Agent': User_Agent,'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}

import csv

def generate_movie_links(file_path):
    """
    读取 CSV 文件中的第三列，将每个数字拼接到指定的字符串后并存入数组。
    """
    base_url = "https://www.themoviedb.org/movie/"
    movie_links = []

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:  # 确保至少有三列
                number = row[2].strip()  # 获取第三列并去除多余空格
                movie_links.append(base_url + number)

    return movie_links
def soup_read_movies(soup_web):
    ans = ""
    mov_road = '#original_header > div.header_poster_wrapper.false > section > div.title.ott_false > h2 > a'
    mov_soup = soup_web.select(mov_road)
    mov_real = mov_soup[0].get_text();
    ans = mov_real
    return ans

def soup_read_director(soup_web):
    ans = ""
    dir_road = '#original_header > div.header_poster_wrapper.false > section > div.header_info > ol'
    dir_soup = soup_web.select(dir_road)
    #print(dir_soup)
    for div in dir_soup:
        divs = div.select('a')
        #print(divs)
        div_real = divs[0].get_text();
        ans = div_real

    return ans

def soup_read_subsciption(soup_web):
    ans = ""
    sub_road = '#original_header > div.header_poster_wrapper.false > section > div.header_info > div > p'
    sub_soup = soup_web.select(sub_road)
    div_real = sub_soup[0].get_text();
    ans = div_real
    return ans

def soup_read_images(soup_web):
    ans = ""
    img_road = '#original_header > div.poster_wrapper.false > div > div.image_content > div > img'
    img_soup = soup_web.select(img_road)
    src = img_soup[0]['src']
    ans = src
    print(ans)
    return ans

def movie_get(movie_link):
    web = movie_link
    #print(web)
    try:
        response = requests.get(web, headers=headers,timeout=10);
    except ReadTimeout or ConnectTimeout:
         print('Timeout')
    html_web = response.content.decode('utf-8');
    soup_web = BeautifulSoup(html_web,'lxml')

    line = []

    # 分各部分读取网页信息
    movie_name = soup_read_movies(soup_web);
    line.append(movie_name)

    director = soup_read_director(soup_web)
    line.append(director)
    #print(director)

    subsciption = soup_read_subsciption(soup_web)
    line.append(subsciption)
    #print(subsciption)

    images = soup_read_images(soup_web)
    line.append(images)

    return line

def append_links_to_csv(file_path, links):
    """
    将整个数组作为一行，每个元素之间用逗号分隔，写入 CSV 文件末端。
    """
    with open(file_path, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(links)




def news_save(text):
    import json
    with open(r'news.txt', 'a', encoding='utf-8') as txt_file:
        for element in text:
            for word in element:
                if len(word) != 0:
                    txt_file.write(word + '\n\n')

#def title_save(text):
#    import json
#    with open(r'title.txt', 'a', encoding='utf-8') as txt_file:
#        for element in text:
#            if len(element) != 0:
#                txt_file.write(element + '\n\n')

if __name__ == '__main__':
#    url = 'https://cs.xmu.edu.cn/';
#    html = get_html(url)
#    text = get_soup(html)
#    news_save(text)
    csv_outfilename = "movie_inf.csv"
    csv_infilename = "links.csv"
    links = generate_movie_links(csv_infilename)
    links = links[1:]
    #print(links)
    for i in range(len(links)):
        imf = movie_get(links[i])
        imf.insert(0,str(i))
        print(imf)
        append_links_to_csv(csv_outfilename,imf)