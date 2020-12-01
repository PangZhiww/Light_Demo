#!/usr/bin/env python
# -*- coding:utf-8 -*-

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = ''  # 替换为用户的 secretId
secret_key = ''  # 替换为用户的 secretKey

region = 'ap-chengdu'  # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

client = CosS3Client(config)


client.delete_object(
    Bucket='wangyang-1301957328',
    Key='p1.png'
)