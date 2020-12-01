#!/usr/bin/env python
# -*- coding:utf-8 -*-

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = ''  # 替换为用户的 secretId
secret_key = ''  # 替换为用户的 secretKey

region = 'ap-chengdu'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)

response = client.head_object(
    Bucket='',
    Key="1080x2400.jpg"  # private  /  public-read / public-read-write
)

print(response) # Content-Length /  23501b30352d1258c03957a6659286a4

# https://s25-15131255089-1585271608-1251317460.cos.ap-chengdu.myqcloud.com/11.png
#https://13598862878-1605257049-1301957328.cos.ap-chengdu.myqcloud.com/1080x2400.jpg
