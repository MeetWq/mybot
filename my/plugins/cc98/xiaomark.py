import requests
import json
from config import *


def get_short_url(long_url):
    url = 'https://api.xiaomark.com/v1/link/create'
    content_type = 'application/json'
    api_key = xiaomark_api_key
    group_sid = xiaomark_group_sid

    data = {'apikey': api_key, "origin_url": long_url, "group_sid": group_sid}
    headers = {'Content-Type': content_type}
    response = requests.post(url=url, data=json.dumps(data), headers=headers).json()

    if response['code'] != 0:
        return None
    else:
        return response['data']['link']['url']
