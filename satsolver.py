target = 'questions.txt'
ansmap = {'a':0,'b':1,'c':2,'d':3,'e':4}

def testSolver(target):
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
    print stem, options
    return 0

testSolver(target)
