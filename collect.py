import sys
import json
import time
import socket
socket.setdefaulttimeout(60)

from crawler import __all__ as all_crawlers
from crawler import *
from crawler.utils import tbd
call = globals()
from utils import matchfile
from utils import domain

cooldown = {crawler:0 for crawler in all_crawlers}
cd = 95

while True:
    pool = []
    timestamp = time.time()
    for crawler in [x for x in all_crawlers if cooldown[x] < timestamp]:
        try:
            for match in call[crawler].crawl_full():
                with matchfile(match) as fw:
                    fw.write(str(match) + '\n')
                if 0 < match.tostart < 3600 and not tbd in match.teams:
                    pool.append(match)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            cooldown[crawler] = time.time() + cd
            print('{0} cooldowned for {1}s for exception'.format(crawler, cd))
            print(e)
            cd += 1.5
    with open('httpalias', 'a') as fw:
        for s1 in pool:
            print(s1)
        for i in range(len(pool)):
            s1 = pool[i]
            for j in range(i+1, len(pool)):
                s2 = pool[j]
                if not domain(s1) == domain(s2):
                    if s1.__eq__(s2):
                        fw.write('{0} {1}\n'.format(s1.webpage, s2.webpage))
                        print('###MATCHED###', s1.webpage, s2.webpage)
    print('done one-round crawling')
    time.sleep(5)
