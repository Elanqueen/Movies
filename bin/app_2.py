#-*- coding: utf-8 -*-
'''
此处使用mysql数据库
采用 import mysqldb的数据库连接方式
'''
import web
#连接数据库
#import sqlite3
import MySQLdb

import urllib
import json
import sys
'''
defaultencoding='utf-8'
if sys.getdefaultencoding()!= defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)'''

urls=(
    '/movie_des/(\d+)','Movie',
    '/','GrabData',
    '/cast/(.*)','Cast',
    '/director/(.*)','Director'
)
#配置URL和匹配页面

app = web.application(urls,globals())
render = web.template.render('templates/',base='layout')  #加载HTML模板

#抛出异常设定
class NullException(BaseException):"It is null, Please check."

dbb = MySQLdb.connect("localhost","root","root","movies",charset='utf8')
db=dbb.cursor()
class Movie:
    def GET(self,movie_id):
        '''cu = db.cursor()
        cu.execute("select * from movie where id = ?",movie_id)
        movie=cu.fetchone()'''

        db.execute("select * from mvgrab where mvid = %s",(movie_id,))
        movie =db.fetchone()
        #db.close()
        if movie:
            return render.movie_des_2(movie)
        else:
            raise NullException

class GrabData:
    """从豆瓣网站抓取排名前250的电影列表"""
    def GET(self):
        self.grab_movie_to_db()
        #db = MySQLdb.connect("MovieSite.db")
        db.execute("select * from mvgrab limit 20")
        movies =db.fetchall()
        #db.close()
        return render.index_2(movies)

    def POST(self):
        #db = MySQLdb.connect("MovieSite.db")
        #db.text_factory=str
        form = web.input(name="霸王别姬") # 默认值设置：name="霸王别姬"name='阿甘正传'
        if form.title:
            #movie=db.execute("select * from mvgrab where title = '霸王别姬'").fetchone()
            # movie=db.execute("select * from mvgrab where title = %s" % form.title).fetchone()
            title="%"+form.title+"%"
            db.execute("select * from mvgrab where title like %s",(unicode(title),))
            movies =db.fetchall()
            db.execute("select count(*) as count from mvgrab where title like %s",
                               (unicode(title),))
            count =db.fetchone()
            count=count[0]
            #db.close()
            return render.index_2(movies,count,form.title)
        else:
            return render.index_2([],0,"")

    def grab_movie_to_db(self):
        '''将通过豆瓣API抓取到的排名前250的电影信息存入数据库'''
        fp = urllib.urlopen("https://api.douban.com/v2/movie/top250?strat=0&count=25py")
        data = fp.read()
        data_js = json.loads(data)
        movie_250 = data_js['subjects']
        movies = []  # 存储数据添加入数据库
        count=1
        db.execute("delete from mvgrab")
        for movie in movie_250:
            #将图片存入本地,暂时屏蔽了下载功能
            #self.get_poster(int(movie['id']),movie['images']['medium'])

            genres = ','.join(movie['genres'])
            casts = ','.join([d['name'] for d in movie['casts']])
            directors = ','.join([d['name'] for d in movie['directors']])
            movies.append((count,movie['id'], movie['title'], movie['rating']['average'],
                        movie['original_title'], directors, movie['alt'],
                        movie['year'], movie['subtype'].decode(), movie['images']['medium'],
                        genres, casts
                        ))
            count=count+1
        #db = MySQLdb.connect("MovieSite.db")
            '''db.execute("insert into mvgrab values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       (count,movie['id'], movie['title'], movie['rating']['average'],
                        movie['original_title'], directors, movie['alt'],
                        movie['year'], movie['subtype'].decode(), movie['images']['medium'],
                        genres,casts,
                        ))'''
        db.executemany("insert into mvgrab values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", movies)
        dbb.commit()
        #db.close()

    def get_poster(self,id,url):
        '''将获取的图片存入本地'''
        pic=urllib.urlopen(url).read()
        fn='static/poster/%d.jpg' % id
        f=open(fn,'wb')
        f.write(pic)
        f.close()

class Cast:
    def GET(self,cast):
        #db=MySQLdb.connect("MovieSite.db")
        cast_name="%"+cast+"%"
        db.execute("select * from mvgrab where casts like %s",
                   (unicode(cast_name),))
        movies =db.fetchall()
        if movies:
            return render.index_2(movies)
        else:
            raise NullException

class Director:
    def GET(self,director):
        #db = MySQLdb.connect("MovieSite.db")
        cast_name = "%" + director + "%"
        db.execute("select * from mvgrab where directors like %s", (unicode(cast_name),))
        movies =db.fetchall()
        if movies:
            return render.index_2(movies)
        else:
            raise NullException

if __name__=='__main__':
    app.run()
