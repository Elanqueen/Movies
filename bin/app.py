#-*- coding: utf-8 -*-
import web
#连接数据库
import sqlite3

import urllib
import json
import sys

defaultencoding='utf-8'
if sys.getdefaultencoding()!= defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

urls=(
    '/','Index',
    '/movie_des/(\d+)','Movie',
    '/grab/','GrabData',
    '/cast/(.*)','Cast',
    '/director/(.*)','Director'
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
#抛出异常设定
class NullException(BaseException):"It is null, Please check."

class Index:
    def GET(self):
        movies=[]
        db = sqlite3.connect("MovieSite.db")
        for movie in db.execute("select * from movie"):
            #movies.append('%s (%s)'% (movie[1],movie[2]))
            movies.append({'id':movie[0],'title':movie[1]})
        db.close()
        return render.index(movies,count=0)

    def POST(self):
        db = sqlite3.connect("MovieSite.db")
        db.text_factory=str
        form = web.input(name="霸王别姬") # 默认值设置：name="霸王别姬"name='阿甘正传'
        if form.title:
            #movie=db.execute("select * from mvgrab where title = '霸王别姬'").fetchone()
            # movie=db.execute("select * from mvgrab where title = %s" % form.title).fetchone()
            title="%"+form.title+"%"
            movies=db.execute("select * from mvgrab where title like ?",(unicode(title),)).fetchall()
            count = db.execute("select count(*) as count from mvgrab where title like ?",
                               (unicode(title),)).fetchall()
            count=count[0][0]
            print title,movies,count
            db.close()
            return render.index(movies,count)

class Movie:
    def GET(self,movie_id):
        '''cu = db.cursor()
        cu.execute("select * from movie where id = ?",movie_id)
        movie=cu.fetchone()'''
        db = sqlite3.connect("MovieSite.db")
        movie=db.execute("select * from mvgrab where mvid = ?",(movie_id,)).fetchone()
        db.close()
        if movie:
            return render.movie_des(movie)
        else:
            raise NullException

class GrabData:
    """从豆瓣网站抓取排名前250的电影列表"""
    def GET(self):
        self.grab_movie_to_db()
        db = sqlite3.connect("MovieSite.db")
        movies=db.execute("select * from mvgrab limit 20").fetchall()
        db.close()
        return render.index(movies)

    def grab_movie_to_db(self):
        '''将通过豆瓣API抓取到的排名前250的电影信息存入数据库'''
        fp = urllib.urlopen("https://api.douban.com/v2/movie/top250?strat=0&count=250")
        data = fp.read()
        data_js = json.loads(data)
        movie_250 = data_js['subjects']
        movies = []  # 存储数据添加入数据库
        count=1
        for movie in movie_250:
            #将图片存入本地,暂时屏蔽了下载功能
            #self.get_poster(int(movie['id']),movie['images']['medium'])

            genres = ','.join(movie['genres'])
            casts = ','.join([d['name'] for d in movie['casts']])
            directors = ','.join([d['name'] for d in movie['directors']])
            movies.append((count,int(movie['id']), movie['title'], movie['rating']['average'],
                        movie['original_title'], directors, movie['alt'],
                        movie['year'], movie['subtype'].decode(), movie['images']['medium'],
                        genres, casts
                        ))
            count=count+1
        db = sqlite3.connect("MovieSite.db")
        db.execute("delete from mvgrab")
        db.executemany("insert into mvgrab values(?,?,?,?,?,?,?,?,?,?,?,?)", movies)
        db.commit()
        db.close()

    def get_poster(self,id,url):
        '''将获取的图片存入本地'''
        pic=urllib.urlopen(url).read()
        fn='static/poster/%d.jpg' % id
        f=open(fn,'wb')
        f.write(pic)
        f.close()

class Cast:
    def GET(self,cast):
        db=sqlite3.connect("MovieSite.db")
        cast_name="%"+cast+"%"
        movies=db.execute("select * from mvgrab where casts like ?",(unicode(cast_name),)).fetchall()
        if movies:
            return render.index(movies)
        else:
            raise NullException

class Director:
    def GET(self,director):
        db = sqlite3.connect("MovieSite.db")
        cast_name = "%" + director + "%"
        movies = db.execute("select * from mvgrab where directors like ?", (unicode(cast_name),)).fetchall()
        if movies:
            return render.index(movies)
        else:
            raise NullException

if __name__=='__main__':
    app.run()
