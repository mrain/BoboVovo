import requests
import time
import re

import slugify
from lxml import etree
from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import tbd

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
    time.sleep(1)
    timestamp = time.time()
    response = requests.get(webpage, headers=headers)
    s = soup(response.text, 'lxml')
    matchtime_rlt = convert_time(s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;width: 33%;'}).text)
    matchtime = matchtime_rlt + timestamp
    bestof = s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;text-align: center;width: 28%;'}).text[-1]
    matchtime_abs = s.find('div', {'class': 'half', 'style': 'font-size: 0.8em;text-align: right;width: 33%;'}).text
    winner = None
    teamA = s.find('span', {'style': 'width: 45%; float: left; text-align: right'}).find('b').text
    if '(win)' in teamA:
        teamA = teamA[:-6]
        winner = teamA
    oddA = float(s.find('span', {'style': 'width: 45%; float: left; text-align: right'}).find('i').text[:-1]) / 100
    teamB = s.find('span', {'style': 'width: 45%; float: left; text-align: left'}).find('b').text
    if '(win)' in teamB:
        teamB = teamB[:-6]
        winner = teamB
    oddB = float(s.find('span', {'style': 'width: 45%; float: left; text-align: left'}).find('i').text[:-1]) / 100
    returnA = 1 + float(s.find('div', {'style': 'float: left; margin: 0.25em 2%;'}).text[5:-6])
    returnB = 1 + float(s.find('div', {'style': 'float: right; margin: 0.25em 2%;'}).text[5:-6])
    return Match(
        active=matchtime_rlt > 0,
        matchtime=time.strftime('%Y-%m-%d %H:%M', time.localtime(matchtime_rlt + timestamp)),
        webpage=webpage,
        serie=series,
        teams=(teamA, teamB),
        odds=(oddA, oddB),
        returns=(returnA, returnB),
        notes=notes,
        winner=winner,
        )

def crawl_full():
    url = 'http://dota2lounge.com/'
    response = requests.get(url, headers=headers)
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
    with open('matches_d2l', 'w') as fw:
        for match in matches:
            href = url + match.find('a').get('href')
            series = match.find('div', {'class': 'eventm'}).text
            notes = re.sub(r'[Â\xa0]+', '', match.find('span', {'style': 'font-weight: bold; color: #D12121'}).text)
            s = crawl_details(href, series, notes)
            yield s

def crawl_home():
    url = 'http://dota2lounge.com/'
    response = requests.get(url, headers=headers)
    timestamp = time.time()
    matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
    with open('matches_d2l', 'w') as fw:
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
                serie=series,
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
