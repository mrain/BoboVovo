import requests
import re
import json
import time
import datetime

from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match

url = 'http://www.nxtgame.com/?sports=1'
match_url = 'http://www.nxtgame.com/match/details/'

def crawl_match(match_id):
    time.sleep(1)
    response = requests.get(match_url + str(match_id), headers=headers)
    content = soup(response.content, 'html.parser')
    league = content.find('div', {'class': 'col-xs-6 text-left'}).p.text
    isLive = False
    isCompleted = False
    if len(content.findAll('span', {'class': 'text-right small tickers_match_details_live'})) > 0:
        isLive = True
        ticker = content.find('span', {'class': 'text-right small tickers_match_details_live'})
        match_time = datetime.datetime.strptime(ticker.get('data-date-time'), '%Y,%m,%d,%H,%M,%S')
    elif len(content.findAll('p', {'class': 'text-right small tickers_match_details'})) > 0:
        ticker = content.find('p', {'class': 'text-right small tickers_match_details'})
        match_time = datetime.datetime.strptime(ticker.get('data-date-time'), '%Y,%m,%d,%H,%M,%S')
    elif len(content.findAll('p', {'class': 'text-right small tickers_match_completed'})) > 0:
        isCompleted = True
        ticker = content.find('p', {'class': 'text-right small tickers_match_completed'})
        match_time = datetime.datetime.strptime(ticker.get('data-date-time'), '%Y,%m,%d,%H,%M,%S')

    teamA = content.find('div', {'class': 'col-xs-6 text-center col-xs-height col-top teamA'})
    teamA_tag = teamA.find('div', {'class': 'col-xs-6 text-center'})
    teamA_name = teamA_tag.p.text.strip()
    teamA_rate = float(teamA_tag.p.next_sibling.next_sibling.text.strip()[:-1]) / 100
    teamA_ID = teamA.find('input', {'class': 'teamID'}).get('value')
    teamA_rewards = float(content.find('div', {'class': 'col-xs-6 col-md-3 text-center odds-panel-teamA'}).span.text)
    
    teamB = content.find('div', {'class': 'col-xs-6 text-center col-xs-height col-top teamB'})
    teamB_tag = teamB.find('div', {'class': 'col-xs-6 text-center'})
    teamB_name = teamB_tag.p.text.strip()
    teamB_rate = float(teamB_tag.p.next_sibling.next_sibling.text.strip()[:-1]) / 100
    teamB_ID = teamB.find('input', {'class': 'teamID'}).get('value')
    teamB_rewards = float(content.find('div', {'class': 'col-xs-6 col-md-3 text-center odds-panel-teamB'}).span.text)

    try:
        bets = re.match(r'\d+', content.find('h5').text.strip()).group()
    except:
        bets = 0
    try:
        best_of = re.search(r'Best of (?P<haha>\d)', content.text).group('haha')
    except:
        best_of = 0
    return Match(
        active = isLive,
        matchtime=datetime.datetime.strftime(match_time, '%Y-%m-%d %H:%M'),
        webpage=match_url + str(match_id),
        serie=league,
        teams=(teamA_name, teamB_name),
        odds=(teamA_rate, teamB_rate),
        returns=(teamA_rewards, teamB_rewards),
        poolsize=bets,
        bestof=best_of
        )

def crawl_full():
    response = requests.get(url, headers=headers)
    content = soup(response.content, 'html.parser')
    matches = content.findAll('div', {'class': 'col-xs-12 item match-thumbnail'})
    for match in matches:
        match_id = match.a.get('id')
        yield crawl_match(match_id)

def crawl_home():
    response = requests.get(url, headers=headers)
    content = soup(response.content, 'html.parser')
    matches = content.findAll('div', {'class': 'col-xs-12 item match-thumbnail'})
    for match in matches:
        match_id = match.a.get('id')
        yield crawl_match(match_id)

def flowtest():
    print('nxt crawler flowtest')
    print('crawling http://nxtgame.com/')
    print('Result:')
    for match in crawl_full():
        print(match)

