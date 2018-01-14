#-*- coding: utf8 -*-

from requests import get
import pandas as pd
import os

CATEGORIES = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman',
              'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen',
              'OffRebound', 'Misc']
BY_TYPES = ['team', 'player']
PLAYER_VALUE_KEYS = [u'P', u'GP', u'Poss', u'Time', u'Points',
                     u'FGM', u'FGA', u'PPP', u'WorsePPP', u'BetterPPP',
                     u'FG', u'aFG', u'FT', u'TO', u'SF', u'PlusOne', u'Score', ]
VALUE_KEYS = {'team': PLAYER_VALUE_KEYS[1:], 'player': PLAYER_VALUE_KEYS}
PLAYER_PRIMARY_KEYS = ['Playtype', 'Team', 'Player']
PRIMARY_KEYS = {
    'team': PLAYER_PRIMARY_KEYS[:-1], 'player': PLAYER_PRIMARY_KEYS}

TYPES = ['offensive', 'defensive']

HEADERS = {
    'user-agent':
    ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
     ),  # noqa: E501
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en'),
    'origin': ('http://stats.nba.com')
}


def api(category, type, by_type):
    return "http://stats-prod.nba.com/wp-json/statscms/v1/synergy/#{by_type}/?season=2017&category=#{category}&limit=500&names=#{type}&seasonType=Reg".replace(
        '#{category}', category).replace('#{type}', type).replace('#{by_type}', by_type)


if __name__ == '__main__':
    for by_type in BY_TYPES:
        for type in TYPES:
            items = []
            print(type)
            for category in CATEGORIES:
                print(category)
                res = get(api(category, type, by_type),
                          headers=HEADERS, timeout=50)
                res.raise_for_status()
                for row in res.json()['results']:
                    if 'PlayerFirstName' in row:
                        item = {'Player': ', '.join(
                            [row['PlayerFirstName'], row['PlayerLastName']]),
                            'Team': row['TeamName'], 'Playtype': category}
                    else:
                        item = {'Team': row['TeamName'], 'Playtype': category}
                    for key in VALUE_KEYS[by_type]:
                        item[key] = row[key]
                    items.append(item)
            print(len(items))
            df = pd.DataFrame(
                items)[PRIMARY_KEYS[by_type] + VALUE_KEYS[by_type]]
            df.to_csv(os.path.join('data', by_type + '_playtype_' +
                                   type + '.csv'), index=False)
