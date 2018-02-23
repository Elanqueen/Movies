#-*- coding: utf-8 -*-

'''
此处采用web.db中方法，实现对数据库的操作
'''

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

#配置URL和匹配页面
urls=(
    '/movie_des/(\d+)','Movie',
    '/','GrabData',
    '/cast/(.*)','Cast',
    '/director/(.*)','Director'
)

app = web.application(urls,globals())
render = web.template.render('templates/',base='layout')  #加载HTML模板

#抛出异常设定
class NullException(BaseException):"It is null, Please check."
db=web.database(dbn="sqlite",db="MovieSite.db")

class Movie:
    def GET(self,movie_id):
        '''cu = db.cursor()
        cu.execute("select * from movie where id = ?",movie_id)
        movie=cu.fetchone()'''
        #db = sqlite3.connect("MovieSite.db")
        #movie=db.execute("select * from mvgrab where mvid = ?",(movie_id,)).fetchone()
        condition='mvid='+movie_id
        movie=db.select('mvgrab',where='mvid=$int(movie_id)',vars=locals())[0]
        #db.close()
        if movie!=[]:
            return render.movie_des(movie)
        else:
            raise NullException

class GrabData:
    """从豆瓣网站抓取排名前250的电影列表"""
    def GET(self):
        self.grab_movie_to_db()
        #db = sqlite3.connect("MovieSite.db")
        #movies=db.execute("select * from mvgrab limit 20").fetchall()
        movies=db.select('mvgrab',limit=10)
        #db.close()
        return render.index(movies)

    def POST(self):
        #db = sqlite3.connect("MovieSite.db")
        #db.text_factory=str
        form = web.input(title="霸王别姬") # 默认值设置：name="霸王别姬"name='阿甘正传'
        if form.title:
            #movie=db.execute("select * from mvgrab where title = '霸王别姬'").fetchone()
            # movie=db.execute("select * from mvgrab where title = %s" % form.title).fetchone()
            #title="%"+form.title+"%"
            #movies=db.execute("select * from mvgrab where title like ?",(unicode(title),)).fetchall()
            #movies=db.select('mvgrab',where='title like $unicode(title)')
            condition=r'title like "%'+form.title+r'%"'
            #print condition
            movies=db.select('mvgrab',where=condition)
            #count = db.execute("select count(*) as count from mvgrab where title like ?",
              #                 (unicode(title),)).fetchall()
            count=db.query('select count(*) as count from mvgrab where '+ condition)
            count=count[0]['count']
            #db.close()
            return render.index(movies,count,form.title)
        #else:
            #return render.index([],0,"")

    def grab_movie_to_db(self):
        '''将通过豆瓣API抓取到的排名前250的电影信息存入数据库'''
        fp = urllib.urlopen("https://api.douban.com/v2/movie/top250?strat=0&count=50")
        data = fp.read()
        data_js = json.loads(data)
        movie_250 = data_js['subjects']
        movies = []  # 存储数据添加入数据库
        count=1
        db.delete('mvgrab',where='id>0')
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
        #db = sqlite3.connect("MovieSite.db")
        #db.execute("delete from mvgrab")
        #db.executemany("insert into mvgrab values(?,?,?,?,?,?,?,?,?,?,?,?)", movies)
            db.insert('mvgrab',id=count,mvid=int(movie['id']),title=movie['title'],rating=movie['rating']['average'],
                      original=movie['original_title'],directors=directors,alt=movie['alt'],
                      year=movie['year'],subtype=movie['subtype'].decode(),images=movie['images']['medium'],
                      genres=genres,casts=casts)
        #db.commit()
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
        #db=sqlite3.connect("MovieSite.db")
        cast_name="%"+cast+"%"
        #movies=db.execute("select * from mvgrab where casts like ?",(unicode(cast_name),)).fetchall()
        #movies=db.query("select * from mvgrab where casts like $x",vars(x=unicode(cast_name)))
        condition= r'casts like "%' + cast + r'%"'
        movies = db.select('mvgrab',where=condition)
        if movies:
            return render.index(movies)
        else:
            raise NullException

class Director:
    def GET(self,director):
        #db = sqlite3.connect("MovieSite.db")
        cast_name = "%" + director + "%"
        #movies = db.execute("select * from mvgrab where directors like ?", (unicode(cast_name),)).fetchall()
        condition=r'directors like "%'+director+r'%"'
        movies=db.select('mvgrab',where=condition)
        if movies:
            return render.index(movies)
        else:
            raise NullException

if __name__=='__main__':
    app.run()
