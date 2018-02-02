#coding=utf-8
import web
#连接数据库
import sqlite3

import urllib
import json

urls=(
    '/','Index',
    '/movie_des/(\d+)','Movie',
    '/grab/','GrabData',
)
#配置URL和匹配页面

app = web.application(urls,globals())
render = web.template.render('templates/',base='layout')  #加载HTML模板

"""
movies=[
    {'title':'Lion',
     'year':2004},
    {'title':'Snow White',
     'year':1999}
]
"""

class Index:
    def GET(self):
        movies=[]
        db = sqlite3.connect("MovieSite.db")
        for movie in db.execute("select * from movie"):
            #movies.append('%s (%s)'% (movie[1],movie[2]))
            movies.append({'id':movie[0],'title':movie[1]})
        db.close()
        return render.index(movies)

    def POST(self):
        db = sqlite3.connect("MovieSite.db")
        form = web.input(name="title")
        movie=db.execute("select * from movie where title = %s" % form.name).fetchone()
        db.close()
        return render.movie_des(movie)

class Movie:
    def GET(self,movie_id):
        '''cu = db.cursor()
        cu.execute("select * from movie where id = ?",movie_id)
        movie=cu.fetchone()'''
        db = sqlite3.connect("MovieSite.db")
        movie=db.execute("select * from movie where id = ?",movie_id).fetchone()
        db.close()
        return render.movie_des(movie)

class GrabData:
    """从豆瓣网站抓取排名前250的电影列表"""
    def GET(self):
        fp = urllib.urlopen("https://api.douban.com/v2/movie/top250?strat=0&count=5")
        data = fp.read()
        # print data
        data_js = json.loads(data)
        movie_250 = data_js['subjects']
        movies = [] #字典存储数据，页面显示
        dat=[] #存储数据添加入数据库
        for movie in movie_250:
            movies.append({"id": movie['id'],
                           "title": movie['title'],
                           'alt':movie['alt'],
                           'genres':movie['genres'],
                           'casts':movie['casts'],
                           })
            #print movie['title'], movie['id']
            dat.append((movie['id'],movie['title'],movie['alt'],movie['genres'],movie['casts']))
        self.add_movie(dat)
        return render.index(movies)

    def add_movie(self,data):
        db = sqlite3.connect("MovieSite.db")
        db.executemany("insert into movie_grab values(?,?,?,?,?)",data)
        db.commit()
        db.close()

if __name__=='__main__':
    app.run()
