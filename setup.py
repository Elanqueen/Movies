#coding=utf-8
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description':'Movies Site',
    'author':'My name',
    'url':"url to get it at .",
    'download_url':'My email',
    'version':'0.1',
    'install_requires':['nose'],
    'packages':['name'],
    'scripts':[],
    'name':'projectname'
}

setup(**config)