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
    correct = []
    incorrect = []
    answerHadInfoList = []
    results = []
    for question in questions:
        # right, stemAssnCount, choicesWithInfo, answerHadInfo = solveAndCheckBlocking(question, params, verbose)
        # answerHadInfoList.append(answerHadInfo)
        # if right:
        #     correct.append((stemAssnCount, choicesWithInfo))
        # elif right == False:
        #     incorrect.append((stemAssnCount, choicesWithInfo))
        results.append(solveAndCheckBlocking(question, params, verbose))
    q.put( results )
    
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
            
        t = threading.Thread(target=solveAndCheckMultiple, args=(questions[start: end], q, params, verbose))
        t.daemon = True
        threads.append(t)
        t.start()
    
    returned = 0
    correctList = []
    incorrectList = []
    answerHadInfoList = []
    results = []
    while returned < 4:
        # subsetCorrect, subsetIncorrect, answerHadInfoSubset = q.get()
        # correctList = correctList + subsetCorrect
        # incorrectList = incorrectList + subsetIncorrect
        # answerHadInfoList
        returned += 1
        # correctCount += len(subsetCorrect)
        # total += len(subsetIncorrect) + len(subsetCorrect)
        results = results + q.get()
    # print "Correct"
    # for pair in correctList:
    #     print pair[0], ',', pair[1]
    # print "Incorrect"
    # for pair in incorrectList:
    #     print pair[0], ',', pair[1]
#    print "Correct: " + str(correctCount)
#    print "Total: " + str(total)
    for result in results:
        if result[0]:
            correctList.append(result)
        else:
            incorrectList.append(result)
        print result
    return float(len(correctList)) / ( len(correctList) + len(incorrectList))
    
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
        guess, stemAssnCount, choicesWithInfoCount, choicesWithInfo = solve(stem, opts, params, verbose)
        # print "ans:", ans
        # print "choicesWithInfo:", choicesWithInfo
        answerHadInfo = opts[ansmap[ans]] in choicesWithInfo
        # print "answerHadInfo:", answerHadInfo
        # print opts[ansmap[ans]]
        # print ans
        if guess == ansmap[ans]:
            return (True, stemAssnCount, choicesWithInfoCount, answerHadInfo)
        else:
            return (False, stemAssnCount, choicesWithInfoCount, answerHadInfo)
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
    # pickle_term_map()
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
    # print scores
    
    stemAssnCount = len(stemRels)
    # print 'stemAssnCount:', stemAssnCount
    optionsWithInfo = []
    for key in scores:
        if scores[key] > 0:
            optionsWithInfo.append(key)
    # print 'optionsWithInfo:', optionsWithInfo
    return (guess, stemAssnCount, len(optionsWithInfo), optionsWithInfo)

def scoreSimilarity(relsA,relsB,params):
    #given two lists of relationships, scores how similar they are
    score = 0.0
    if relsA and relsB:

        #existing relationships modifer
        score += params['existMod']

        for rA in relsA:
            for rB in relsB:

                #identical relationships modifier
                if rA == rB:
#                    print 'weight', rA, params['weights'][rA]
                    score += params['idMod']*params['weights'][rA]
#                    print 'matched', rA
                    break

                #directionality frame modifier
                dirsA = [r[-1] for r in rA]
                dirsB = [r[-1] for r in rB]
                if dirsA == dirsB:
                    score += params['dirMod']

                #subsets modifiers
                if len(rA) == 2 and len(rB) == 2:
                    if rA[0] == rB[0] or rA[1] == rB[1]:
                        score += params['subsMod']
                elif len(rA) == 2 and len(rB) == 1:
                    if rA[0] == rB[0] or rA[1] == rB[0]:
                        score += params['subsMod']
                elif len(rA) == 1 and len(rB) == 2:
                    if rB[0] == rA[0] and rB[1] == rA[0]:
                        score += params['subsMod']

        #normalization by length of relsB
        normalization = (len(relsB) - 1) * params['normMod'] + 1
        score = score * normalization / len(relsB)

    return score

def setParams():
    params = {'existMod':0.01,   #modifier added for existing relationships
              'idMod':1.0,       #modifier added for identical relationships
              'normMod':1.0,     #modifier added for normalizing by number of relationships (1.0 is off)
              'dirMod':0.0,      #modifier added for matched directionality (0.0 if off)
              'subsMod':0.0,     #modifier added for matched subset (0.0 is off)
              'defWeight':1.0    #default weight of relations
              }
    weights = defaultdict(lambda:params['defWeight'], {(u'/r/IsAF',):0.2, (u'/r/IsAB',):0.2, ('sameLemma',):0.1})
    params['weights'] = weights
    return params

argparser = argparse.ArgumentParser(description="Solve SAT analogy questions.")
argparser.add_argument("questions", help="the set of questions to use")
argparser.add_argument("number", help="how many questions to answer", nargs='?', default=400, type=int)
argparser.add_argument("-v", "--verbose", help="show every question", action="store_true")
args = argparser.parse_args()

def optimizePars():
#    paropts = [(float(a)/10,float(b)/10,float(c)/10) for a in xrange(0,12,5) for b in xrange(0,12,5) for c in xrange(0,12,5)]
#    paropts = [(a,b,c) for a in [0.0,0.5,1.0] for b in [0.0,0.5,1.0] for c in [0.0,0.5,1.0]]
    paropts = [0.1,0.12,0.14,0.16,0.18,0.2,0.22,0.24,0.26,0.28,0.3]
    results = {}
    for par in paropts:
        print par
        params = setParams(par)
        acc = quadThreadedSolver(args.questions, params, args.verbose)
        results[par] = acc
    print results
    m = max(results,key=lambda k: results[k])
    print m
    print results[m]

#optimizePars()
params = setParams()
print quadThreadedSolver(args.questions, params, args.verbose)
#print testSolver(args.questions, params, args.verbose)
