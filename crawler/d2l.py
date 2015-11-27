import requests
import time
import re

import slugify
from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import pc

url = 'http://dota2lounge.com/'

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
    return absolute * multiplier * sign * 60

def crawl_details(webpage, series, notes):
    time.sleep(2)
    timestamp = time.time()
    response = requests.get(webpage, headers=headers)
    if 'nyx nyx' in response.text:
        time.sleep(15)
        assert(0)
    s = soup(response.text, 'lxml')
    matchtime_rlt = convert_time(s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;width: 33%;'}).text)
    matchtime = matchtime_rlt + timestamp
    botext = s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;text-align: center;width: 28%;'}).text
    if 'Series' in botext:
        bestof = int(botext[0])
    else:
        bestof = int(botext[-1])
    try:
        poolsize = re.search('placed (?P<no>[0-9]+)', [x.text.strip() for x in s.findAll('div', {'class': 'full'}) if 'placed' in x.text][0]).group('no')
    except Exception:
        poolsize = 0
    matchtime_abs = s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;text-align: right;width: 33%;'}).text
    scoreA, scoreB = (-1, -1)
    teamA = s.find('span', {'style': 'width: 45%; float: left; text-align: right'}).find('b').text
    if '(win)' in teamA:
        teamA = teamA[:-6]
        scoreA = int(bestof / 2) + 1
    oddA = pc(s.find('span', {'style': 'width: 45%; float: left; text-align: right'}).find('i').text)
    teamB = s.find('span', {'style': 'width: 45%; float: left; text-align: left'}).find('b').text
    if '(win)' in teamB:
        teamB = teamB[:-6]
        scoreB = int(bestof / 2) + 1
    oddB = pc(s.find('span', {'style': 'width: 45%; float: left; text-align: left'}).find('i').text)
    if s.find('div', {'style': 'float: left; margin: 0.25em 2%;'}):
        returnA = 1 + float(s.find('div', {'style': 'float: left; margin: 0.25em 2%;'}).text[5:-6])
    else:
        returnA = -1
    if s.find('div', {'style': 'float: right; margin: 0.25em 2%;'}):
        returnB = 1 + float(s.find('div', {'style': 'float: right; margin: 0.25em 2%;'}).text[5:-6])
    else:
        returnB = -1
    return Match(
        active=matchtime_rlt > 0,
        matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
        webpage=webpage,
        series=series,
        teams=(teamA, teamB),
        odds=(oddA, oddB),
        returns=(returnA, returnB),
        notes=notes,
        result=(scoreA, scoreB),
        poolsize=poolsize,
        bestof=bestof,
        tostart=matchtime_rlt,
        )

def crawl_full():
    response = requests.get(url, headers=headers)
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
    for match in matches:
        matchtime_rlt = convert_time(match.find('div', {'class': 'whenm'}).find(text=True, recursive=False))
        if matchtime_rlt < -3600:
            continue
        href = url + match.find('a').get('href')
        series = match.find('div', {'class': 'eventm'}).text
        notes = re.sub(r'[Â\xa0]+', '', match.find('span', {'style': 'font-weight: bold; color: #D12121'}).text)
        s = crawl_details(href, series, notes)
        yield s

def crawl_home():
    response = requests.get(url, headers=headers)
    timestamp = time.time()
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
    for match in matches:
        matchtime_rlt = convert_time(match.find('div', {'class': 'whenm'}).find(text=True, recursive=False))
        series = match.find('div', {'class': 'eventm'}).text
        notes = re.sub(r'[Â\xa0]+', '', match.find('span', {'style': 'font-weight: bold; color: #D12121'}).text)
        a = match.find('a')
        href = url + a.get('href')
        teamtext = a.findAll('div', {'class': 'teamtext'})
        teamA = teamtext[0].find('b').text
        oddA = teamtext[0].find('i').text
        teamB = teamtext[1].find('b').text
        oddB = teamtext[1].find('i').text
        yield Match(
            active=matchtime_rlt > 0,
            matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
            webpage=href,
            series=series,
            teams=(teamA, teamB),
            odds=(oddA, oddB),
            notes=notes,
            )

def flowtest():
    print('d2l crawler flowtest')
    print('crawling http://dota2lounge.com/')
    print('Result:')
    for s in crawl_full():
        print(s)
