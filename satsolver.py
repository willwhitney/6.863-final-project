import random
from conceptnetQuerier import *

ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def testSolver(target):
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
        guess = solve(stem,opts)
        total += 1
        if guess == ansmap[ans]:
            correct += 1
    return correct/total

def solve(stem,options):
    #given a stem that's a tuple (word0,word1)
    #and a list of options in the same format
    #get the relationship between every pair of words
    #scores each option's relationship's similarity to the stem's relationship
    #returns the option index of the most similar option
    stemRels = get_relationship(*stem)
    print stem, stemRels
    scores = {}
    for opt in options:
	optRels = get_relationship(*opt)
	print opt, optRels
	sim = scoreSimilarity(stemRels,optRels)
	scores[opt] = sim
    best = max(scores,key=lambda k: scores[k])
    print 'My guess is', best, '\n'
    guess = options.index(best)
    return guess
#    return random.randint(0,4)

#def getRelationship(pair):
#    return 'isA'

def scoreSimilarity(relsA,relsB):
    #given two lists of relationships, scores how similar they are
    if not relsA or not relsB:
	return 0.0
    for rA in relsA:
	for rB in relsB:
	     if rA == rB:
		return 1.0
    return 0.5
#    return random.randint(0,4)

print testSolver('easyset.txt')
