import requests

def get_conceptnet_term(term, force_search = False):
  r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/c/en/' + term)
  if force_search or r.json['numFound'] == 0:
    r = requests.get('http://conceptnet5.media.mit.edu/data/5.1/search?startLemmas=' + term)
  json = r.json
  return json

# build up and returns a dict of words A is connected to directly
def build_term_list(a, adata, forward = True):
  aterms = {}
  for edge in adata['edges']:
    if is_useful_relationship(edge['rel']):
      
      # A is the end of this edge
      if edge['endLemmas'] == a:
        aterms[edge['startLemmas']] = edge
        if forward:
          edge['rel'] = edge['rel'] + 'backward'
        else:
          edge['rel'] = edge['rel'] + 'forward'
          
      # A is the start of this edge
      else:
        aterms[edge['endLemmas']] = edge
        if forward:
          edge['rel'] = edge['rel'] + 'forward'
        else:
          edge['rel'] = edge['rel'] + 'backward'
  return aterms

def is_useful_relationship(relationship):
  if relationship == u'/r/TranslationOf':
    return False
  return True
  
def search_indirect_oneway(a, aterms, adata, b, bterms, bdata, matches, a_first = True):
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
            if a_first:
              matches.append( {'rels': (aterms[termA]['rel'], bterms[termB]['rel']), 'degree': 2, 'edges': [aterms[termA], bterms[termB]]} )
            else:
              matches.append( {'rels': (bterms[termB]['rel'], aterms[termA]['rel']), 'degree': 2, 'edges': [bterms[termB], aterms[termA]]} )


def get_relationship_simple(a, b, force_search_A = False, force_search_B = False):
  adata = get_conceptnet_term(a, force_search_A)
  bdata = get_conceptnet_term(b, force_search_B)
  matches = []
  
  # build up a list of words A and B are connected to directly
  aterms = build_term_list(a, adata, True)
  bterms = build_term_list(b, bdata, False)
        
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
  
def get_relationship(a, b):
  relationships = get_relationship_simple(a, b, False, False)
  if len(relationships) == 0:
    relationships = get_relationship_simple(a, b, False, True)
  if len(relationships) == 0:
    relationships = get_relationship_simple(a, b, True, False)
  if len(relationships) == 0:
    relationships = get_relationship_simple(a, b, True, True)
  return relationships

print get_relationship("tale", "story")

# {"isA", "has"}

# traincepts = get_conceptnet_term("train")
# print traincepts['edges'][0]
# traincepts['edges'][0]['endLemmas']
# traincepts['edges'][0]['startLemmas']







