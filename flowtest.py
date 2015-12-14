import sys

from crawler import __all__ as all_crawlers
from crawler import *
all_crawlers = {crawler:globals()[crawler] for crawler in all_crawlers}
all_crawlers[sys.argv[1]].flowtest()
