# time_profiler.py
# Bencmark context manager found at:
# http://dabeaz.blogspot.fr/2010/02/context-manager-for-timing-benchmarks.html

import time
import logging


class benchmark(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, ty, val, tb):
        end = time.time()
        logging.info("%s : %0.3f seconds" % (self.name, end - self.start))
        return False
