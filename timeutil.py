#!/bin/env python

# A time util to measure time elapsed.

import datetime


class TimeUtil(object):
    """
    A unit to easily measure elasped time
    """
    def __init__(self):
        super(TimeUtil, self).__init__()

    def start(self):
        self._time = datetime.datetime.now()

    def elapsed(self):
        self._now = datetime.datetime.now()
        self._delta = self._now - self._time
        return self._delta

    def elapsedSeconds(self):
        self.elapsed()
        print "Seconds elapsed: ", self._delta.seconds

    def elapsedMicroseconds(self):
        self.elapsed()
        print "Microseconds elapsed: ", self._delta.microseconds

    def reset(self):
        self.start()


def test():
    tu = TimeUtil()
    tu.start()
    k = 0
    for i in range(1, 10000000):
        k += i
    print i
    print "Seconds: ", tu.elapsed().seconds
    tu.elapsedSeconds()
    tu.elapsedMicroseconds()



if __name__ == '__main__':
    test()
