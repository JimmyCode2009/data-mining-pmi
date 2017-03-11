#!/bin/env python
# Author: chunyang.wen@gmail.com

"""
This file is to prepare data for generating words from file.
It can generate n-gram words.
"""

import re
import os
import sys
import multiprocessing

def ChainWords(gramNumber, fd, words):
        """Used to chain words into gramNumber
        Args:
            gramNumber, n-gram
            fd, output file
            words, collections of words
        Return:
            return words left after generate grams
        """
        assert gramNumber > 0, 'gramNumber must be greater than 0'
        size = len(words)
        for i in xrange(size - gramNumber + 1):
            fd.write("\t".join(words[i:i+gramNumber]))
            fd.write("\n")
        return words[-(gramNumber - 1):]


def PrepareCommon(gramNumber, inputFile, outputFile):
    """split by non [A-Za-z0-9]+ characters"""
    words = []
    with open(outputFile, 'w') as outFd:
        with open(inputFile, 'r') as inFd:
            for line in inFd:
                words.extend(re.split(r'[^0-9A-Za-z]+', line.strip()))
                words = map(lambda word:word.lower(), words)
                # empty or single character
                words = filter(lambda word:len(word) > 1, words)
                # pure number
                words = filter(lambda word:not re.match(r'^[0-9]+$', word), words)
                # number & a-z combination
                words = filter(lambda word:not re.search(r'.*([0-9][a-z])|([a-z][0-9]).*', word), words)
                # single repeated character
                words = filter(lambda word: not re.match(r'^([a-z])\1*$', word), words)
                words = ChainWords(gramNumber, outFd, words)
        if words:
            outFd.write("\t".join(words))
            outFd.write("\n")

class PrepareWords(object):
    """Prepare gram file and candidate file"""

    def __init__(self, inputFile, outputGramFile, outputCandidateFile):
        self._inputFile = inputFile
        assert os.path.exists(self._inputFile), 'File %s not existed' % self._inputFile
        self._outputGramFile = outputGramFile
        self._outputCandidateFile = outputCandidateFile
        self._args = []

    def chainWords(self, gramNumber, fd, words):
        """Used to chain words into gramNumber
        Args:
            gramNumber, n-gram
            fd, output file
            words, collections of words
        Return:
            return words left after generate grams
        """
        assert gramNumber > 0, 'gramNumber must be greater than 0'
        size = len(words)
        for i in xrange(size - gramNumber + 1):
            fd.write("\t".join(words[i:i+gramNumber]))
            fd.write("\n")
        return words[-(gramNumber - 1):]

    def prepareCommon(gramNumber, inputFile, outputFile):
        """split by non [A-Za-z0-9]+ characters"""
        print "Start preparing: %s" % str(gramNumber)
        words = []
        with open(outputFile, 'w') as outFd:
            with open(inputFile) as inFd:
                for line in inFd:
                    words.extend(re.split(r'[^0-9A-Za-z]+', line.strip()))
                    words = map(lambda word:word.lower(), words)
                    # empty or single character
                    words = filter(lambda word:len(word) > 1, words)
                    # pure number
                    words = filter(lambda word:not re.match(r'^[0-9]+$', word), words)
                    # number & a-z combination
                    words = filter(lambda word:not re.search(r'.*([0-9][a-z])|([a-z][0-9]).*', word), words)
                    # single repeated character
                    words = filter(lambda word: not re.match(r'^([a-z])\1*$', word), words)
                    words = self.chainWords(gramNumber, outFd, words)
            if words:
                outFd.write("\t".join(words))
                outFd.write("\n")
        print "End preparing: %s" % str(gramNumber)

    def prepareGram(self, gramNumber):
        """generate gramNumber specified file
        Args:
            gramNumber, n-gram, n = gramNumber
        """
        """
        self.prepareCommon(gramNumber, self._outputGramFile)
        """
        """
        p1 = multiprocessing.Process(target=self.prepareCommon,
                args=(gramNumber, self._outputGramFile))
        p1.daemon = True
        p1.start()
        """
        self._args.append((gramNumber, self._inputFile, self._outputGramFile))


    def prepareCandidate(self, candidateNumber):
        """generate candidate number specified file
        Args:
            candidateNumber, how many words should be used to generate a candidate
        """
        """
        self.prepareCommon(candidateNumber, self._outputCandidateFile)
        """
        """
        p1 = multiprocessing.Process(target=self.prepareCommon,
                args=(candidateNumber, self._outputCandidateFile))
        p1.daemon = True
        p1.start()
        """
        self._args.append((candidateNumber, self._inputFile, self._outputCandidateFile))

    def run(self):
        pool = multiprocessing.Pool(processes = 3)
        for args in self._args:
            print args
            pool.apply_async(PrepareCommon, args)
        pool.close()
        pool.join()


def test():
    gramNumber = 3
    candidateNumber = 2
    #inputFile = '/home/yang/work/pmi/shakespeare/t8.shakespeare.txt'
    inputFile = './data/total.txt'
    outputGramFile = './data/%s-gram.txt' % str(gramNumber)
    outputCandidateFile = './data/%s-candidate.txt' % str(candidateNumber)
    prep = PrepareWords(inputFile, outputGramFile, outputCandidateFile)
    prep.prepareGram(gramNumber)
    prep.prepareCandidate(candidateNumber)
    prep.run()


if __name__ == '__main__':
    test()
