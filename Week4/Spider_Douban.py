import requests
import time
import random
from lxml import etree
import pymysql

def load_page(url):
    #定义请求头，模拟浏览器
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36"
    }
    try:
        # 添加请求头
        html = requests.get(url, headers=headers)
        html.encoding = html.encoding
        if html.status_code == 200:
            return html
    except Exception as e:
        print('抓取失败：%s' % e)


#获取25个页面
def get_data(baseurl,movies):
    for i in range(0,10):
        url = baseurl + str(i*25)
        html = load_page(url)
        time.sleep(random.randint(3,5))
        parse(html,movies)


#页面解析
def parse(html,movies):
    html = etree.HTML(html.text)
    lis = html.xpath("//ol[@class='grid_view']/li")
    for li in lis:
        titles = li.xpath(".//a/span[@class='title']/text()")[0]
        scores = li.xpath(".//span[@class='rating_num']/text()")
        judge_nums = li.xpath(".//div[@class='star']/span/text()")[1].replace('人评价','')
        pictures = li.xpath(".//img/@src")
        links = li.xpath(".//div[@class='hd']/a/@href")

        for link in links:
            page = load_page(link)
            time.sleep(random.randint(3,5))
            page = etree.HTML(page.text)

            try:
                contents = page.xpath("//span[normalize-space(@property)='v:summary']/text()")
                directors = page.xpath("//a[@rel='v:directedBy']/text()")
                actors = page.xpath("//a[@rel='v:starring']/text()")
                years = str(page.xpath("//span[@class='year']/text()"))
                years = years.replace('(','')
                years = years.replace(')','')
                years = years.replace("'","")
                years = years.replace('[','')
                years = years.replace(']','')

                i = 0
                content = ''
                director = ''
                actor = ''
                while i < len(contents):
                    content = content + str(contents[i])
                    i = i + 1
                i = 0
                #有可能有很多个br标签，整个循环把它们连在一起
                #但是我发现有些全部概述藏在all hiden标签下，有些又没有这个标签，所以概述会有缺失
                while i < len(directors):
                    director = director + str(directors[i]) + ' '
                    i = i + 1
                i = 0
                while i < len(actors):
                    actor = actor + str(actors[i]) + ' '
                    i = i + 1
                content = content.replace('\n','')
                content = content.replace('\u3000','')
                content = content.replace(' ','')

                movie = {'title':titles,'year':years,'score':scores,'judge_num':judge_nums,'picture':pictures,
                      'content':content,'directors':directors,'actors':actors}
                sql = """
                        INSERT INTO MOVIES(title, year, score, judge_num, picture, content, directors, actors)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                data = [(titles, years, scores, judge_nums, pictures, content, director, actor)]
                try:
                    cursor.executemany(sql, data)
                    conn.commit()
                    print('success')
                except Exception as e:
                    print(e)
                    conn.rollback()

                movies.append(movie)
                print(movie)
            except:
                continue

if __name__ == '__main__':
    movies = []
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="YUAN69188059*",
        database="Douban_Top250",
        charset="utf8"
    )
    cursor = conn.cursor()

    sql = """CREATE TABLE MOVIES (
             TITLE TEXT NOT NULL,
             YEAR TEXT,
             SCORE TEXT,
             JUDGE_NUM TEXT,
             PICTURE TEXT,
             CONTENT TEXT,
             DIRECTORS TEXT,
             ACTORS TEXT)"""
    try:
        cursor.execute(sql)
    except Exception as e:
        print(e)
        conn.rollback()
    cursor = conn.cursor()

    baseurl = 'https://movie.douban.com/top250?start='
    movies = get_data(baseurl,movies)
    conn.close