import nba_py
from nba_py import team, game, constants, player
import json
import os
import pandas as pd
import time

TEAMS_FILE = 'teams.csv'

VALUE_KEYS = [u'GP', u'MIN', u'PLUS_MINUS',
              u'OFF_RATING', u'DEF_RATING', u'NET_RATING']
PRIMARY_KEYS = [u'GROUP_SET', u'TEAM_ID', u'TEAM_ABBREVIATION',
                u'TEAM_NAME', u'VS_PLAYER_ID', u'VS_PLAYER_NAME']
MEASURE_TYPES = ['Base', 'Advanced', 'Misc',
                 'Four Factors', 'Scoring', 'Opponent', ]

if __name__ == '__main__':
    if os.path.exists(TEAMS_FILE):
        teams = pd.DataFrame.from_csv(TEAMS_FILE)
    else:
        teams = team.TeamList().info().dropna()
        teams.to_csv(TEAMS_FILE)
    for measure_type in MEASURE_TYPES:
        all = None
        file_name = 'data/onoff_' + measure_type.lower().replace(' ', '_') + '.csv'
        for index, row in teams.iterrows():
            per_mode = constants.PerMode.Per100Possessions if measure_type == 'Misc' else constants.PerMode.Default
            data = team.TeamPlayerOnOffDetail(
                team_id=row['TEAM_ID'], measure_type=measure_type, per_mode=per_mode)
            on_court = data.on_court().drop([u'COURT_STATUS'], 1)
            off_court = data.off_court().drop([u'COURT_STATUS'], 1)

            overall = on_court.merge(
                off_court, left_on=PRIMARY_KEYS,
                right_on=PRIMARY_KEYS, how='outer',
                suffixes=['_ON', '_OFF']).dropna()

            value_keys = [item for item in list(
                on_court.columns) if item not in PRIMARY_KEYS and "RANK" not in item]
            ordered_overall = overall[['TEAM_NAME', 'VS_PLAYER_NAME']]

            for name in value_keys:
                keys = []
                for suffix in ['_ON', '_OFF']:
                    full_name = name + suffix
                    value = overall[[full_name]]
                    ordered_overall[full_name] = value
                    keys.append(full_name)
                ordered_overall['_'.join([name, 'DIFF'])] = ordered_overall[
                    keys[0]] - ordered_overall[keys[1]]
            if all is not None:
                all = pd.concat([all, ordered_overall])
            else:
                all = ordered_overall
            print all
            time.sleep(4)
        all.to_csv(file_name, index=False)
