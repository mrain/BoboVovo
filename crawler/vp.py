# -*- coding: utf-8 -*-

import requests
import datetime
import time
import re

import slugify
from bs4 import BeautifulSoup as soup
from calendar import month_abbr as month
month = list(month)

from .utils import headers
from .utils import Match
from .utils import pc

url = 'http://dota2.vpgame.com'

def convert_time(t):
    g = re.match('Schedule : (?P<dd>[0-9]{2})[a-z]{2} (?P<month_abbr>[a-zA-z]{3}) , (?P<yyyy>[0-9]{4}) (?P<hh>[0-9]{2}):(?P<mm>[0-9]{2}):(?P<ss>[0-9]{2})', t.strip())
    print(t)
    print('{0}-{1}-{2} {3}:{4}'.format(g.group('yyyy'), month.index(g.group('month_abbr')), g.group('dd'), g.group('hh'), g.group('mm')))
    return '{0}-{1}-{2} {3}:{4}'.format(g.group('yyyy'), month.index(g.group('month_abbr')), g.group('dd'), g.group('hh'), g.group('mm'))

def crawl_details(webpage, series, notes):
    time.sleep(1)
    timestamp = time.time()
    response = requests.get(webpage, headers=headers)
    s = soup(response.text, 'lxml')
    poolsize = int(''.join(s.find('div', {'class': 'spinach-item-tt'}).find_all(text=True,recursive=False)).strip())
    matchtime = convert_time(s.find('p', {'class': 'pull-right'}).find('span', {'class': 'mr-5'}).text)
    matchtime_datetime = datetime.datetime.strptime(matchtime, '%Y-%m-%d %H:%M')
    bestof = int(s.find('span', {'class': 'f-14'}).text.strip()[-1])
    teams = [x.find('p', {'class': 'spinach-corps-name ellipsis'}).text.strip() for x in s.find_all('div', {'class': 'spinach-corps-data'})]
    odds = [pc(x.text.strip()) for x in s.find_all('p', {'class': 'text-center f-14 mt-5'})]
    returns = [1 + float(x.find('span', {'class': 'vp-item-odds'}).text.strip()) for x in s.find_all('div', {'class': 'spinach-corps-data'})]
    result = (-1, -1)
    status = s.find('p', {'class': 'pull-right'}).text
    if 'Cleared' in status:
        result = s.find('span', {'class': 'spinach-team-score'}).text.strip().split(':')
        active = False
    elif 'Cancel' in status or 'live' in status or 'Live' in status:
        active = False
    else:
        active = True
    return Match(
        active=active,
        matchtime=matchtime,
        webpage=webpage,
        series=series,
        teams=teams,
        odds=odds,
        returns=returns,
        result=result,
        poolsize=poolsize,
        bestof=bestof,
        notes=notes,
        tostart=(matchtime_datetime - datetime.datetime.now()).total_seconds(),
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
            series = match.find('span', {'class': 'spinach-league'}).text.strip().split('【')[0]
            try:
                notes = match.find('span', {'class': 'spinach-league'}).text.strip().split('【')[1][:-1]
            except IndexError:
                notes = None
            href = url + match.get('href')
            yield crawl_details(href, series, notes)
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
            series = match.find('span', {'class': 'spinach-league'}).text.strip().split('【')[0]
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
    print('crawling http://dota2.vpgame.com')
    print('Result:')
    print(crawl_details('http://dota2.vpgame.com/guess-match-118525.html', 'test', 'test'))
    for s in crawl_full():
        print(s)
