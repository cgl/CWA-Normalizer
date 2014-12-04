from  numpy import array
from pymongo import MongoClient
from conf import NA_TAGS, window_size

CLIENT = MongoClient('localhost', 27017)
try:
    db_tweets = CLIENT['tweets2']
    db_dict = CLIENT['dictionary2']
except:
    db_tweets  = None

M = int(window_size/2)
    # NO TAG

def get_candidates_scores_with_degree(tweet_pos_tagged,oov,oov_tag):
    froms,tos = get_neighbours(tweet_pos_tagged,oov)
    keys = []
    score_matrix = []
    for ind,(word, tag, _) in enumerate(froms):
        if tag not in NA_TAGS:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = len(froms) - 1 - ind
            cands_q = get_cands_with_degree(oov_tag, 'to', 'from', neigh_node, neigh_tag, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q, keys, score_matrix)
    for ind,(word, tag, _) in enumerate(tos):
        if tag not in NA_TAGS:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = ind
            cands_q = get_cands_with_degree(oov_tag, 'from', 'to', neigh_node, neigh_tag, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q,keys,score_matrix)
    return keys,score_matrix

def get_cands_with_degree(oov_tag, position, neigh_position, neigh_node, neigh_tag, distance):
    try: # to limit all neighbours
        db_tweets.nodes.find_one({'node':neigh_node, 'tag': neigh_tag})['freq']
    except:
        print(neigh_node)
        return []

    candidates_q = db_tweets.edges.find({neigh_position:neigh_node, neigh_position+'_tag': neigh_tag,
                    position+'_tag': oov_tag,
                    'dis': distance , 'weight' : { '$gt': 1 } })
    cands_q = []
    for node in candidates_q:
        cand = node[position] # cand
        if len(cand) < 2:
            continue
        # get frequencies of candidates
        if oov_tag == 'G':
            try:
                cand_tag = db_tweets.nodes.find({'node':cand, 'ovv':False}).sort("freq", 1)[0]['tag']
                degree = db_tweets.edges.find({position : cand, position+"tag" : cand_tag}).count()
            except IndexError:
                return []
        else:
            degree = db_tweets.edges.find({position : cand, position+"tag" : oov_tag}).count()
        cands_q.append({'position': position, 'cand':cand, 'weight': node['weight'] ,
                'freq' : degree})
    return cands_q


def get_candidates_scores_wo_tag(tweet_pos_tagged,oov):
    froms,tos = get_neighbours(tweet_pos_tagged,oov)
    keys = []
    score_matrix = []
    for ind,(word, tag, _) in enumerate(froms):
        if tag not in NA_TAGS:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = len(froms) - 1 - ind
            cands_q = get_graph_cands_wo_tag('to', 'from', neigh_node, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q, keys, score_matrix)
    for ind,(word, tag, _) in enumerate(tos):
        if tag not in NA_TAGS:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = ind
            cands_q = get_graph_cands_wo_tag('from', 'to', neigh_node, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q,keys,score_matrix)
    return keys,score_matrix

def get_graph_cands_wo_tag(position, neigh_position, neigh_node, distance):
    try:
        db_tweets.nodes.find_one({'node':neigh_node })['freq']
    except:
        return []
    candidates_q = db_tweets.edges.find({neigh_position:neigh_node,
                    'dis': distance , 'weight' : { '$gt': 1 } })
    cands_q = []
    for node in candidates_q:
        cand = node[position] # cand
        if len(cand) < 2:
            continue
        # get frequencies of candidates
        try:
            cand_node = db_tweets.nodes.find({'node':cand, 'ovv':False ,'freq': { '$gt': 8 } }).sort("freq", 1)[0]
        except IndexError:
            return []
        cands_q.append({'position': position, 'cand':cand, 'weight': node['weight'] , 'freq' : cand_node['freq']})
    return cands_q

def get_neighbours_by_string(tweet_pos_tagged,oov):
    froms = []
    tos = []
    for ind,(word, _ , _) in enumerate(tweet_pos_tagged):
        if word == oov:
            froms = tweet_pos_tagged[max(ind-M,0):ind]
            tos = tweet_pos_tagged[ind+1:ind+1+M]
    return froms, tos

def get_neighbours(tweet_pos_tagged,oov_index):
    froms = []
    tos = []
    ind = oov_index
    froms = tweet_pos_tagged[max(ind-M,0):ind]
    tos = tweet_pos_tagged[ind+1:ind+1+M]
    return froms, tos

def write_scores(neigh,neigh_tag,cands_q,keys,score_matrix):
    for cand_q in cands_q:
        new_scores = [array([cand_q['weight'],cand_q['freq']]),(neigh,neigh_tag)]
        if cand_q['cand']  not in keys:
            keys.append(cand_q['cand'])
            score_matrix.append([new_scores])
        else:
            index = keys.index(cand_q['cand'])
            score_matrix[index].append(new_scores)
    return keys,score_matrix
