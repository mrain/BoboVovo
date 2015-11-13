from crawler import __all__ as all_crawlers
from crawler import *
all_crawlers = [globals()[crawler] for crawler in all_crawlers]
all_crawlers[0].flowtest()

