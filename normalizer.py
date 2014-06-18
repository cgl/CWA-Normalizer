import enchant
from pymongo import MongoClient
from tools import isMention, isHashtag, isvalid
import Levenshtein as Lev
import fuzzy
from math import log
from  numpy import array
import pdb
import logging
from graph import write_scores, get_neighbours

salient=0.001
class Normalizer:

    # input is a list s.t.
#lot = [[('example', 'N', 0.979), ('tweet', 'V', 0.7763), ('1', '$', 0.9916)],
#       [('example', 'N', 0.979), ('tweet', 'V', 0.7713), ('2', '$', 0.5832)]]
    def __init__(self, input, database='tweets',method='normalize'):
        max_dis = 4  # n-gram
        self.method = method
        self.m = max_dis - 1
        self.texts = input
        self.d = enchant.Dict("en_US")
        client = MongoClient('localhost', 27017)
        db = client[database]
        self.nodes = db['nodes']
        self.edges = db['edges']
        self.ovvLists = [[ind for ind, t in enumerate(text)
                          if self.isOvv(t[0], t[1])] for text in self.texts]
    def isOvvStr(self, w, t):
        return 'OVV' if self.isOvv(w, t) else 'IV'

    def isOvv(self, w, t):
#            if not isvalid(w):
        if t in [',','E','~','@','U']: # punctuation, emoticon, discourse marker, mention, url
            return False
        elif t in ['$',] or isMention(w): # Numeral or url or mention
            return False
        elif t in ['#'] or isHashtag(w):
            return False
        elif not isvalid(w) and t is not '&' :
            #print '%s : %s is not ovv' % (t, w)
            return False
        else:
            return not self.d.check(w)

    def normalizeAll(self):
        results = []
        for ind,tweet in enumerate(self.texts):
            tweet_result = [ self.make_tuple(word.decode(),tag,word_ind,ind) for (word_ind ,(word, tag, conf)) in enumerate(tweet)]
            results.append(tweet_result)
        return results

    # Given a word and its pos tag normalizes it IF NECESSARY
    # Given also the whole tweet and word's index within the tweet
    def normalize(self,word, tag, word_ind, tweet,allCands=False):
#        if self.norm_tricks(word,tag):
#            return self.norm_tricks(word,tag)
#        if not self.isOvv(word,tag):
#            return word
        ovvWord = word
        print ovvWord
        ovvTag = tag
        ovvInd = word_ind
        scores = {}
        scores = self.returnCandRight(tweet,ovvWord,ovvInd, ovvTag,{})
        scores = self.returnCandLeft(tweet,ovvWord,ovvInd, ovvTag,scores)
#        for sug in filter(self.d.check,self.d.suggest(ovvWord)):
#            self.updateScore_suggested(scores,sug,ovvWord,ovvTag)
        scores_sorted = sorted(scores.items(), key= lambda x: x[1][0], reverse=True)
        if scores_sorted:
            #print 'Ovv: "%s" with tag: %s corrected as: "%s" with a score %d' %(ovvWord,ovvTag, scores_sorted[0][0], scores_sorted[0][1])
            if allCands:
                return scores_sorted[:200]
            return scores_sorted[0][0].lower()
        else:
            return word

    def make_tuple(self, word, tag, word_ind, tweet_ind):
        normalizer = getattr(self, self.method)
        return (word, self.isOvvStr(word, tag),
                normalizer(word, tag, word_ind, self.texts[tweet_ind]))

