from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from io import BytesIO

import click
import imageio
import time
import numpy
from PIL import Image
import pandas as pd


def take_screenshot(driver, element=None):
    screenshot_from_selenium = BytesIO(driver.get_screenshot_as_png())

    screenshot = Image.open(screenshot_from_selenium)
    if element:
        location = element.location
        size = element.size
        print(location)
        print(size)
        left = int(location['x']) * 2
        top = int(location['y']) * 2
        right = int(location['x'] + size['width']) * 2
        bottom = int(location['y'] + size['height']) * 2
        print(left, top, right, bottom)
        screenshot = screenshot.crop((left, top, right, bottom))
    # screenshot = Image.new("RGB", screenshot_no_bg.size, (255, 255, 255))
    # screenshot.paste(screenshot_no_bg, mask=screenshot_no_bg.split()[3])

    # # retina display + chrome ends up with screenshots that are too large, resize those
    # if screenshot.width > width:
    #     screenshot = screenshot.resize(
    #         (width, int(screenshot.height * (width / screenshot.width))))

    # if resize:
    #     screenshot_canvas = screenshot_canvas.resize((960, 600))

    return numpy.asarray(screenshot)


def gifs_by_team(teams, keys, driver):
    for team in teams:
        team_frames = []
        for key in keys:
            print(team, key)
            element = driver.find_element_by_id(
                'viz_container').find_element_by_css_selector('rect')
            print(element)
            # hover = ActionChains(driver).move_to_element(element)
            # hover.perform()
            driver.execute_script("document.getElementById('" + team +
                                  "-" + key + "').dispatchEvent(new MouseEvent('mouseover'))")
            frame = take_screenshot(driver, element=element)
            team_frames.append(frame)
            imageio.mimwrite('gifs/teams/' + team + '.gif',
                             team_frames, duration=1)


def gifs_by_position(keys, driver, df):
    for key in keys:
        key_frames = []
        teams = list(df.sort_values(key, ascending=False)['RPM'])
        for team in teams:
            print(team, key)
            element = driver.find_element_by_id(
                'viz_container').find_element_by_css_selector('rect')
            print(element)
            # hover = ActionChains(driver).move_to_element(element)
            # hover.perform()
            driver.execute_script("document.getElementById('" + team +
                                  "-" + key + "').dispatchEvent(new MouseEvent('mouseover'))")
            frame = take_screenshot(driver, element=element)
            key_frames.append(frame)
        imageio.mimwrite('gifs/positions/' + key + '.gif',
                         key_frames, duration=0.3)


options = webdriver.ChromeOptions()
# use headless
# options.add_argument('headless')
options.add_argument('disable-web-security')
# options.add_argument('window-size=1200x600')
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(
    executable_path="chromedriver", chrome_options=options)
driver.implicitly_wait(100)
url = 'file:///Users/hang/rimzero.github.io/rpm_radar/index.html'
keys = ['PG', 'SG', 'SF', 'PF', 'C']
teams = ['MIL', 'GSW', 'BOS', 'TOR', 'UTA', 'DEN', 'PHI', 'IND', 'OKC', 'HOU', 'POR', 'NOP', 'SAS', 'MIN', 'DAL', 'LAL', 'CHO', 'LAC', 'MEM', 'MIA', 'SAC', 'BRK', 'WAS', 'ORL', 'DET', 'PHO', 'ATL', 'NYK', 'CHI', 'CLE']

driver.get(url)


def numlize(x): return int(x.replace('%', '')) if '%' in x else x


df = pd.read_csv('data/rpm.csv')
df = df.applymap(numlize)
driver.find_element_by_xpath('/html/body/table/tr[1]/th').click()
time.sleep(3)
gifs_by_position(keys, driver, df)

driver.quit()
