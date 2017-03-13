#!/bin/env python
# Author: chunyang.wen@gmail.com

"""
This file is to prepare data for generating words from file.
It can generate n-gram words.
"""

import re
import os
import sys
import glob
import multiprocessing
import multiprocessing.dummy # for test

from timeutil import TimeUtil

def chainWords(gram_number, fd, words):
        """Used to chain words into gramNumber
        Args:
            gramNumber, n-gram
            fd, output file
            words, collections of words
        Return:
            return words left after generate grams
        """
        assert gram_number > 0, 'gramNumber must be greater than 0'
        size = len(words)
        for i in xrange(size - gram_number + 1):
            fd.write("\t".join(words[i:i+gram_number]))
            fd.write("\n")
        return words[-(gramNumber - 1):]


def prepareCommon(gram_number, input_file, output_dir):
    """split by non [A-Za-z0-9]+ characters"""
    words = []
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_dir, filename)
    with open(output_file, 'w') as ofd:
        with open(input_file, 'r') as ifd:
            for line in ifd:
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
                # include character repeated > 3
                words = filter(lambda word: not re.search(r'([a-z])\1{2,}', word), words)
                words = chainWords(gram_number, ofd, words)
        if words:
            ofd.write("\t".join(words))
            ofd.write("\n")

class PrepareWords(object):
    """Prepare gram file and candidate file"""
    PROCESS_LIMIT = 20

    def __init__(self, input, output_gram_dir, output_candidate_dir):

        self._input_files = []
        if os.path.isfile(input):
            assert os.path.exists(input), 'File %s not existed' % input
            self._input_files.append(input)
        else:
            input = os.path.join(input, '*') if os.path.isdir(input) else input
            for file in glob.glob(input):
                self._input_files.append(file)
        assert len(self._input_files) > 0, "No input files"

        self._output_gram_dir = output_gram_dir
        self._output_candidate_dir = output_candidate_dir
        assert os.path.exists(output_gram_dir), "Gram directory not exists"
        assert os.path.exists(output_candidate_dir), "Candidate directory not exists"
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

    def prepareGram(self, gram_number):
        """generate gram_number specified file
        Args:
            gram_number, n-gram, n = gram_number
        """
        """
        self.prepareCommon(gram_number, self._output_gram_dir)
        """
        """
        p1 = multiprocessing.Process(target=self.prepareCommon,
                args=(gram_number, self._output_gram_dir))
        p1.daemon = True
        p1.start()
        """
        for file in self._input_files:
            self._args.append((gram_number, file, self._output_gram_dir))


    def prepareCandidate(self, candidate_number):
        """generate candidate number specified file
        Args:
            candidate_number, how many words should be used to generate a candidate
        """
        """
        self.prepareCommon(candidate_number, self._output_candidate_dir)
        """
        """
        p1 = multiprocessing.Process(target=self.prepareCommon,
                args=(candidate_number, self._output_candidate_dir))
        p1.daemon = True
        p1.start()
        """
        for file in self._input_files:
            self._args.append((candidate_number, file, self._output_candidate_dir))

    def run(self):
        process_num = min(len(self._input_files), PrepareWords.PROCESS_LIMIT)
        module=multiprocessing
        pool = module.Pool(processes = process_num)
        for args in self._args:
            pool.apply_async(prepareCommon, args)
        pool.close()
        pool.join()


def test():
    gram_number = 3
    candidate_number = 2
    #inputFile = '/home/yang/work/pmi/shakespeare/t8.shakespeare.txt'
    input_dir = './data/sources/'
    output_gram_dir = './data/grams/'
    output_candidate_dir = './data/candidates/'
    prep = PrepareWords(input_dir, output_gram_dir, output_candidate_dir)
    prep.prepareGram(gram_number)
    prep.prepareCandidate(candidate_number)
    tu = TimeUtil()
    tu.reset()
    prep.run()
    tu.elapsedSeconds()


if __name__ == '__main__':
    test()
