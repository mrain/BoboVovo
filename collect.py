import sys
import json
import time

from crawler import __all__ as all_crawlers
from crawler import *
call = globals()
from utils import matchfile

cooldown = {crawler:0 for crawler in all_crawlers}
cd = 360
    
while True:
    print('starting crawling all sites')
    pool = []
    timestamp = time.time()
    for crawler in [x for x in all_crawlers if cooldown[x] < timestamp]:
        try:
            for match in call[crawler].crawl_full():
                with matchfile(match) as fw:
                    print(match.webpage)
                    fw.write(str(match) + '\n')
                if 0 < match.tostart < 3700:
                    pool.append(match)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            cooldown[crawler] = time.time() + cd
            print('{0} cooldowned for {1} seconds for exception')
    time.sleep(5)
