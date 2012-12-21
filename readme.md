# ConceptNet SAT Solver


## Running

To run the solver normally, do

	./satsolver.py <question-file>

	optional arguments:
		-v, --verbose  show every question, including relationships found and score
		-p, --pickle   pickle the term map after running (to cache the queries)

where `<question-file>` is one of the `set_.txt` files, for a small run of ten questions, or `questions.txt` for the full 374-question set.

**WARNING:** Running the full question set will take a _long time_ if you don't have `termMap.pickle` in the same directory, likely somewhere between ten minutes and half an hour. However, this repo includes that cache, so it will probably take a minute or so.

The `-p` argument will cause the data fetched from ConceptNet to be written out to a file `termMap.pickle`. This file will then be loaded on every future run and used as a local cache in preference of requesting against the ConceptNet API. This will greatly speed future runs on the same test set.