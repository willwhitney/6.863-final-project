#! /usr/bin/env python
import random
import argparse
from collections import defaultdict
from conceptnetQuerier import *
import Queue
import threading
import time
import math

ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def threadedSolver(target, numQuestions, verbose):
    # Solves a list of n questions using n threads. Causes breakage.
    q = Queue.Queue()
    
    file = open(target).read()
    questions = file.split('\n\n')
    correctCount, total = 0.0, 0.0
    threads = []
    
    numQuestions = min(numQuestions, len(questions))
    for index, question in enumerate(questions):
        if index >= numQuestions:
            break
        t = threading.Thread(target=solveAndCheck, args=(question, q, verbose))
        t.daemon = True
        threads.append(t)
        t.start()
            
    while total < numQuestions:
        correct = q.get()
        if correct:
            correctCount += 1
        if not correct == None:
            total += 1
        dead = 0
        for thread in threads:
            if not thread.isAlive():
                dead += 1
        if dead == len(threads):
            print "Correct: " + str(correctCount)
            print "Total: " + str(total)
            return correctCount / total
            
    print "Correct: " + str(correctCount)
    print "Total: " + str(total)
    return correctCount / total
    
def solveAndCheckMultiple(questions, q, params, verbose):
    # solves and checks a list of questions.
    correct, total = 0, 0
    for question in questions:
        right = solveAndCheckBlocking(question, params, verbose)
        if right:
            correct += 1
        if right != None:
            total += 1
    q.put( (correct, total) )
    
def quadThreadedSolver(target, params, verbose):
    # Splits the problem in four, solves each set in a separate thread,
    # then aggregates results.
    q = Queue.Queue()
    
    f = open(target).read()
    questions = f.split('\n\n')
    correctCount, total = 0.0, 0.0
    threads = []
    
    for i in xrange(0, 4):
        start = int(i * math.floor(len(questions) / 4))
        end = start + len(questions) / 4
        if i == 3:
            end = len(questions) + 1
#        print "from:", start, "to: ",  end
            
        t = threading.Thread(target=solveAndCheckMultiple, args=(questions[start: end], q, params, verbose))
        t.daemon = True
        threads.append(t)
        t.start()
    
    returned = 0
    while returned < 4:
        subsetCorrect, subsetTotal = q.get()
        returned += 1
        correctCount += subsetCorrect
        total += subsetTotal
                    
#    print "Correct: " + str(correctCount)
#    print "Total: " + str(total)
    return correctCount / total
    
def biThreadedSolver(target, verbose):
    # Splits the problem in four, solves each set in a separate thread,
    # then aggregates results.
    q = Queue.Queue()

    f = open(target).read()
    questions = f.split('\n\n')
    correctCount, total = 0.0, 0.0
    threads = []

    for i in [0, len(questions) / 2]:
#        print "i: ", i
        t = threading.Thread(target=solveAndCheckMultiple, args=(questions[i: i + len(questions) / 2], q, verbose))
        t.daemon = True
        threads.append(t)
        t.start()

    returned = 0
    while returned < 2:
        subsetCorrect, subsetTotal = q.get()
        returned += 1
        correctCount += subsetCorrect
        total += subsetTotal

#    print "Correct: " + str(correctCount)
#    print "Total: " + str(total)
    return correctCount / total
        
def solveAndCheck(question, q, params, verbose):
    # for use with threadedSolver. Dumps its results in a queue.
    try:
        question = question.split('\n')
        stem, opts, ans = question[1], question[2:7], question[7]
        stem = stem.split()
        stem = (stem[0],stem[1])
        opts = [opt.split() for opt in opts]
        opts = [(opt[0],opt[1]) for opt in opts]
        guess = solve(stem, opts, params, verbose)
        if guess == ansmap[ans]:
            q.put(True)
        else:
            q.put(False)
    except:
        q.put(None)
        return

def solveAndCheckBlocking(question, params, verbose):
    # just like solveAndCheck, but blocks and returns.
    # for use with solveAndCheckMultiple.
    try:
        question = question.split('\n')
        stem, opts, ans = question[1], question[2:7], question[7]
        stem = stem.split()
        stem = (stem[0],stem[1])
        opts = [opt.split() for opt in opts]
        opts = [(opt[0],opt[1]) for opt in opts]
        guess = solve(stem, opts, params, verbose)
        if guess == ansmap[ans]:
            return True
        else:
            return False
    except Exception as e:
        print "EXCEPTION! ", e
        return None

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
    pickle_term_map()
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
                if rA == rB:
                    score += params['idMod']*params['weights'][rA]
                dirsA = [r[-1] for r in rA]
                dirsB = [r[-1] for r in rB]
                if dirsA == dirsB:
                    score += params['dirMod']
                if len(rA) == 2 and len(rB) == 2:
                    if rA[0] == rB[0] or rA[1] == rB[1]:
                        score += params['subsMod']
        # params['normMod'] is in the range [0, 1]
        normalization = (len(relsB) - 1) * params['normMod'] + 1
        score = score * normalization / len(relsB)
    return score
#    return random.randint(0,4)

def setParams(isaf,isab,same):
    params = {'existMod':0.01,   #modifier added for existing relationships
              'idMod':1.0,       #modifier added for identical relationships
              'normMod':1.0,     #modifier added for normalizing by number of relationships (1.0 is off)
              'dirMod':0.0,      #modifier added for matched directionality (0.0 if off)
              'subsMod':0.0,     #modifier added for matched subset (0.0 is off)
              'defWeight':1.0    #default weight of relations
              }
    weights = defaultdict(lambda:params['defWeight'], {(u'/r/IsAF',):isaf, (u'/r/IsAB',):isab, (u'sameLemma'):same})
    params['weights'] = weights
    return params

argparser = argparse.ArgumentParser(description="Solve SAT analogy questions.")
argparser.add_argument("questions", help="the set of questions to use")
argparser.add_argument("number", help="how many questions to answer", nargs='?', default=400, type=int)
argparser.add_argument("-v", "--verbose", help="show every question", action="store_true")
args = argparser.parse_args()

def optimizePars():
    paropts = [(float(a)/10,float(b)/10,float(c)/10) for a in xrange(0,12,5) for b in xrange(0,12,5) for c in xrange(0,12,5)] 
    results = {}
    for par in paropts:
        print par
        params = setParams(*par)
        acc = quadThreadedSolver(args.questions, params, args.verbose)
        results[par] = acc
    print results
    m = max(results,key=lambda k: results[k])
    print m
    print results[m]

optimizePars()
#params = setParams(1.0,0.0,0.2)
#print quadThreadedSolver(args.questions, params, args.verbose)
#params = setParams(1.0,0.0,0.0)
#print quadThreadedSolver(args.questions, params, args.verbose)
