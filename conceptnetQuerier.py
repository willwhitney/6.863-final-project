import requests

def get_conceptnet_term(term):
  r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/c/en/' + term)
  if r.json['numFound'] == 0:
    r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/search?startLemmas=' + term)
  json = r.json
  return json

# build up and returns a dict of words A is connected to directly
def build_term_list(a, adata):
  aterms = {}
  for edge in adata['edges']:
    if is_useful_relationship(edge['rel']):
      if edge['endLemmas'] == a:
        aterms[edge['startLemmas']] = edge
      else:
        aterms[edge['endLemmas']] = edge
  return aterms

def is_useful_relationship(relationship):
  if relationship == u'/r/TranslationOf':
    return False
  return True
  
def search_indirect_oneway(a, aterms, adata, b, bterms, bdata, matches):
  # check if A is connected to B by a single word contained in one of A's connections
  for termA in aterms:
    words = termA.split()
    if len(words) > 1:
      for subtermA in words:
        
        # check if one of those single words is B
        if subtermA == b:
          matches.append( {'rels': (aterms[termA]['rel'],), 'degree': 1, 'edges': aterms[termA]} )
          
        #check if B is connected to one of those single words
        for termB in bterms:
          if subtermA == termB:
            matches.append( {'rels': (aterms[termA]['rel'], bterms[termB]['rel']), 'degree': 2, 'edges': [aterms[termA], bterms[termB]]} )


def get_relationship(a, b):
  adata = get_conceptnet_term(a)
  bdata = get_conceptnet_term(b)
  matches = []
  
  # build up a list of words A and B are connected to directly
  aterms = build_term_list(a, adata)
  bterms = build_term_list(b, bdata)
        
  # check if B is a word A is connected to directly
  for term in aterms:
    if term == b:
      matches.append( {'rels': (aterms[term]['rel'],), 'degree': 1, 'edges': aterms[b]} )
      
  # check if A is a word B is connected to directly
  for term in bterms:
    if term == a:
      matches.append( {'rels': (bterms[term]['rel'],), 'degree': 1, 'edges': bterms[a]} )
      
  # check if A and B are connected via an intermediate term
  for termA in aterms:
    for termB in bterms:
      if termA == termB:
        matches.append( {'rels': (aterms[termA]['rel'], bterms[termB]['rel']), 'degree': 2, 'edges': [aterms[termA], bterms[termB]]} )
        
  # check if A and B are connected indirectly
  search_indirect_oneway(a, aterms, adata, b, bterms, bdata, matches)
  search_indirect_oneway(b, bterms, bdata, a, aterms, adata, matches)
  
  relationships = [match['rels'] for match in matches]
  return relationships
  
# print get_relationship("coop", "poultry")

# {"isA", "has"}

# traincepts = get_conceptnet_term("train")
# print traincepts['edges'][0]
# traincepts['edges'][0]['endLemmas']
# traincepts['edges'][0]['startLemmas']







