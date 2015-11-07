# -*- coding: utf-8 -*-

import os
import time
import json
from slugify import slugify

headers = {
'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
}
tbd = 'TBD'

class Match(object):
    def __init__(self, active='', matchtime='1990-01-01 00:00', webpage='', serie='', teams=(tbd, tbd), odds=(0, 0), returns=(0, 0), notes=None, winner=''):
        self.active = active
        self.matchtime = matchtime
        self.serie = slugify(serie)
        teams = [slugify(team) for team in teams]
        if teams[0] <= teams[1]:
            self.teams = teams
            self.odds = odds
            self.returns = returns
        else:
            self.teams = teams[::-1]
            self.odds = odds[::-1]
            self.returns = returns[::-1]
        self.notes = notes
        self.webpage = webpage

    def indentical(self, s):
        assert(isinstance(s, match))
        if abs(time.mktime(self.matchtime) - time.mktime(s.matchtime)) <= 5400 and self.serie == s.serie and self.team == s.team:
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
