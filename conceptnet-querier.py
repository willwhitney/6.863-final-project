import requests

def get_conceptnet_term(term):
  r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/search?startLemmas=' + term)
  json = r.json
  for i in xrange(len(r.json['edges'])):
    json['edges'][i]['startLemmas'] = r.json['edges'][i]['startLemmas'].split()
    json['edges'][i]['endLemmas'] = r.json['edges'][i]['endLemmas'].split()
  return json


traincepts = get_conceptnet_term("train")
traincepts['edges'][0]['rel']
traincepts['edges'][0]['endLemmas']
traincepts['edges'][0]['startLemmas']  
