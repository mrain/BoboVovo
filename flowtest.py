import sys

from crawler import __all__ as all_crawlers
from crawler import *
all_crawlers = [globals()[crawler] for crawler in all_crawlers]
s=all_crawlers[0].flowtest()
globals()[sys.argv[1]].flowtest()
