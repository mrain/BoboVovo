import requests
import time
import re

import slugify
from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import pc

url = 'http://dota2bestyolo.com/'

'''
Notes on yolo:
1. Tostart, which are extracted from the "** mins from now" bar, could be manually set to a small positive number (say, 1k) after it's negative for a while. In this script active is guessed from tostart.
2. It used to happen that the time was misset to be hours before the true match live. yolo could resume the match to be betable until it's live.
3. It's staff used to put a wrong matchtime (say, 1 hr ago) when they are juz to put this match online (poolsize is small atm). They'd fix it soon after the post.
'''

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
    response = requests.get(webpage, headers=headers, timeout=45)
    response2 = requests.get('http://dota2bestyolo.com/match/index-right/id/{0}'.format(webpage.split('/')[-1]), timeout=45)
    p = re.search('>(?P<pool>[0-9]*) items has been placed', response2.text)
    poolsize = int(p.group('pool'))
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
    try:
        returnA = float(returnA) + 1.0
    except ValueError:
        returnA = -1
    returnB = s.find('div', {'class': 'right-reward'}).find('div', {'class': 'value-rw appid_570'}).text
    returnB = re.search('(?P<return>[0-9\.]+) for 1', returnB).group('return')
    try:
        returnB = float(returnB) + 1.0
    except ValueError:
        returnB = -1
    result = (-1, -1)
    if s.find('span', {'class': 'result-2 rc'}):
        if not '' in s.find('span', {'class': 'result-2 rc'}).text.strip().split(':'):
            result = s.find('span', {'class': 'result-2 rc'}).text.strip().split(':')
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
        poolsize=poolsize,
        tostart=matchtime_rlt,
        )

def crawl_full():
    response = requests.get(url, headers=headers, timeout=45)
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'blk2'})
    for match in matches:
        matchtime_rlt = convert_time(match.find('div', {'class': 'time'}).find(text=True, recursive=False))
        if matchtime_rlt < -3600:
            continue
        series = match.find('div', {'class': 'series'}).text
        if series.startswith('*'): # which indicates non-dota2 series/match
            continue
        href = url + match.find('div', {'class': 'view-btn'}).find('a').get('href')[1:]
        s = crawl_details(href)
        yield s

def crawl_home():
    response = requests.get(url, headers=headers, timeout=45)
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
