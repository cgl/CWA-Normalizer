import normalizer,tools
from analysis import ext_contextual_candidates, add_slangs, add_from_dict, add_nom_verbs, iter_calc_lev,show_results, calculate_score, filter_and_sort_candidates, evaluate_alt
from conf import SLANG, database, window_size, distance, max_val, OOVFUNC as oov_fun
import pdb

def norm_one(tweet, oov_index):
    oov = tweet[oov_index][0] # oov_tag = tweet[oov_index][1]
    norm = normalizer.Normalizer([tweet],database)
    norm.m = window_size/2
    contextual_candidates = ext_contextual_candidates(tweet,oov_index,norm)
    fms = add_slangs([contextual_candidates],SLANG)
    mapp = [[oov,None,tweet[oov_index][1]]]
    not_oov = ['' for _ in mapp ]  # bos_oov
    fmd = add_from_dict(fms,[contextual_candidates],distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp)
    feat_mat = iter_calc_lev([contextual_candidates],fm_reduced,not_oov)
    res_dict = feat_mat[0]
    score_mat = filter_and_sort_candidates(res_dict,oov)
    return feat_mat,score_mat


def calculate_score_all_cands(feat_mat):
    for cand in feat_mat[0]:
        score = calculate_score(feat_mat[0][cand], max_val)
        feat_mat[0][cand].append(round(score,7))

def norm_all(tweets_annotated,order):
    lo_tweets = []
    evaluations = {'correct_answers':[], 'incorrect_answers':[], 'num_of_words_req_norm':0,
                   'incorrectly_corrected_word' : [], 'correctly_unchanged' : [] }
    for ind,tweet in enumerate(tweets_annotated):
        print(ind)
        tweet_obj = Tweet(tweet)
        tweet_obj.normalize(order)
        tweet_obj.evaluate(evaluations)
        lo_tweets.append(tweet_obj)
    ans = evaluations['correct_answers']
    incor = evaluations['incorrect_answers']
    fp = evaluations['incorrectly_corrected_word']
    tools.get_performance(len(ans),len(incor),len(fp),evaluations['num_of_words_req_norm'])
    return lo_tweets,evaluations

# standalone.construct_annotated(constants.pos_tagged, constants.results, conf.ovv_fun_20_filtered_extended)
def construct_annotated(pos_tagged, results,oov_fun):
    annotated = []
    for t_ind,tweet in enumerate(results):
        ann_list = []
        for w_ind,(word,stag,corr) in enumerate(tweet):
            ann_list.append((word,pos_tagged[t_ind][w_ind][1],corr,
                             'OOV' if oov_fun(word,stag,corr) else 'IV'))
        annotated.append(ann_list)
    return annotated

# tweet:
class Tweet:
    def __init__(self, tweet_annotated):
        self.num_of_words_req_norm = 0
        self.tokens = [] # tweet_annotated [[0:oov,1:tag,2:canonical,3:'OOV'/'IV'],..]
        self.normalization = [] # tweet_annotated
        self.oov_tokens = [] # [ind, tag, normalization]
        for ind,token in enumerate(tweet_annotated):
            self.tokens.append(token)
            self.normalization.append(token[0:3])
            if token[-1] == 'OOV':
                self.oov_tokens.append([ind,token[1]])
            if token[0] != token[2]:
                self.num_of_words_req_norm += 1
        print('There are %s oov words in the tweet' %len(self.oov_tokens))

    def normalize(self,order):
        for oov_token in self.oov_tokens:
            oov_ind = oov_token[0]
            _,cand_list = norm_one(self.normalization,oov_ind)
            best_cand = cand_list[0][0] if cand_list else None
            oov_token.append(best_cand)
            if order and best_cand:
                self.normalization[oov_token[0]] = (best_cand,self.tokens[oov_token[0]][1],self.tokens[oov_token[0]][2])

    def evaluate(self,evaluations):
        self.evaluation = {}
        self.evaluation['correct_answers'] = []            # True Positive
        self.evaluation['incorrect_answers'] =  []         # False Negative
        self.evaluation['incorrectly_corrected_word'] = [] # False Positive
        self.evaluation['correctly_unchanged'] = []        # True Negative
        for oov_token in self.oov_tokens:
            correct_answer = self.tokens[oov_token[0]][2] # canonical
            oov = self.tokens[oov_token[0]][0]
            answer = oov_token[-1] or oov #best_cand
            evaluate_alt(answer, correct_answer, oov, self.evaluation)
        evaluations['correct_answers'].extend(self.evaluation['correct_answers'])
        evaluations['incorrect_answers'].extend(self.evaluation['incorrect_answers'])
        evaluations['incorrectly_corrected_word'].extend(self.evaluation['incorrectly_corrected_word'])
        evaluations['correctly_unchanged'].extend(self.evaluation['correctly_unchanged'])
        evaluations['num_of_words_req_norm'] += self.num_of_words_req_norm

    def __str__(self):
        for token in self.oov_tokens:
            print(self.tokens[token[0]]+': '+token)
