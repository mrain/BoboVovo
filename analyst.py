import os
import time
import json

from crawler.utils import Match
from utils import matchurl

def stable_active_indicator():
    for f in os.listdir('matches'):
        active = True
        for line in open('matches/{0}'.format(f)):
            s = Match.loads(line)
            if s.active is False:
                active = False
            if active is False and s.active is True:
                print(matchurl(f), s.timestamp)
                break

def stable_poolsize():
    for f in os.listdir('matches'):
        (poolsize, tcap) = 0, 0
        for line in open('matches/{0}'.format(f)):
            s = Match.loads(line)
            if s.poolsize > poolsize:
                poolsize, tcap = s.poolsize, s.tostart
        if s.tostart <= 0:
            print(matchurl(f), tcap)
    

#with open('httpalias') as fp:
    
