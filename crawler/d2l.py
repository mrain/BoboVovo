import requests
import time

import re
import slugify
from lxml import etree
from bs4 import BeautifulSoup as soup

from utils import headers

def convert_time(t):
    s = t.split()
    absolute = int(s[0])
    if s[1] in {'minute', 'minutes'}:
        multiplier = 1
    elif s[1] in {'hour', 'hours'}:
        multiplier = 60
    elif s[1] in {'day', 'days'}:
        multiplier = 1440
    if s[2] == 'ago':
        sign = -1
    elif s[2] == 'from':
        sign = 1
    if len(s) >= 4 and s[3] == 'LIVE':
        live = 1
    else:
        live = -1
    x = absolute * multiplier * sign
    if x > 0:
        return '+' + str(x)
    if x < 0:
        return str(x)

url = 'http://dota2lounge.com/'
response = requests.get(url, headers=headers)
matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
with open('matches_d2l', 'w') as fw:
    for match in matches:
        href = match.find('a').get('href')
        print('fetching ' + url + href)
        time.sleep(1)
        response = requests.get(url + href, headers=headers)
        half_tag = soup(response.text, 'lxml').findAll('div', {'class': 'half'})
        potential = []
        for value in half_tag:
            if 'for' in value.text:
                potential.append(value.text.strip()[5:8])
        matchinfo = re.split(r'[\nÂ\xa0]+', match.text.strip())

        note = 'No-note'
        if len(matchinfo) == 5:
            t, event, team1, _, team2 = matchinfo
        if len(matchinfo) == 6:
            t, note, event, team1, _, team2 = matchinfo
        fw.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n'.format(convert_time(t), event, team1[:-3], team1[-3:], potential[0], team2[:-3], team2[-3:], potential[1], note))
        fw.flush()
