from crawler import __all__ as all_crawlers
from crawler import *
all_crawlers = [globals()[crawler] for crawler in all_crawlers]
for s in all_crawlers[0].crawl_full():
    print(s)

