import requests

def get_conceptnet_term(term):
  r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/search?startLemmas=' + term)
  json = r.json
  for i in xrange(len(r.json['edges'])):
    # json['edges'][i]['startLemmas'] = r.json['edges'][i]['startLemmas'].split()
    # json['edges'][i]['endLemmas'] = r.json['edges'][i]['endLemmas'].split()
    json['edges'][i]['startLemmas'] = [r.json['edges'][i]['startLemmas']]
    json['edges'][i]['endLemmas'] = [r.json['edges'][i]['endLemmas']]
  return json

def get_relationship(a, b):
  adata = get_conceptnet_term(a)
  bdata = get_conceptnet_term(b)
  
  aterms = {}
  for edge in adata['edges']:
    for end in edge['endLemmas']:
      aterms[end] = edge
      
  for term in aterms:
    if b == term:
      return (aterms[term]['rel'], 1)

  for edge in bdata['edges']:
    for end in edge['endLemmas']:
      if end == a:
        return (edge['rel'], 1)
      if end in aterms:
        return (edge['rel'], 2)
        
# get_relationship("house", "home")

# {"isA", "has"}

# traincepts = get_conceptnet_term("train")
# print traincepts['edges'][0]
# traincepts['edges'][0]['endLemmas']
# traincepts['edges'][0]['startLemmas']
