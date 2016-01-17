import sys
import json
import itertools
import time
import socket
socket.setdefaulttimeout(60)

import networkx

from crawler import __all__ as all_crawlers
from crawler import *
from crawler.utils import tbd
call = globals()
from utils import matchfile
from utils import domain
from utils import red
from utils import lb

cooldown = {crawler:0 for crawler in all_crawlers}
cd = 95
profit = -0.1

while True:
    pool = {}
    timestamp = time.time()
    for crawler in [x for x in all_crawlers if cooldown[x] < timestamp]:
        try:
            for match in call[crawler].crawl_full():
                with matchfile(match) as fw:
                    fw.write(str(match) + '\n')
                if 0 < match.tostart < 3600 and not tbd in match.teams:
                    pool[match.webpage] = match
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            cooldown[crawler] = time.time() + cd
            print('{0} cooldowned for {1}s for exception'.format(crawler, cd))
            print(e)
            cd += 0
    with open('httpalias', 'a') as fw:
        G = networkx.Graph()
        print('{0} matches start <1h'.format(len(G)))
        for s1, s2 in itertools.combinations(pool.values(), 2):
            if domain(s1) == domain(s2) or not s1 == s2:
                continue
            G.add_edge(s1.webpage, s2.webpage)
        for idx, c in enumerate(networkx.connected_components(G)):
            fw.write(' '.join(c) + '\n')
            print('###MATCHED### {0}: '.format(idx) + ' '.join(c))
            if max([pool[w].returns[0] for w in c]) * max([pool[w].returns[1] for w in c]) < 1 + profit:
                continue
            for w in c:
                s = pool[w]
                print(red('    {0} {1} ({2}): {3} {4} {5}'.format(s.teams[0], s.teams[1], s.series, s.returns, domain(s), s.tostart)))
    #print('done one-round crawling')
    time.sleep(5)
