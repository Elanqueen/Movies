#coding=utf-8
import urllib
import json
fp = urllib.urlopen("https://api.douban.com/v2/movie/top250?strat=0&count=5")
data = fp.read()
#print data
data_js=json.loads(data)
movie_250 = data_js['subjects']
movies=[]
for movie in movie_250:
    movies.append({"id":movie['id'],"title":movie['title']})
    print movie['title'],movie['id']