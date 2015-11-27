import requests
import re
import json
import time
import datetime

from bs4 import BeautifulSoup as soup

from .utils import headers
from .utils import Match
from .utils import pc

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
    else:
        return None
    teamA = content.find('div', {'class': 'col-xs-6 text-center col-xs-height col-top teamA'})
    teamA_tag = teamA.find('div', {'class': 'col-xs-6 text-center'})
    teamA_name = teamA_tag.p.text.strip()
    teamA_rate = pc(teamA_tag.p.next_sibling.next_sibling.text.strip())
    teamA_ID = teamA.find('input', {'class': 'teamID'}).get('value')
    teamA_rewards = content.find('div', {'class': 'col-xs-6 col-md-3 text-center odds-panel-teamA'}).span.text
    
    teamB = content.find('div', {'class': 'col-xs-6 text-center col-xs-height col-top teamB'})
    teamB_tag = teamB.find('div', {'class': 'col-xs-6 text-center'})
    teamB_name = teamB_tag.p.text.strip()
    teamB_rate = pc(teamB_tag.p.next_sibling.next_sibling.text.strip())
    teamB_ID = teamB.find('input', {'class': 'teamID'}).get('value')
    teamB_rewards = content.find('div', {'class': 'col-xs-6 col-md-3 text-center odds-panel-teamB'}).span.text
    
    try:
        bets = re.match(r'\d+', content.find('h5').text.strip()).group()
    except:
        bets = 0
    try:
        best_of = re.search(r'Best of (?P<bo>\d)', content.text).group('bo')
    except:
        best_of = 0
    return Match(
        active = not isLive,
        matchtime=datetime.datetime.strftime(match_time, '%Y-%m-%d %H:%M'),
        webpage=match_url + str(match_id),
        series=league,
        teams=(teamA_name, teamB_name),
        odds=(teamA_rate, teamB_rate),
        returns=(float(teamA_rewards) + 1.0, float(teamB_rewards) + 1.0),
        poolsize=bets,
        bestof=best_of,
        tostart=(match_time - datetime.datetime.now()).total_seconds(),
        )

def crawl_full():
    response = requests.get(url, headers=headers)
    content = soup(response.content, 'html.parser')
    matches = content.findAll('div', {'class': 'col-xs-12 item match-thumbnail'})
    for match in matches:
        match_id = match.a.get('id')
        s = crawl_match(match_id)
        if s:
            yield s

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

