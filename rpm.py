#-*- coding: utf8 -*-

from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
from datetime import datetime


def api(page=1, year=2019):
    return "http://www.espn.com/nba/statistics/rpm/_/year/#{year}/page/#{page}".replace(
        '#{page}', str(page)).replace('#{year}', str(year))


def parse_datetime(updated_at):
    year = str(datetime.today().year)
    day_str, time_str = updated_at.split(year)
    day_str = datetime.strptime(
        day_str + year, '%B %d, %Y').strftime('%Y-%m-%d')
    return day_str + time_str


if __name__ == '__main__':
    max_page = 1000
    page = 1
    data = []
    while True:
        print(page)
        soup = BeautifulSoup(
            get(api(page=page, year=2020)).content, "html.parser")
        trs = soup.find('div', {'id': 'my-players-table'}).find('div',
                                                                {'class': 'mod-content'}).find('table').find_all('tr')
        updated_at = parse_datetime(re.findall(
            r"Last Updated: (.*)", soup.find('div', {'class': 'mod-page-header'}).text)[0])
        headers = [td.text for td in trs.pop(0)]
        for tr in trs:
            player = {}
            for i, td in enumerate(tr):
                player[headers[i]] = td.text
            data.append(player)
        page += 1
        max_page = int(
            soup.find('div', {'class': 'page-numbers'}).text.split(' of ')[-1])
        if page > max_page:
            break
        time.sleep(2)
    print(headers)
    df = pd.DataFrame(data)[headers]
    df.to_csv(os.path.join('data', 'rpm.csv'), index=False)
    df.to_csv(os.path.join('data', 'rpm', updated_at + '.csv'), index=False)
