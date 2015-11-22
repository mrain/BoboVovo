import requests
import time
import re

import slugify
from lxml import etree
from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import pc

url = 'http://dota2bestyolo.com/'

def convert_time(t):
    s = t.split()
    absolute = int(s[0])
    if s[1] in {'min', 'mins'}:
        multiplier = 1
    elif s[1] in {'hr', 'hrs'}:
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
    return absolute * multiplier * sign * 60

def crawl_details(webpage):
    time.sleep(1)
    timestamp = time.time()
    response = requests.get(webpage, headers=headers)
    s = soup(response.text, 'lxml')
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
    response = requests.get(url, headers=headers)
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'blk2'})
    for match in matches:
        series = match.find('div', {'class': 'series'}).text
        if series.startswith('*'): # which indicates non-dota2 series/match
            continue
        href = url + match.find('div', {'class': 'view-btn'}).find('a').get('href')[1:]
        s = crawl_details(href)
        yield s

def crawl_home():
    response = requests.get(url, headers=headers)
    timestamp = time.time()
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'blk2'})
    for match in matches:
        series = match.find('div', {'class': 'series'}).text
        if series.startswith('*'): # which indicates non-dota2 series/match
            continue
        matchtime_rlt = convert_time(match.find('div', {'class': 'time'}).find(text=True, recursive=False))
        teamA = match.find('div', {'class': 'title-opt'}).find('h3').text
        oddA = pc(match.find('div', {'class': 'title-opt'}).find('label', {'class': 'percent'}).text)
        teamB = match.find('div', {'class': 'title-opt right-bg'}).find('h3').text
        oddB = pc(match.find('div', {'class': 'title-opt right-bg'}).find('label', {'class': 'percent'}).text)
        href = url + match.find('div', {'class': 'view-btn'}).find('a').get('href')[1:]
        yield Match(
            active=matchtime_rlt > 0,
            matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
            webpage=href,
            series=series,
            teams=(teamA, teamB),
            odds=(oddA, oddB),
            notes=None,
            )

def flowtest():
    print('yolo crawler flowtest')
    print('crawling http://dota2bestyolo.com/')
    print('Result:')
    for s in crawl_full():
        print(s)
