import requests
import re
import json
import pandas as pd


def get_data(season=2020):
    cookies = {
        '__stripe_mid': 'cf3e39b9-79c7-47b8-88f5-7243fa310a93dd22d9',
        '__stripe_sid': '3e1e7eb0-7ba8-4b42-bd9e-8610f8dd8bbcd0cd7a',
        '_ga': 'GA1.2.390842309.1631192573',
        '_gid': 'GA1.2.800546148.1631192573',
        'connect.sid': 's%3AbFEp5NIJSekVyhVL7ectyJ8ouJJrjtme.KL6hK81jeKX%2FqsBK%2FSWN7Vw0jRoeW1aY42wP2cYQqfo',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Host': 'dunksandthrees.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    params = (
        ('season', str(season)),
    )

    response = requests.get('https://dunksandthrees.com/epm', headers=headers, params=params, cookies=cookies)
    element = re.search(r"var data = `({.*})`", response.text, flags=re.MULTILINE)
    if not element:
        return None
    json_text = element.group(1)
    data = json.loads(json_text)
    print(data.keys())
    pd.DataFrame(data['player_stats']).to_csv(f"{season}_epm.csv", index=False)


if __name__ == '__main__':
    get_data(2021)
