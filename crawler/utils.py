# -*- coding: utf-8 -*-

import os
import time
import json
from slugify import slugify

headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
}
tbd = 'TBD'

def pc(x):
    return float(x[:-1]) / 100

class Match(object):
    def __init__(self, active='', matchtime='1990-01-01 00:00', webpage='', series='', teams=(tbd, tbd), odds=(0, 0), returns=(0, 0), notes=None, result=(-1, -1), poolsize=-1, bestof=-1):
        self.active = active
        self.matchtime = matchtime
        self.series = slugify(series)
        teams = [slugify(team) for team in teams]
        odds = [float(odd) for odd in odds]
        returns = [float(_return) for _return in returns]
        result = [float(score) for score in result]
        if teams[0] <= teams[1]:
            self.teams = teams
            self.odds = odds
            self.returns = returns
            self.result = result
        else:
            self.teams = teams[::-1]
            self.odds = odds[::-1]
            self.returns = returns[::-1]
            self.result = result[::-1]
        self.notes = notes
        self.webpage = webpage
        self.poolsize = int(poolsize)
        self.bestof = int(bestof)
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __eq__(self, s):
        assert(isinstance(s, match))
        if abs(time.mktime(self.matchtime) - time.mktime(s.matchtime)) <= 5400 and self.series == s.series and self.team == s.team:
            return True
        else:
            return False

    def __str__(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def load(s):
        obj = match(active='', matchtime='', webpage='')
        obj.__dict__ = json.loads(s)
        return obj

def ww(d, f, m='w'):
    t = time.localtime()
    s = time.strftime('%Y-%m-%d', t)
    return open(os.path.join(d, '{0}_{1}'.format(f, s)), m)
    
def rr(d, f):
    l = os.listdir(d)
    s = [x[len(f) + 1:] for x in l if x.startswith(f)]
    t = [time.strptime(x, '%Y-%m-%d') for x in s]
    s = time.strftime('%Y-%m-%d', max(t))
    return open(os.path.join(d, '{0}_{1}'.format(f, s)))
