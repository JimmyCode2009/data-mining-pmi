#!/bin/env python
# Author: chunyang.wen@gmail.com

"""
This file is to generate trie data by fed data of n-gram.
In each node, it stores data of the frequency.
E.g.
trie['hello world'] = 1
trie['hello earth'] = 1

frequency of 'hello' = 2, but frequency of 'world' and 'earth' is 0. Since we use n-gram to feed
the tree, we will lost only the last two words' frequence.

'I love to embrace challenge'
3-gram: I love to, love to embrace, to embrace challenge, embrace challenge
frequency: 'I' = 1, 'love' = 1, 'to' = 1, 'embrace' = 1, we lost frequency of 'challenge'.
"""

import os
import sys
import math
import pickle
import argparse

import pygtrie as trie
from  timeutil import TimeUtil

class Process(object):
    """Generate score with gram file and candidate file"""
    SEP = '\t'

    def __init__(self, gramFile, candidateFile, scoreFile):
        self._gramFile = gramFile
        self._candidateFile = candidateFile
        self._scoreFile = scoreFile
        self._trie = trie.StringTrie(separator=Process.SEP)
        self._trieFile = 'GramTrie'
        self._cache = {}
        assert os.path.exists(gramFile), "GramFile %s not exists" % gramFile
        assert os.path.exists(candidateFile), "CandidateFile %s not exists" % candidateFile

    def buildTrie(self):
        """Generate StringTrie"""
        Count = 0
        with open(self._gramFile) as fd:
            for line in fd:
                key = line.strip()
                self._trie.setdefault(key, 0)
                self._trie[key] += 1
                Count += 1
                if Count % 100000 == 0:
                    print "Count: ", Count
        #with open(self._trieFile, 'w') as fd:
        #    pickle.dump(self._trie, fd)

    def lazySum(self, key):
        if not self._cache.has_key(key):
            self._cache[key] = sum(self._trie.itervalues(prefix=key))
        return self._cache[key]

    def generateScore(self, file=None):
        """Use trie to generate score for candidate.
        pmi(x, y) = log p(xy)/(p(x) * p(y))
        """
        if file:
            with open(file, 'rb') as fd:
                self._trie = pickle.load(fd)
        totalFreq = sum(self._trie.itervalues())
        with open(self._scoreFile, 'w') as outFd:
            with open(self._candidateFile) as fd:
                for line in fd:
                    words = line.strip().split('\t')
                    if len(words) < 2 or any(map(lambda word:len(word)<2, words)):
                        continue

                    XFreq = self.lazySum(words[0])
                    YFreq = self.lazySum(words[1])
                    XYFreq = self.lazySum(line.strip())
                    # frequences filter
                    if XYFreq < 2 or XYFreq > 24:
                        continue
                    PX = XFreq * 1.0 / totalFreq
                    PY = YFreq * 1.0 / totalFreq
                    PXY = XYFreq * 1.0 / totalFreq
                    score = math.log(PXY/PX/PY, 2) * XYFreq
                    #print "Freq:", XFreq, YFreq, XYFreq
                    result = "{0}\t{1:.2f}\n".format(line.strip(), score)
                    outFd.write(result)

def test():
    gramNumber = 3
    candidateNumber = 2
    gramFile = './data/%s-gram.txt' % str(gramNumber)
    candidateFile = './data/%s-candidate.txt' % str(candidateNumber)
    scoreFile = './data/%s-score.txt' % str(candidateNumber)
    prop = Process(gramFile, candidateFile, scoreFile)
    tu = TimeUtil()
    tu.start()
    prop.buildTrie()
    tu.elapsedSeconds()
    tu.reset()
    key1 = 'the\tfuture\tand'
    key2 = 'not\tplaced\tin'
    print prop._trie.has_key(key1)
    print prop._trie.has_key(key2)
    tu.elapsedSeconds()
    tu.reset()
    print sum(prop._trie.itervalues(prefix='your'))
    tu.elapsedSeconds()
    tu.reset()
    prop.generateScore()
    tu.elapsedSeconds()

def test1():
    gramNumber = 3
    candidateNumber = 2
    gramFile = './data/%s-gram.txt' % str(gramNumber)
    candidateFile = './data/%s-candidate.txt' % str(candidateNumber)
    scoreFile = './data/%s-score.txt' % str(candidateNumber)
    prop = Process(gramFile, candidateFile, scoreFile)
    tu = TimeUtil()
    tu.start()
    prop.generateScore('GramTrie')
    tu.elapsedSeconds()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', action='store_true', default=False)
    opts = parser.parse_args(sys.argv[1:])
    if opts.u:
        test1()
    else:
        test()

