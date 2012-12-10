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
  
def is_useful_relationship(relationship):
  if relationship == u'/r/TranslationOf':
    return False
  return True

def get_relationship(a, b):
  adata = get_conceptnet_term(a)
  bdata = get_conceptnet_term(b)
  
  matches = []
  aterms = {}
  
  # build up a list of words A is connected to
  for edge in adata['edges']:
    if is_useful_relationship(edge['rel']):
      for end in edge['endLemmas']:
        aterms[end] = edge
      
  # see if B is one of those words A is connected to
  for term in aterms:
    if b == term:
      matches.append( {'rels': (aterms[term]['rel'],), 'degree': 1, 'edges': aterms[b]} )
    for subterm in term.split():
      if b == subterm:
        matches.append( {'rels': (aterms[term]['rel'],), 'degree': 1, 'edges': aterms[term]} )

  bterms = {}
  # check each word B is connected to and see if A is also connected to it
  for edge in bdata['edges']:
    if is_useful_relationship(edge['rel']):
      for end in edge['endLemmas']:
        bterms[end] = edge
        if end in aterms:
          matches.append( {'rels': (aterms[end]['rel'], edge['rel']), 'degree': 2, 'edges': [edge, aterms[end]]} )
        
  # see if A is one of those words B is connected to
  for term in bterms:
    if a == term:
      matches.append( {'rels': (bterms[term]['rel'],), 'degree': 1, 'edges': bterms[a]} )
      for subterm in term.split():
        if a == subterm:
          matches.append( {'rels': (bterms[term]['rel'],), 'degree': 1, 'edges': bterms[term]} )
    
  
  relationships = [match['rels'] for match in matches]
  return relationships
  
# print get_relationship("ewe", "sheep")

# {"isA", "has"}

# traincepts = get_conceptnet_term("train")
# print traincepts['edges'][0]
# traincepts['edges'][0]['endLemmas']
# traincepts['edges'][0]['startLemmas']
