import requests
import re
import json
import utils
from bs4 import BeautifulSoup as soup

url = "http://www.nxtgame.com/?sports=1"
match_url = "http://www.nxtgame.com/match/details/"

def crawl_match(match_id):
    match = {"id": match_id}
    response = requests.get(match_url + str(match_id), headers = utils.headers)
    content = soup(response.content, "html.parser")
    league = content.find("div", {"class": "col-xs-6 text-left"}).p.text
    #print("League: " + league)
    match["series"] = league
    # Meta Data
    if len(content.findAll("span", {"class": "text-right small tickers_match_details_live"})) > 0:
        #print("Live!")
        ticker = content.find("span", {"class": "text-right small tickers_match_details_live"})
        match_time = ticker.get("data-date-time")
        match["time"] = match_time
        #print("Match time: " + match_time)
    elif len(content.findAll("p", {"class": "text-right small tickers_match_details"})) > 0:
        ticker = content.find("p", {"class": "text-right small tickers_match_details"})
        match_time = ticker.get("data-date-time")
        #print("Match time: " + match_time)
        match["time"] = match_time
    # Teams
    teamA = content.find("div", {"class": "col-xs-6 text-center col-xs-height col-top teamA"})
    teamA_tag = teamA.find("div", {"class": "col-xs-6 text-center"})
    teamA_name = teamA_tag.p.text.strip()
    teamA_rate = teamA_tag.p.next_sibling.next_sibling.text.strip()
    teamA_ID = teamA.find("input", {"class": "teamID"}).get("value")
    teamA_rewards = content.find("div", {"class": "col-xs-6 col-md-3 text-center odds-panel-teamA"}).span.text
    #print("TeamA: " + teamA_name + " (" + teamA_rate + "), rewards " + teamA_rewards)
    match["team"] = [teamA_name]
    match["odds"] = [teamA_rate]
    match["rewards"] = [teamA_rewards]
    teamB = content.find("div", {"class": "col-xs-6 text-center col-xs-height col-top teamB"})
    teamB_tag = teamB.find("div", {"class": "col-xs-6 text-center"})
    teamB_name = teamB_tag.p.text.strip()
    teamB_rate = teamB_tag.p.next_sibling.next_sibling.text.strip()
    teamB_ID = teamB.find("input", {"class": "teamID"}).get("value")
    teamB_rewards = content.find("div", {"class": "col-xs-6 col-md-3 text-center odds-panel-teamB"}).span.text
    #print("TeamB: " + teamB_name + " (" + teamB_rate + "), rewards " + teamB_rewards)
    match["team"].append(teamB_name)
    match["odds"].append(teamB_rate)
    match["rewards"].append(teamB_rewards)
    bets = content.find("h5").text.strip()
    #print(bets)
    match["bets"] = bets
    return match

def crawl_match_list():
    response = requests.get(url, headers=utils.headers)
    content = soup(response.content, "html.parser")
    matches = content.findAll("div", {"class": "col-xs-12 item match-thumbnail"})
    match_list = []
    for match in matches:
        match_id = match.a.get("id")
        match_list.append(match_id)
    return match_list

match_list = crawl_match_list()
for match_id in match_list:
    print("Match ID" + str(match_id))
    print(crawl_match(match_id))

