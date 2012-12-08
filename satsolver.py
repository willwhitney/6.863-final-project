import random

target = 'questions.txt'
ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def testSolver(target):
    #given a target question file, read the questions and makes guesses
    #returns the percentage of the questions answered correctly
    file = open(target).read()
    questions = file.split('\r\n\r\n')
    correct, total = 0.0,0.0
    for q in questions:
	q = q.split('\r\n')
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
    stemR = getRelationship(stem)
    scores = {}
    for opt in options:
	optR = getRelationship(opt)
	sim = scoreSimilarity(stemR,optR)
	scores[opt] = sim
    best = max(scores,key=lambda k: scores[k])
    print stem, best
    guess = options.index(best)
    return guess
#    return random.randint(0,4)

def getRelationship(pair):
    return ['isA']

def scoreSimilarity(rel0,rel1):
    #given two relationships, scores how similar they are
    if rel0 == rel1:
	return 1.0
    elif rel0 and rel1:
	return 0.5
    else:
	return 0.0
#    return random.randint(0,4)

print testSolver(target)
