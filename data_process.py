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
from timeutil import TimeUtil

class Process(object):
    """Generate score with gram file and candidate file"""
    SEP = '\t'

    def __init__(self, gramFile, candidateFile, scoreFile):
        self._gramFile = gramFile
        self._candidateFile = candidateFile
        self._scoreFile = scoreFile
        """pre_trie"""
        self._pretrie = trie.StringTrie(separator=Process.SEP)
        self._pretrieFile = 'PreGramTrie'
        self._precache = {}
        """post_trie"""
        self._posttrie = trie.StringTrie(separator=Process.SEP)
        self._posttrieFile = 'PostGramTrie'
        self._postcache = {}
        assert os.path.exists(gramFile), "GramFile %s not exists" % gramFile
        assert os.path.exists(candidateFile), "CandidateFile %s not exists" % candidateFile

    def buildTrie(self):
        """Generate StringTrie"""
        with open(self._gramFile) as fd:
            for line in fd:
                key = line.strip()
                self._pretrie.setdefault(key, 0)
                self._pretrie[key] += 1

                #I love to embrace, prefix(love to) = {embrace,...}, postfix(love to) = {I,...}
                try:
                    #last line in gram-3 has only 2 column
                    preword, midword, postword = line.strip().split(Process.SEP)
                except:
                    continue
                key = Process.SEP.join([midword,postword,preword])
                self._posttrie.setdefault(key, 0)
                self._posttrie[key] += 1

        #with open(self._pretrieFile, 'w') as fd:
        #   pickle.dump(self._pretrie, fd)

    def lazySum(self, key):
        if not self._precache.has_key(key):
            self._precache[key] = sum(self._pretrie.itervalues(prefix=key))
        return self._precache[key]

    """
    Use trie to generate score for candidate.
    pmi(x, y) = log p(xy)/(p(x) * p(y))
    """
    def generateScore(self, file=None):

        if file:
            with open(file, 'rb') as fd:
                self._pretrie = pickle.load(fd)
        totalFreq = sum(self._pretrie.itervalues())
        with open(self._scoreFile, 'w') as outFd:
            with open(self._candidateFile) as fd:
                for line in fd:
                    words = line.strip().split('\t')
                    if len(words) < 2 or any(map(lambda word:len(word)<2, words)):
                        continue
                    try:
                        # The last word in the whole text is lost frequency
                        XFreq = self.lazySum(words[0])
                        YFreq = self.lazySum(words[1])
                    except:
                        continue
                    XYFreq = self.lazySum(line.strip())
                    # frequences filter
                    if XYFreq < 2 or XYFreq > 24:
                        continue
                    PX = XFreq * 1.0 / totalFreq
                    PY = YFreq * 1.0 / totalFreq
                    PXY = XYFreq * 1.0 / totalFreq
                    pmi = math.log(PXY/PX/PY, 2) * XYFreq
                    result = "{0}\t{1:.2f}\n".format(line.strip(), pmi)
                    outFd.write(result)
    """
    use pre_trie and post_trie to compute information entropy of left and right.
    H(x) = -sum(P(x)logP(x))
    """
    def computeEntropy(self, candidatekey):
        H_right = 0
        sumright = 0
        for item in self._pretrie.iteritems(prefix=candidatekey):
            sumright += item[1]
        for item in self._pretrie.iteritems(prefix=candidatekey):
            probility_x = 1.0*item[1]/sumright
            H_right += -probility_x*math.log(probility_x, 2)
        H_left = 0
        sumleft = 0
        for item in self._posttrie.iteritems(prefix=candidatekey):
            sumleft += item[1]
        for item in self._posttrie.iteritems(prefix=candidatekey):
            probility_x = 1.0*item[1]/sumleft
            H_left += -probility_x*math.log(probility_x, 2)
        print "\t".join(map(str, [H_right, sumright]))
        print "\t".join(map(str, [H_left, sumleft]))

def test():
    gramNumber = 3
    candidateNumber = 2
    gramFile = r'C:\Users\yafe\Downloads\%s-gram.txt' % str(gramNumber)
    candidateFile = r'C:\Users\yafe\Downloads\%s-candidate.txt' % str(candidateNumber)
    scoreFile = r'C:\Users\yafe\Downloads\%s-score.txt' % str(candidateNumber)
    prop = Process(gramFile, candidateFile, scoreFile)
    tu = TimeUtil()
    tu.start()
    prop.buildTrie()
    tu.elapsedSeconds()
    tu.reset()
    key1 = 'acronyms\tand\tterms'
    key2 = 'not\tplaced\tin'
    print prop._pretrie.has_key(key1)
    print prop._pretrie.has_key(key2)
    tu.elapsedSeconds()
    tu.reset()
    print sum(prop._pretrie.itervalues(prefix='additional'))
    tu.elapsedSeconds()
    tu.reset()
    prop.generateScore()
    tu.elapsedSeconds()

def test1():
    gramNumber = 3
    candidateNumber = 2
    gramFile = r'C:\Users\yafe\Downloads\%s-gram.txt' % str(gramNumber)
    candidateFile = r'C:\Users\yafe\Downloads\%s-candidate.txt' % str(candidateNumber)
    scoreFile = r'C:\Users\yafe\Downloads\%s-score.txt' % str(candidateNumber)
    prop = Process(gramFile, candidateFile, scoreFile)
    tu = TimeUtil()
    tu.start()
    prop.generateScore('GramTrie')
    tu.elapsedSeconds()

def test_pre_post_trie():
    gramNumber = 3
    candidateNumber = 2
    gramFile = r'C:\Users\yafe\Downloads\%s-gram.txt' % str(gramNumber)
    candidateFile = r'C:\Users\yafe\Downloads\%s-candidate.txt' % str(candidateNumber)
    scoreFile = r'C:\Users\yafe\Downloads\%s-score.txt' % str(candidateNumber)
    prop = Process(gramFile, candidateFile, scoreFile)
    prop.buildTrie()
    print "pre_trie------------"
    for item in prop._pretrie.iteritems(prefix="information\ttheory"):
        print item
    print "post_trie-----------"
    for item in prop._posttrie.iteritems(prefix="information\ttheory"):
        print item
    #prop.generateScore()
    prop.computeEntropy("information\ttheory")

if __name__ == '__main__':
    test_pre_post_trie()

