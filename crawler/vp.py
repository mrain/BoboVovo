import requests
import time
import re

import slugify
from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import pc

url = 'http://dota2.vpgame.com'

def convert_time(t):
    if t.strip() == 'Live':
        return 0
    s = t.strip().split()
    absolute = int(s[0])
    if s[1] in {'m'}:
        multiplier = 1
    elif s[1] in {'h'}:
        multiplier = 60
    elif s[1] in {'d'}:
        multiplier = 1440
    return absolute * multiplier * 60

def crawl_details(webpage):
    time.sleep(1)
    timestamp = time.time()
    response = requests.get(webpage, headers=headers)
    s = soup(response.text, 'lxml')
    print(webpage)
    poolsize = s.find('div', {'class': 'spinach-item-tt'}).get_text(text=True, recursive=False)
    print(poolsize)
    series = s.find('span', {'class': 'tt-right'}).text
    matchtime_rlt = convert_time(s.find('div', {'class': 'time'}).text)
    bestof = s.find('div', {'class': 'kind-match'}).text.strip()[-1]
    teamA = s.find('div', {'class': 'op1'}).find('span').text
    oddA = pc(s.find('div', {'class': 'op1'}).find('label', {'class': 'percent'}).text)
    teamB = s.find('div', {'class': 'op2'}).find('span').text
    oddB = pc(s.find('div', {'class': 'op2'}).find('label', {'class': 'percent'}).text)
    returnA = s.find('div', {'class': 'left-reward'}).find('div', {'class': 'value-rw appid_570'}).text
    returnA = re.search('(?P<return>[0-9\.]+) for 1', returnA).group('return')
    returnB = s.find('div', {'class': 'right-reward'}).find('div', {'class': 'value-rw appid_570'}).text
    returnB = re.search('(?P<return>[0-9\.]+) for 1', returnB).group('return')
    if s.find('span', {'class': 'result-2 rc'}):
        z = re.search('(?P<scoreA>[0-9]) : (?P<scoreB>[0-9])', s.find('span', {'class': 'result-2 rc'}).text)
        result = (int(z.group('scoreA')), int(z.group('scoreB')))
    else:
        result = (-1, -1)
    return Match(
        active=matchtime_rlt > 0,
        matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
        webpage=webpage,
        series=series,
        teams=(teamA, teamB),
        odds=(oddA, oddB),
        returns=(returnA, returnB),
        result=result,
        bestof=bestof,
        )

def crawl_full():
    page = 1
    while True:
        params = {'page': page}
        response = requests.get(url + '/home/index.html', headers=headers, params=params)
        timestamp = time.time()
        matches = soup(response.text, 'lxml').find('div', {'class': 'items'}).findAll('a')
        for match in matches:
            if not 'dota2-icon' in match.find('i').get('class'):
                continue
            href = url + match.get('href')
            yield crawl_details(href)
        if len(matches) < 10:
            break
        page += 1

def crawl_home():
    page = 1
    while True:
        params = {'page': page}
        response = requests.get(url + '/home/index.html', headers=headers, params=params)
        timestamp = time.time()
        matches = soup(response.text, 'lxml').find('div', {'class': 'items'}).findAll('a')
        for match in matches:
            if not 'dota2-icon' in match.find('i').get('class'):
                continue
            series = match.find('span', {'class': 'spinach-league'}).text
            href = url + match.get('href')
            matchtime_rlt = convert_time(match.find('div', {'class': 'pull-right spinach-league-right'}).text)
            yield Match(
                active=matchtime_rlt > 0,
                matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
                webpage=href,
                series=series,
                )
        if len(matches) < 10:
            break
        page += 1

def flowtest():
    print('vp crawler flowtest')
    print('crawling http://dota2bestyolo.com/')
    print('Result:')
    for s in crawl_full():
        print(s)
