#! /usr/bin/env python
import random
import argparse
from conceptnetQuerier import *

ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def testSolver(target,params,verbose):
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
        guess = solve(stem,opts,params,verbose)
        if verbose:
            print 'My guess is', opts[guess], 'the right answer is', opts[ansmap[ans]], '\n'
        total += 1
        if guess == ansmap[ans]:
            correct += 1
    return correct/total

def solve(stem,options,params,verbose=False):
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
        sim = scoreSimilarity(stemRels,optRels,params)
        scores[opt] = sim
        if verbose:
            print sim
    best = max(scores,key=lambda k: scores[k])
    guess = options.index(best)
    return guess
#    return random.randint(0,4)

def scoreSimilarity(relsA,relsB,params):
    #given two lists of relationships, scores how similar they are
    score = 0.0
    if relsA and relsB:
        score += params['existMod']
        for rA in relsA:
            for rB in relsB:
                weights = params['weights']
                if rA in weights:
                    w = weights[rA]
                else: w = params['defWeight']
                if rA == rB:
                    score += params['idMod']*w
                if params['dirMatch'] == True:
                    dirsA = [r[-1] for r in rA]
                    dirsB = [r[-1] for r in rB]
                    if dirsA == dirsB:
                        score += params['dirMod']
                if params['subsMatch'] == True:
                    if len(rA) == 2 and len(rB) == 2:
                        if rA[0] == rB[0] or rA[1] == rB[1]:
                            score += params['subsMod']*w
        if params['normB'] == True:
            score = score * len(relsB)
    return score
#    return random.randint(0,4)

argparser = argparse.ArgumentParser(description="Solve SAT analogy questions.")
argparser.add_argument("questions", help="the set of questions to use")
argparser.add_argument("-v", "--verbose", help="show every question", action="store_true")
args = argparser.parse_args()

params = {'existMod':0.01,    #modifier added for existing relationships
          'idMod':1.0,        #modifier added for identical relationships
          'normB':False,      #true for normalizing by number of relationships of option
          'dirMatch':False,   #true for matching on only directionality
          'dirMod':0.1,       #modifier added for matched directionality
          'subsMatch':False,  #true for matching subset of relationship
          'subsMod':0.5,      #modifier added for matched subset
          'defWeight':1.0,    #default weight of relations
          'weights':{(u'/r/IsAF',):0.4, (u'/r/IsAB',):0.4, (u'sameLemma'):0.3}          
          }

print testSolver(args.questions, params, args.verbose)
