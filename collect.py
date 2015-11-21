from itertools import chain
import json

from crawler import __all__ as all_crawlers
from crawler import *
all_crawlers = [globals()[crawler] for crawler in all_crawlers]

inactive = json.load(open('inactive.log'))

with open('match.log', 'a') as fw:
    for match in chain(*[crawler.crawl_full() for crawler in all_crawlers]):
        print(match)
        fw.write(match.__str__() + '\n')
