from datetime import datetime, timedelta
import os

from requests import get
from nba_py.constants import League

HAS_PANDAS = True
try:
    from pandas import DataFrame
except ImportError:
    HAS_PANDAS = False

HAS_REQUESTS_CACHE = True
CACHE_EXPIRE_MINUTES = int(os.getenv('NBA_PY_CACHE_EXPIRE_MINUTES', 10))
try:
    from requests_cache import install_cache
    install_cache(
        cache_name='nba_cache',
        expire_after=timedelta(minutes=CACHE_EXPIRE_MINUTES))
except ImportError:
    HAS_REQUESTS_CACHE = False

# Constants
TODAY = datetime.today()
BASE_URL = 'http://stats.nba.com/stats/{endpoint}'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'user-agent':
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'),  # noqa: E501
    'Dnt': ('1'),
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate',
    'origin': ('http://stats.nba.com')
}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def _api_scrape(json_inp, ndx):
    """
    Internal method to streamline the getting of data from the json

    Args:
        json_inp (json): json input from our caller
        ndx (int): index where the data is located in the api

    Returns:
        If pandas is present:
            DataFrame (pandas.DataFrame): data set from ndx within the
            API's json
        else:
            A dictionary of both headers and values from the page
    """

    try:
        headers = json_inp['resultSets'][ndx]['headers']
        values = json_inp['resultSets'][ndx]['rowSet']
    except KeyError:
        # This is so ugly but this is what you get when your data comes out
        # in not a standard format
        try:
            headers = json_inp['resultSet'][ndx]['headers']
            values = json_inp['resultSet'][ndx]['rowSet']
        except KeyError:
            # Added for results that only include one set (ex. LeagueLeaders)
            headers = json_inp['resultSet']['headers']
            values = json_inp['resultSet']['rowSet']
    if HAS_PANDAS:
        return DataFrame(values, columns=headers)
    else:
        # Taken from www.github.com/bradleyfay/py-goldsberry
        return [dict(zip(headers, value)) for value in values]


def _get_json(endpoint, params, referer='scores'):
    """
    Internal method to streamline our requests / json getting

    Args:
        endpoint (str): endpoint to be called from the API
        params (dict): parameters to be passed to the API

    Raises:
        HTTPError: if requests hits a status code != 200

    Returns:
        json (json): json object for selected API call
    """
    h = dict(HEADERS)
    h['referer'] = 'http://stats.nba.com/{ref}/'.format(ref=referer)
    _get = get(
        BASE_URL.format(endpoint=endpoint),
        params=params,
        headers=h,
        timeout=50)
    print _get.url
    _get.raise_for_status()
    return _get.json()


class Scoreboard:
    """ A scoreboard for all games for a given day
    Displays current games plus info for a given day

    Args:
        :month: Specified month (1-12)
        :day: Specified day (1-31)
        :year: Specified year (YYYY)
        :league_id: ID for the league to look in (Default is 00)
        :offset: Day offset from which to operate

    Attributes:
        :json: Contains the full json dump to play around with
    """
    _endpoint = 'scoreboard'

    def __init__(self,
                 month=TODAY.month,
                 day=TODAY.day,
                 year=TODAY.year,
                 league_id=League.NBA,
                 offset=0):
        self._game_date = '{month:02d}/{day:02d}/{year}'.format(
            month=month, day=day, year=year)
        self.json = _get_json(
            endpoint=self._endpoint,
            params={
                'LeagueID': league_id,
                'GameDate': self._game_date,
                'DayOffset': offset
            })

    def game_header(self):
        return _api_scrape(self.json, 0)

    def line_score(self):
        return _api_scrape(self.json, 1)

    def series_standings(self):
        return _api_scrape(self.json, 2)

    def last_meeting(self):
        return _api_scrape(self.json, 3)

    def east_conf_standings_by_day(self):
        return _api_scrape(self.json, 4)

    def west_conf_standings_by_day(self):
        return _api_scrape(self.json, 5)

    def available(self):
        return _api_scrape(self.json, 6)
