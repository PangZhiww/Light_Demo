import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 's28.settings')
django.setup()

from web import models

# 往数据库添加数据：链接数据库、操作、关闭链接
models.UserInfo.objects.create(username='陈硕', email='chenshuo@live.com', mobile_phone='1383838383',
                               password='123456789')
