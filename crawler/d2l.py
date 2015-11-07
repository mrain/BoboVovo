import requests
import time

import re
import slugify
from lxml import etree
from bs4 import BeautifulSoup as soup

from utils import headers
from utils import Match
from utils import tbd

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
    return absolute * multiplier * sign

def crawl_details(webpage, series, notes):
    print('fetching ' + webpage)
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

#s = crawl_details('http://dota2lounge.com/match?m=9794', 'summit', None)
#print(s)

url = 'http://dota2lounge.com/'
response = requests.get(url, headers=headers)
matches = soup(response.text, 'lxml').findAll('div', {'class': 'matchmain'})
with open('matches_d2l', 'w') as fw:
    for match in matches:
        href = url + match.find('a').get('href')
        #potential = []
        #for value in half_tag:
        #    if 'for' in value.text:
        #        potential.append(value.text.strip()[5:8])
        matchinfo = re.split(r'[\nÂ\xa0]+', match.text.strip())

        notes = None
        if len(matchinfo) == 5:
            t, series, teamA, _, teamB = matchinfo
        if len(matchinfo) == 6:
            t, notes, series, teamA, _, teamB = matchinfo
        s = crawl_details(href, series, notes)
        fw.write(str(s))
        print(str(s))
        #fw.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n'.format(convert_time(t), event, team1[:-3], team1[-3:], potential[0], team2[:-3], team2[-3:], potential[1], note))
        #fw.flush()
