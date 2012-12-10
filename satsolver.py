#! /usr/bin/env python
import random
import argparse
from conceptnetQuerier import *

ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def testSolver(target, verbose):
    #given a target question file, read the questions and makes guesses
    #returns the percentage of the questions answered correctly
    file = open(target).read()
    questions = file.split('\n\n')
    correct, total = 0.0,0.0
    for q in questions:
        q = q.split('\n')
        stem, opts, ans = q[1], q[2:7], q[7]
        stem = stem.split()
        stem = (stem[0],stem[1])
        opts = [opt.split() for opt in opts]
        opts = [(opt[0],opt[1]) for opt in opts]
        guess = solve(stem,opts, verbose)
        total += 1
        if guess == ansmap[ans]:
            correct += 1
    return correct/total

def solve(stem,options, verbose = False):
    #given a stem that's a tuple (word0,word1)
    #and a list of options in the same format
    #get the relationship between every pair of words
    #scores each option's relationship's similarity to the stem's relationship
    #returns the option index of the most similar option
    stemRels = get_relationship(*stem)
    if verbose:
        print stem, stemRels
    scores = {}
    for opt in options:
        optRels = get_relationship(*opt)
        if verbose:
            print opt, optRels
        sim = scoreSimilarity(stemRels,optRels)
        print sim
        scores[opt] = sim
    best = max(scores,key=lambda k: scores[k])
    if verbose:
        print 'My guess is', best, '\n'
    guess = options.index(best)
    return guess
#    return random.randint(0,4)

def scoreSimilarity(relsA,relsB):
    #given two lists of relationships, scores how similar they are
    score = 0.0
    weights = {(u'/r/IsAF',):0.4, (u'/r/IsAB',):0.4, (u'sameLemma'):0.1}
    if relsA and relsB:
        score += 0.01
        for rA in relsA:
            for rB in relsB:
#                print rA,rB
                if rA in weights:
                    w = weights[rA]
                else: w = 1.0
                if rA == rB:
                    score += 1.0*w
#                    print 'equality!',rA,'w',w,'score',score
#                elif len(rA) == 2 and len(rB) == 2:
#                    if rA[0] == rB[0] or rA[1] == rB[1]:
#                        score += 1.0*w
        score = score / (1.2*len(relsB))
    return score
#    return random.randint(0,4)

argparser = argparse.ArgumentParser(description="Solve SAT analogy questions.")
argparser.add_argument("questions", help="the set of questions to use")
argparser.add_argument("-v", "--verbose", help="show every question", action="store_true")
args = argparser.parse_args()

print testSolver(args.questions, args.verbose)
