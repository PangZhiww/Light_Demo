#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
pip3 install requests
"""
import requests

res = requests.get('https://13598862878-1605510443-1301957328.cos.ap-chengdu.myqcloud.com/1605690976307_1080x2160.jpg')

print(res.content)
