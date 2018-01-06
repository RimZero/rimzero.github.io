#-*- coding: utf8 -*-

from requests import get
import pandas as pd
import os

CATEGORIES = ['Transition', 'Isolation', 'PRBallHandler', 'PRRollman',
              'Postup', 'Spotup', 'Handoff', 'Cut', 'OffScreen',
              'OffRebound', 'Misc']

VALUE_KEYS = [u'P', u'GP', u'Poss', u'Time', u'Points',
              u'FGM', u'FGA', u'PPP', u'WorsePPP', u'BetterPPP',
              u'FG', u'aFG', u'FT', u'TO', u'SF', u'PlusOne', u'Score', ]
PRIMARY_KEYS = ['Playtype', 'Team', 'Player']

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


def api(category, type):
    return "http://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/?season=2017&category=#{category}&limit=500&names=#{type}&seasonType=Reg".replace(
        '#{category}', category).replace('#{type}', type)


if __name__ == '__main__':
    for type in TYPES:
        players = []
        print(type)
        for category in CATEGORIES:
            print(category)
            res = get(api(category, type), headers=HEADERS, timeout=50)
            res.raise_for_status()
            for row in res.json()['results']:
                player = {'Player': ', '.join(
                    [row['PlayerFirstName'], row['PlayerLastName']]),
                    'Team': row['TeamName'], 'Playtype': category}
                for key in VALUE_KEYS:
                    player[key] = row[key]
                players.append(player)
        print(len(players))
        df = pd.DataFrame(players)[PRIMARY_KEYS + VALUE_KEYS]
        df.to_csv(os.path.join('data', 'playtype_' + type + '.csv'), index=False)
