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
import glob
import pickle
import argparse
import multiprocessing

import pygtrie
from  timeutil import TimeUtil

SEP = '\t'

def getTrieFile(file, pickle_dir):
    return os.path.join(pickle_dir, "%s-trie" % file)

def buildTrieSingle(file, pickle_dir):
    """Build trie, dumps using pickle
    """
    trie_file = getTrieFile(os.path.basename(file), pickle_dir)
    trie = pygtrie.StringTrie(separator=SEP)
    with open(file) as fd:
        for line in fd:
            key = line.strip()
            trie.setdefault(key, 0)
            trie[key] += 1
    with open(trie_file, 'w') as fd:
        pickle.dump(trie, fd, protocol = 2)


class Process(object):
    """Generate score with gram file and candidate file"""
    PROCESS_LIMIT = 20

    def __init__(self, grams, candidates, score_dir, pickle_dir):
        self._gram_files = self.detectFiles(grams)
        self._candidate_files = self.detectFiles(candidates)
        self._score_dir = score_dir
        self._pickle_dir = pickle_dir
        self._tries = []
        self._global_cache = {} # cache for keys after generating from tries
        self._total = None
        self._cache = {} # cache keys in each trie
        assert len(self._gram_files) > 0, "gram file %s not exists %s" % grams
        assert len(self._candidate_files) > 0, "candidate file %s not exists" % candidates
        print "Gram: ", self._gram_files
        print "Candidate: " , self._candidate_files

    def detectFiles(self, input):
        """find all the files
        Args:
            file, folder, file_pattern
        Return:
            list of files found
        """
        output = []
        if os.path.isfile(input):
            output.append(input)
        else:
            input = os.path.join(input, '*') if os.path.isdir(input) else input
            for file in glob.glob(input):
                output.append(file)
        return output

    def buildTrieSingle(self, file):
        """Build trie, dumps using pickle
        """
        pass

    def buildTrie(self):
        """Generate StringTrie"""
        module = multiprocessing
        process_num = min(len(self._gram_files), Process.PROCESS_LIMIT)
        pool = module.Pool(processes=process_num)
        for file in self._gram_files:
            pool.apply_async(buildTrieSingle, (file, self._pickle_dir))
        pool.close()
        pool.join()

    def lazySum(self, key):

        if key is None:
            # means total
            if self._total is None:
                self._total = 0
                for index, trie in enumerate(self._tries):
                    self._total += sum(trie.itervalues())
            return self._total

        if not self._global_cache.has_key(key):
            value = 0
            for index, trie in enumerate(self._tries):
                file_key = "%s$$$$%s" % (index, key)
                if not self._cache.has_key(file_key):
                    if trie.has_node(key):
                        self._cache[file_key] = sum(trie.itervalues(prefix=key))
                    else:
                        self._cache[file_key] = 0
                value += self._cache[file_key]
            self._global_cache[key] = value
        return self._global_cache[key]

    def loadTrie(self):
        """load trie from pickle dumped file"""
        for file in self._gram_files:
            trie_file = getTrieFile(os.path.basename(file), self._pickle_dir)
            with open(trie_file, 'rb') as fd:
                self._tries.append(pickle.load(fd))

    def generateScore(self):
        """Use trie to generate score for candidate.
        pmi(x, y) = log p(xy)/(p(x) * p(y))
        """
        totalFreq = self.lazySum(key=None)
        for file in self._candidate_files:
            filename = os.path.basename(file)
            score_file = os.path.join(self._score_dir, filename)
            with open(score_file, 'w') as ofd:
                with open(file) as ifd:
                    for line in ifd:
                        words = line.strip().split('\t')
                        if len(words) < 2 or any(map(lambda word:len(word)<2, words)):
                            continue

                        XFreq = self.lazySum(words[0])
                        YFreq = self.lazySum(words[1])
                        XYFreq = self.lazySum(line.strip())
                        # frequences filter
                        #if XYFreq < 2 or XYFreq > 24:
                        #    continue
                        if YFreq == 0 or XFreq == 0:
                            # because when generating grams, we last last words' frequency
                            continue
                        PX = XFreq * 1.0 / totalFreq
                        PY = YFreq * 1.0 / totalFreq
                        PXY = XYFreq * 1.0 / totalFreq
                        score = math.log(PXY/PX/PY, 2) * XYFreq
                        #print "Freq:", XFreq, YFreq, XYFreq
                        result = "{0}\t{1:.2f}\n".format(line.strip(), score)
                        ofd.write(result)

def test():
    grams = './data/grams/'
    candidates = './data/candidates/'
    score_dir = './data/scores/'
    pickle_dir = './data/pickles/'
    prop = Process(grams, candidates, score_dir, pickle_dir)
    tu = TimeUtil()
    tu.start()
    prop.buildTrie()
    tu.elapsedSeconds()
    tu.reset()
    prop.loadTrie()
    tu.elapsedSeconds()
    tu.reset()
    prop.generateScore()
    tu.elapsedSeconds()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', action='store_true', default=False)
    opts = parser.parse_args(sys.argv[1:])
    test()

