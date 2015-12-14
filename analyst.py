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
        a = []
        ps = 0
        idx1 = 0
        for idx, line in enumerate(open('matches/{0}'.format(f))):
            s = Match.loads(line)
            a.append(s.active)
            if s.poolsize > ps:
                ps = s.poolsize
                idx1 = idx
        cnt = 0
        for idx in range(len(a)-1, -1, -1):
            cnt = (a[idx] is True) * (cnt + 1)
            if cnt == 3:
                break
        idx2 = idx + 3
        if idx1 > idx2:
            print(matchurl(f), idx1, idx2)
    
stable_poolsize()
#with open('httpalias') as fp:
    
