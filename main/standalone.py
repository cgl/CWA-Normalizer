import normalizer,tools
from analysis import ext_contextual_candidates, add_slangs, add_from_dict, add_nom_verbs, iter_calc_lev,show_results, calculate_score, filter_and_sort_candidates, evaluate_alt
from conf import SLANG, database, window_size, distance, max_val, ovv_fun_20_filtered_extended as EMNLP_fun
from Oov_token import Oov_token

def main(tweet_as_str, oov_fun=EMNLP_fun ):
    tweet_pos_tagged = tools.parseTweet(tweet_as_str)
    tweet_annotated = [(word,tag,None,'OOV' if oov_fun(word,tag,_) else 'IV') for (word,tag,_) in tweet_pos_tagged]
    tweet_obj = Tweet(tweet_annotated)
    tweet_obj.normalize(True)
    tweet_obj.print_normalized()
    return tweet_obj

def norm_one(tweet, oov_index):
    oov = tweet[oov_index][0] # oov_tag = tweet[oov_index][1]
    norm = normalizer.Normalizer(database)
    norm.m = window_size/2
    contextual_candidates = ext_contextual_candidates(tweet,oov_index,norm)
    fms = add_slangs([contextual_candidates],SLANG)
    mapp = [[oov,None,tweet[oov_index][1]]]
    not_oov = ['' for a in mapp ]  # bos_oov
    fmd = add_from_dict(fms,[contextual_candidates],distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp)
    feat_mat = iter_calc_lev([contextual_candidates],fm_reduced,not_oov)
    res_dict = feat_mat[0]
    score_mat = filter_and_sort_candidates(res_dict,oov)
    return (feat_mat,contextual_candidates,fms,fmd),score_mat


def calculate_score_all_cands(feat_mat):
    for cand in feat_mat[0]:
        score = calculate_score(feat_mat[0][cand], max_val)
        feat_mat[0][cand].append(round(score,7))

def norm_all(tweets_annotated,order):
    lo_tweets = []
    evaluations = {'correct_answers':[], 'incorrect_answers':[], 'num_of_words_req_norm':0,
                   'incorrectly_corrected_word' : [], 'correctly_unchanged' : [], 'no_ans' : []}
    for ind,tweet in enumerate(tweets_annotated):
        tweet_obj = Tweet(tweet)
        tweet_obj.normalize(order)
        tweet_obj.evaluate(evaluations)
        lo_tweets.append(tweet_obj)
    ans = evaluations['correct_answers']
    incor = evaluations['incorrect_answers']
    fp = evaluations['incorrectly_corrected_word']
    no_ans = evaluations['no_ans']
    tools.get_performance(len(ans),len(incor),len(fp),len(no_ans),evaluations['num_of_words_req_norm'])
    return lo_tweets,evaluations

# standalone.construct_annotated(pos_tagged, results, conf.ovv_fun_20_filtered_extended)
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
        self.normalization = [] # tweet_annotated: [0:oov/answer,1:tag,2:canonical]
        self.oov_tokens = []
        self.evaluation = {}
        for ind,token in enumerate(tweet_annotated):
            self.tokens.append(token)
            self.normalization.append(token[0:3])
            if token[-1] == 'OOV':
                oov_token = Oov_token(token[0],ind,token[1],token[2],self)
                self.oov_tokens.append(oov_token)
            if token[0] != token[2]:
                self.num_of_words_req_norm += 1

    def __repr__(self):
        rep = ''
        for token in self.tokens:
            rep += (token[0] if token[3] == 'IV' else '['+str(token[0])+']') + ' '
        return rep

    def print_normalized(self):
        normalized = []
        no_change = []
        output = [token for token,_,_,_ in self.tokens]
        for oov_token in self.oov_tokens:
            if oov_token.answer:
                normalized.append(oov_token.oov_ind)
                output[oov_token.oov_ind] = oov_token.answer
            else:
                no_change.append(oov_token.oov_ind)
        print(" ".join(output))
        return output,normalized,no_change

    def normalize(self,order):
        for oov_token in self.oov_tokens:
            oov_token.norm_one()
            if order and oov_token.answer: #update normalized oov to answer
                self.normalization[oov_token.oov_ind] = (oov_token.answer,
                                            self.normalization[oov_token.oov_ind][1],
                                            self.normalization[oov_token.oov_ind][2])

    def evaluate(self,evaluations):
        self.evaluation['correct_answers'] = []            # True Positive
        self.evaluation['incorrect_answers'] =  []         # False Negative
        self.evaluation['incorrectly_corrected_word'] = [] # False Positive
        self.evaluation['correctly_unchanged'] = []        # True Negative
        self.evaluation['no_answer'] = []
        for oov_token in self.oov_tokens:
            correct_answer = oov_token.canonical
            oov = self.tokens[oov_token.oov_ind][0]
            answer = oov_token.answer or oov
            evaluate_alt(answer, correct_answer, oov, self.evaluation)
        evaluations['correct_answers'].extend(self.evaluation['correct_answers'])
        evaluations['incorrect_answers'].extend(self.evaluation['incorrect_answers'])
        evaluations['incorrectly_corrected_word'].extend(self.evaluation['incorrectly_corrected_word'])
        evaluations['correctly_unchanged'].extend(self.evaluation['correctly_unchanged'])
        evaluations['no_ans'].extend(self.evaluation['no_answer'])
        evaluations['num_of_words_req_norm'] += self.num_of_words_req_norm

    def __str__(self):
        rep = ''
        for oov_token in self.oov_tokens:
            rep += '%s\t: %s \n' %(oov_token.oov,oov_token.answer or '-')
        return rep
