#-*- coding: utf8 -*-

from requests import get
import pandas as pd
import os
from bs4 import BeautifulSoup

HEADERS = {
    'user-agent':
    ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
     ),  # noqa: E501
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en'),
    'origin': ('http://stats.nba.com')
}


if __name__ == '__main__':
    res = get("http://cbadata.sports.sohu.com/sch/all/",
              headers=HEADERS, timeout=50)
    soup = BeautifulSoup(res.content)
    table = soup.find('div', {'class': "cutE"}).findAll('tr')
    headers = table[0].text.split()
    data = []
    for row in table[1:]:
        if '已结束' not in row.findAll('td')[2].text:
            continue
        item = {}
        for i in [0, 1, 2]:
            item[headers[i]] = row.findAll('td')[i].text
        url = "http://cbadata.sports.sohu.com" + \
            row.findAll('td')[3].find(
                'a').attrs['href'].replace('/show/', '/content/')
        detail_res = get(url)
        detail_soup = BeautifulSoup(detail_res.content)
        for div in detail_soup.findAll('div', {'class': "cutE"}):
            team = div.find('h2').text
            trs = div.findAll('tr')
            player_headers = trs[0].text.split()
            for tr in trs[1:-1]:
                player_item = item.copy()
                tds = tr.findAll('td')
                player_item['首发'] = 1 if tds[0].find('img') else 0
                for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
                    player_item[player_headers[i]] = tds[i].text
                player_item['编号'] = tds[1].find(
                    'a').attrs['href'].split('/')[-1]
                player_item['球队'] = team
                data.append(player_item)
    result = []
    for item in data:
        new_item = {}

        for key in ['球员', '球队', '进攻', '篮板', '时间', '状态', '首发', '出场时间', '助攻', '抢断', '盖帽', '失误', '犯规', '得分', '编号']:
            new_item[key] = item[key]
        for key in ['三分球', '两分球', '罚球']:
            new_item[key + '命中'], new_item[key + '出手'] = item[key].split('-')
        new_item['对阵'] = [team for team in item['对阵'].split(
            ' VS ') if team != item['球队']][0]
        result.append(new_item)

    df = pd.DataFrame(result, columns=['球员', '球队', '对阵', '时间', '状态', '首发', '出场时间', '三分球命中', '三分球出手',
                                       '两分球命中', '两分球出手', '罚球命中', '罚球出手', '进攻', '篮板', '助攻', '抢断', '盖帽', '失误', '犯规', '得分', '编号'], index=None)
    df.to_csv('data/cba_boxscores.csv', index=None, encoding="utf_8_sig")
