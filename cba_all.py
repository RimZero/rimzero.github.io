#-*- coding: utf8 -*-

import requests
import pandas as pd
import os
from bs4 import BeautifulSoup


if __name__ == '__main__':
    cookies = {
        'beitai_uuid_cbamobile': '095bb48a-0412-4e55-8178-bc237e775c48',
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Host': 'sportsdata.misports.cn',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'br, gzip, deflate',
        'Origin': 'https://sportsdata.misports.cn',
        'Referer': 'https://sportsdata.misports.cn/beitai/cbamobile/schedule?leagueid=401',
        'Connection': 'keep-alive',
        'Content-Length': '38',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'time': '2017/10/03',
        'type': 'down',
        'leagueid': '401'
    }

    response = requests.post('https://sportsdata.misports.cn/beitai/cbamobile/schedule/scheduleJson',
                             headers=headers, cookies=cookies, data=data)
    print(response.json())