#---------------------------------------------------
    def get_candidates_scores(self, tweet_pos_tagged,ovv,ovv_tag):
        froms,tos= get_neighbours(tweet_pos_tagged,ovv)
        keys = []
        score_matrix = []
        for ind,(word, tag, acc) in enumerate(froms):
          if tag not in [',','@']:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = len(froms) - 1 - ind
            cands_q = self.get_cands_with_weigh_freq(ovv, ovv_tag, 'to', 'from', neigh_node, neigh_tag, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q, keys, score_matrix)
        for ind,(word, tag, acc) in enumerate(tos):
          if tag not in [',','@']:
            neigh_node = word.strip()
            neigh_tag = tag
            distance = ind
            cands_q = self.get_cands_with_weigh_freq(ovv, ovv_tag, 'from', 'to', neigh_node, neigh_tag, distance)
            keys,score_matrix = write_scores(neigh_node,neigh_tag,cands_q,keys,score_matrix)
        return keys,score_matrix

    def get_cands_with_weigh_freq(self, ovv_word, ovv_tag, position, neigh_position, neigh_node, neigh_tag, distance):
        try:
            neigh_node_freq = self.nodes.find_one({'node':neigh_node,'tag': neigh_tag })['freq']
        except:
            return []
        candidates_q = self.edges.find({neigh_position:neigh_node, neigh_position+'_tag': neigh_tag,
                                        position+'_tag': ovv_tag,
                                        'dis': distance , 'weight' : { '$gt': 1 } })
        cands_q = []
        for node in candidates_q:
            cand = node[position] # cand
            if len(cand) < 2:
                continue
            # get frequencies of candidates
            if ovv_tag == 'G':
                try:
                    cand_node = self.nodes.find({'node':cand, 'ovv':False ,'freq': { '$gt': 8 } }).sort("freq", 1)[0]
                except IndexError:
                    return []
            else:
                cand_node = self.nodes.find_one({'node':cand,'tag': ovv_tag, 'ovv':False ,'freq': { '$gt': 8 } })
            if(cand_node):
                cands_q.append({'position': position, 'cand':cand, 'weight': node['weight'] ,
                                'freq' : cand_node['freq']})
        return cands_q

#-------------------------------------------------------

    def returnCandRight(self,tweet,ovvWord,ovvInd, ovvTag,scores):
        neigh_start_ind = max(ovvInd-self.m,0)
        neigh_end_ind = ovvInd
        left = False
        position = 'to'
        neigh_position = 'from'
        return self.returnCand(tweet,ovvWord,ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position)

    def returnCandLeft(self,tweet,ovvWord,ovvInd, ovvTag,scores):
        neigh_start_ind = ovvInd+1
        neigh_end_ind = ovvInd+1+self.m
        left = True
        position = 'from'
        neigh_position = 'to'
        return self.returnCand(tweet,ovvWord,ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position)

    def returnCand(self,tweet,ovvWord, ovvInd, ovvTag,scores,
                   neigh_start_ind,neigh_end_ind, left, position,neigh_position):
#        print 'Ovv: %s with tag %s' %(ovvWord,ovvTag)
        neighbours = tweet[neigh_start_ind:neigh_end_ind]
        for ind_neigh,neighbour in enumerate(neighbours):
            distance = ind_neigh if left else len(neighbours) - ind_neigh
            neigh_node = neighbour[0].strip()
            neigh_tag = neighbour[1]
            # For each word next to ovv we look to the graph for candidates
            # thatshares same distance and tag with the ovv
            # find all the non ovv nodes from the neighbour with same dis
            cands_q = self.get_cands_with_weigh_freq(ovvWord, ovvTag, position, neigh_position, neigh_node, neigh_tag, distance)
            n_ind = distance
            scores = self.score(ovvWord,cands_q,n_ind,scores)
        return scores

    def score(self, ovvWord, cands_q, n, scores):
        for cand_q in cands_q:
            cand = cand_q['cand']
            #self.updateScore(scores,cand,score)
            print '%s: %f %f' %(cand, cand_q['weight'],cand_q['freq'])
            self.updateScore(scores,cand,
                             cand_q['weight'], cand_q['freq'])
        return scores
        #scores_sorted = sorted(scores.items(), key= lambda x: x[1], reverse=True)

    def updateScore(self,scores,cand,weight,freq):
        #score = log(weight) * (1/lev) * met * log(freq)
        if scores.has_key(cand):
            score_set = scores.get(cand)
        else:
            score_set = array([0., 0.])
        current_score_set = array([0,weight, freq])
        current_score_set[0] = current_score_set[1]/max(current_score_set[2],0.00001)
#        print current_score_set[0]
        score_set = current_score_set + score_set
        scores.update({cand:score_set})
        return scores
