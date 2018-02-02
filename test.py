#coding=utf-8
#导入sqlite3模块
import sqlite3
#连接数据库/新建数据库
db=sqlite3.connect('MovieSite.db')
#创建游标
cu=db.cursor()
#建表
sql = "create table test (id integer primary key, pid integer,name varchar(10))"
cu.execute(sql)
#<sqlite3.Cursor object at 0x0000000004172650>
#插入数据
sql = "insert into test values(1,1,'xiaomai')"
cu.execute(sql)
#<sqlite3.Cursor object at 0x0000000004172650>
sql = "insert into test values(2,2,'bird')"
cu.execute(sql)
#<sqlite3.Cursor object at 0x0000000004172650>
#提交
db.commit()
