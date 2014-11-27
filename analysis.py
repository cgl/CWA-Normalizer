from scoring import han,pennel
import enchant
from fuzzy import DMetaphone
import normalizer
import graph
import CMUTweetTagger
import tools
import numpy
import re
import copy
import traceback
import logging
import constants
from extra import calc_score_matrix_wo_tag, calc_score_matrix_with_degree

from conf import SLANG, threshold, slang_threshold, max_val, verbose, distance, database, OOVFUNC as oov_fun, wo_tag, with_degree, window_size

# create file handler which logs even debug messages
fh = logging.FileHandler('analysis.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fh.setFormatter(formatter)
# add the handlers to logger
root_logger = logging.getLogger()
root_logger.propagate = False
root_logger.addHandler(fh)
#root_logger.disabled = True

def main(index=False):
    results = han(549)[1]
    oov = lambda x,y : True if y == 'OOV' else False
    in_suggestions(results,oov,index_count=index)

if __name__ == "__main__ ":
    main()

# Usage not_oov = detect_oov(slang,mapp)
def detect_oov(slang,mapp):
    not_oov = []
    for ind in range (0,len(mapp)):
        oov = mapp[ind][0]
        oov_reduced = tools.get_reduced(oov,count=1)
        #oov_reduced = tools.get_reduced_alt(oov) or oov
        if slang.has_key(oov_reduced):
            s_word = slang.get(oov) or slang.get(oov_reduced)
            if len(s_word.split(" ")) >  1:
                not_oov.append(oov)
            else:
                not_oov.append('')
        elif oov.isdigit():
            not_oov.append(oov)
#        elif len(oov_reduced) > 1 and dic.check(oov_reduced.capitalize()):
#            not_oov.append(oov_reduced.capitalize())
        elif not oov_reduced.isalnum():
            not_oov.append(oov)
        else:
            not_oov.append('')
    i = 0
    for ind,words in enumerate(mapp):
        if words[0] == words[1]:
            if not not_oov[ind]:
                i += 1
    print i," not oov detected"
    return not_oov


def add_from_dict(fm, mat, distance, not_oov):
    clean_words = tools.get_clean_words()
    for ind,cands in enumerate(fm):
        if not not_oov[ind]:
            cands = find_more_results(mat[ind][0][0],mat[ind][0][1],cands,clean_words,distance)
    return fm

def find_more_results(oov,oov_tag,cand_dict,clean_words,distance,give_suggestions=True):
    cands = tools.get_from_dict_met(oov,{})
    cands_more = tools.get_from_dict_dis(oov,oov_tag,clean_words,distance)
    cands.extend(cands_more)
    cands = list(set(cands))
    if give_suggestions:
        sugs = tools.get_suggestions(oov,oov_tag)
        cands.extend(sugs)
    for cand in cands:
        if not cand_dict.has_key(cand):
            cand_dict[cand] = get_score_line(cand,0,oov,oov_tag)
    return cand_dict

def iter_calc_lev(matrix, fm, not_oov ,edit_dis=2,met_dis=1,verbose=False):
    for ind,cands in enumerate(fm):
        if not not_oov[ind]:
            cands = get_candidates_from_graph(matrix[ind],matrix[ind][0][0], matrix[ind][0][1],cands,edit_dis,met_dis)
    return fm

def get_candidates_from_graph(matrix_line,oov,oov_tag,cand_dict,edit_dis,met_dis):
    filtered_cand_list = [cand for cand in matrix_line[1]
                          if cand_dict.has_key(cand) or tools.filter_cand(oov,cand,edit_dis=edit_dis,met_dis=met_dis)]

    for cand in filtered_cand_list:
        sumof = 0.
        for a,b in matrix_line[2][matrix_line[1].index(cand)]:
            sumof += a[0]/a[1]
        if not cand_dict.has_key(cand):
            cand_dict[cand] = get_score_line(cand,sumof,oov,oov_tag)
        else:
            cand_dict[cand][0] = round(sumof,7)
            #cand_dict[cand][0] += sumof
    return cand_dict

def get_score_line(cand,sumof,oov,oov_tag):
    node =  tools.get_node(cand,tag=oov_tag)
    #node_wo_tag =  tools.get_node(cand)
    freq = freq_score(int(node['freq'])) if node else 0.
    #freq_wo_tag = freq_score(int(node_wo_tag[0]['freq'])) if node_wo_tag else 0.
    #degree = tools.get_degree_score(cand,oov_tag)
    line = [ #cand,
            sumof,                                # weight
            tools.lcsr(oov,cand),                 # lcsr
            tools.distance(oov,cand),             # distance
            0, # degree,  #freq_wo_tag,
            #tools.common_letter_score(oov,cand),  # shared letter
            0,                                    # 7 : is_in_slang
            freq,
    ]
    for ind in range(0,len(line)):
        line[ind] = round(line[ind],8)
    return line

def freq_score(freq):
    if freq >= 715:
        return 1
    elif freq >= 327:
        return 0.8
    elif freq >= 205:
        return 0.6
    elif freq >= 100:
        return 0.4
    elif freq >= 9:
        return 0.2
    else:
        return 0

def add_slangs(mat,slang,verbose=False):
    res_mat = []
    for ind in range (0,len(mat)):
        oov = mat[ind][0][0]
        oov_reduced = tools.get_reduced(oov,count=2)
        #oov_reduced = tools.get_reduced_alt(oov) or oov
        cands = {}
        if slang.has_key(oov_reduced):
            sl = slang.get(oov_reduced).lower()
            if len(sl.split(" ")) <=  1:
                oov_tag =  mat[ind][0][1]
                res_line = get_score_line(sl,0,oov,oov_tag)
                res_line[4] = 1
                cands[sl] = res_line
                if verbose:
                    print ind,oov,sl,cands[sl]
        res_mat.append(cands)
    return res_mat

def calculate_score(res_vec,max_val):
    try:
        score  =  res_vec[0] * max_val[0]  # weight
        score +=  res_vec[1] * max_val[1]  # lcsr
        score +=  res_vec[2] * max_val[2]  # distance
        score +=  res_vec[3] * max_val[3]  # common letter
        score +=  res_vec[4] * max_val[4]  # slang
        score +=  res_vec[5] * max_val[5]  # freq
        return score
    except IndexError, i:
        print res_vec,i
    except TypeError, e:
        print res_vec
        print traceback.format_exc()

# tweets, results = han(548)
def calc_each_neighbours_score(tweets_str, results, oov,tweets):
    lo_tweets = CMUTweetTagger.runtagger_parse(tweets_str)
    lo_candidates = []
    norm = normalizer.Normalizer(lo_tweets)
    for i in range(0,len(results)):
        tweet = results[i]
        tweet_pos_tagged = CMUTweetTagger.runtagger_parse([tweets[i]])[0] # since only 1 tweet
        for j in range(0,len(tweet)):
            word = tweet[j]
            if oov(word[0],word[1]):
                oov_word = word[0]
                oov_tag = tweet_pos_tagged[j][1]
                candidates = norm.get_neighbours_candidates(tweet_pos_tagged,oov_word,oov_tag)
                lo_candidates.append({'oov_word' : oov_word , 'tag' : oov_tag , 'cands' : candidates})
    return lo_candidates

def in_suggestions(results,oov,index_count=False):
    pos = {} if index_count else 0
    neg = 0
    dictinary = enchant.Dict("en_US")
    for tweet in results:
        for word in tweet:
            # word = (u'comming', u'OOV', u'coming')
            if oov(word[0],word[1]):
                suggestions = [sug for sug in  dictinary.suggest(word[0]) if dictinary.check(sug)]
                if word[2] in suggestions:
                    if index_count:
                        pos[suggestions.index(word[2])] = pos.get(suggestions.index(word[2]),0) + 1
                    else:
                        pos += 1
                else:
                    neg += 1
    print '%s positive result, %d negative result' % (pos, neg)

def metaphone_match(results,oov):
    pos = 0
    neg = 0
    for tweet in results:
        for word in tweet:
            if oov(word[0],word[1]):
                met_oov = set([met for met in set(DMetaphone(4)(word[0])) if met is not None])
                met_cand = [met for met in set(DMetaphone(4)(word[2])) if met is not None]
                intersects =  met_oov.intersection(met_cand)
                if len(intersects):
                    pos += 1
                else:
                    print '%s [%s] : %s and %s %s' % (word[0],word[2], met_oov , met_cand ,intersects)
                    neg += 1
    print '%s positive result, %d negative result' % (pos, neg)

def contains(tweets,results,oov):
    lo_tweets = CMUTweetTagger.runtagger_parse(tweets)
    N = normalizer.Normalizer(lo_tweets);
    pos = 0
    pos_dict = {}
    lo_candidates = []
    neg = 0
    for i in range(0,len(results)):
        tweet = results[i]
        tweet_pos_tags = CMUTweetTagger.runtagger_parse([tweets[i]])[0] # since only 1 tweet
        for j in range(0,len(tweet)):
            word = tweet[j]
            if oov(word[0],word[1]):
                oov_word = word[0]
                tag = tweet_pos_tags[j][1]
                candidates = N.normalize(oov_word.decode(), tag, j, tweet_pos_tags ,allCands=True)
                index = [candidates.index(x) for x in candidates if x[0] == word[2]]
                if index:
                    pos += 1
                    pos_dict[index[0]] = pos_dict.get(index[0],0) + 1
                    print '%s :[%s]%s ' % (word[0],index[0],word[2])
                else:
                    neg += 1
                lo_candidates.append({oov_word : candidates, 'contains' : True if index else False })
    print '%s positive result, %d negative result' % (pos, neg)
    print pos_dict
    return lo_candidates

def repeat_check(results,oov):
    pass


def check(results,oov,method):
    for tweet in results:
        for word in tweet:
            if oov(word[0],word[1]):
                method(results,oov)

def add_nom_verbs(fm,mapp):
    for ind,cands in enumerate(fm):
        oov = mapp[ind][0]
        oov_tag = mapp[ind][2]
        add_nom_verbs_inner(oov,oov_tag,cands)
    return fm

def add_nom_verbs_inner(oov,oov_tag,cands):
        if oov_tag == "L" :
            if oov.lower() == u"im":
                cand = u"i'm"
                add_candidate(cands,cand,oov,oov_tag,slang_threshold)
        elif oov_tag == u"~":
            if oov.lower() == u"cont":
                cand = u'continued'
                add_candidate(cands,cand,oov,oov_tag,slang_threshold)
        elif oov_tag == u"P":
            if tools.pronouns.has_key(oov):
                cand = tools.pronouns[oov]
                add_candidate(cands,cand,oov,oov_tag,slang_threshold)
        elif oov_tag == u"R":
            if oov == u"2":
                cand = u"too"
                add_candidate(cands,cand,oov,oov_tag,slang_threshold)
        #cand = tools.get_reduced(oov,count=2)
        cand = tools.get_reduced_alt(oov)
        if cand and oov != cand:
            add_candidate(cands,cand,oov,oov_tag,slang_threshold*0.8)
        cand = tools.replace_digits_alt(oov)
        if cand and oov != cand:
            add_candidate(cands,cand,oov,oov_tag,slang_threshold)

def add_candidate(cands,cand,oov,oov_tag,slang_threshold):
    if not cands.has_key(cand):
        cands[cand] = get_score_line(cand,0,oov,oov_tag)
    cands[cand][4] = slang_threshold

#--------------------------------------------------------------

def calc_score_matrix(lo_postagged_tweets,results,oov_fun,window_size):
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database)
    norm.m = window_size/2
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = results[tweet_ind][j]
            if oov_fun(word[0],word[1],word[2]):
                contextual_candidates = ext_contextual_candidates(tweet_pos_tagged,j,norm)
                lo_candidates.append(contextual_candidates)
                #lo_candidates.append([(word[0],oov_tag),[word[0]], # to append oov word itself to the candidate list
                #                      [[[numpy.array([    9.93355,  4191.     ]), 'new|A'],
                #                        [numpy.array([  1.26120000e+00,   4.19100000e+03]), 'pix|N']]] ])
    return lo_candidates

def ext_contextual_candidates(tweet_pos_tagged,oov_ind,norm):
    oov_word = tweet_pos_tagged[oov_ind][0]
    oov_tag = tweet_pos_tagged[oov_ind][1]
    keys,score_matrix = norm.get_candidates_scores(tweet_pos_tagged,oov_ind,oov_tag)
    oov_word_reduced = tools.get_reduced(oov_word,count=2)
    #oov_word_reduced = tools.get_reduced_alt(oov_word) or oov_word
    oov_word_digited = tools.replace_digits(oov_word_reduced)
    return [(oov_word_digited,oov_tag),keys,score_matrix]

def construct_mapp_penn(pos_tagged_penn, results_penn):
    mapp_penn = []
    for t_ind,tweet in enumerate(results_penn):
        for w_ind,(word,stag,cor) in enumerate(tweet):
            if stag == "OOV":
                mapp_penn.append((word,cor,pos_tagged_penn[t_ind][w_ind][1]))
    return mapp_penn

def calculate_score_penn(hyp_file,ref_file):
    tweets_penn,results_penn = pennel(5000,hyp_file,ref_file)
    pos_tagged_penn = CMUTweetTagger.runtagger_parse(tweets_penn)
    window_size = 5
    matrix_penn = calc_score_matrix(pos_tagged_penn, results_penn, oov_fun, window_size)
    mapp_penn = construct_mapp_penn(pos_tagged_penn, results_penn)
    bos_oov_penn = ['' for word in mapp_penn ]
    set_penn = run(matrix_penn,[],[],bos_oov_penn,results = results_penn, pos_tagged = pos_tagged_penn)
    return set_penn, mapp_penn, results_penn, pos_tagged_penn

def construct_mapp(pos_tagged, results,oov_fun):
    mapp = []
    for t_ind,tweet in enumerate(results):
        for w_ind,(word,stag,cor) in enumerate(tweet):
            if oov_fun(word,stag,cor):
                mapp.append((word,cor,pos_tagged[t_ind][w_ind][1]))
    return mapp

def test_detection(index,oov_fun):
    if index:
        pos_tagged = constants.pos_tagged[index:index+1]
        results = constants.results[index:index+1]
    else:
        pos_tagged = constants.pos_tagged
        results = constants.results
    matrix1 = calc_score_matrix(pos_tagged,results,oov_fun, window_size)
    mapp = construct_mapp(pos_tagged, results, oov_fun)
    all_oov =  ['' for word in mapp ]
    set_oov_detect = run(matrix1,[],[],all_oov,results = results, pos_tagged = pos_tagged)
    return set_oov_detect

# res_dict = feat_mat[ind]
def filter_and_sort_candidates(res_dict,oov):
    res_list = []
    if res_dict:
        for res_ind,cand in enumerate(res_dict):
            #if(not tools.spell_check(cand)): #or oov == cand): # spell check on graph is problematic
            #    continue;
            score = calculate_score(res_dict[cand],max_val)
            if score >= threshold and cand != oov:
                res_dict[cand].append(round(score,7))
                res_line = [cand]
                res_line.extend(res_dict[cand])
                res_list.append(res_line)
        res_list.sort(key=lambda x: -float(x[-1]))
    return res_list

def evaluate_alt(answer, correct_answer, oov, evaluation):
    if answer != oov: # ppl --> people , people --> ppl, ppl --> apple
        if answer.lower() == correct_answer.lower() : # tp: ppl --> people
            evaluation['correct_answers'].append(answer)
        else:
            if oov == correct_answer: # fp: people --> ppl
                evaluation['incorrectly_corrected_word'].append(answer)
            else:                     # fn: ppl --> apple
                evaluation['incorrect_answers'].append(answer)
    else: # people --> people , ppl --> ppl
        if oov != correct_answer: # fn: ppl  --> ppl
            pass #incorrect_answers.append((ind,answer))
        else:                     # tn: people --> people
            evaluation['correctly_unchanged'].append(answer)

def evaluate(answer, correct_answer, oov,correct_answers, ind, incorrect_answers,
             incorrectly_corrected_word, correctly_unchanged):
    if answer != oov: # ppl --> people , people --> ppl, ppl --> apple
        if answer.lower() == correct_answer.lower() : # tp: ppl --> people
            correct_answers.append((ind,answer))
        else:
            if oov == correct_answer: # fp: people --> ppl
                incorrectly_corrected_word.append((ind,answer))
            else:                     # fn: ppl --> apple
                incorrect_answers.append((ind,answer))
    else: # people --> people , ppl --> ppl
        if oov != correct_answer: # fn: ppl  --> ppl
            pass #incorrect_answers.append((ind,answer))
        else:                     # tn: people --> people
            correctly_unchanged.append((ind,answer))

# show_results(feat_mat, mapp, not_oov = not_oov)
def show_results(res_mat,mapp, not_oov = []):
    results = []
    correct_answers = [] # True Positive
    incorrect_answers = [] # False Negative
    miss = []
    incorrectly_corrected_word = [] # False Positive
    correctly_unchanged = [] # True Negative
    for ind in range (0,len(res_mat)):
        oov = mapp[ind][0]
        if not_oov and not_oov[ind]:
            res_list = [[not_oov[ind],0,0,0,0,0,0]]
        else:
            res_dict = copy.deepcopy(res_mat[ind])
            res_list = filter_and_sort_candidates(res_dict,oov)
        results.append(res_list)
        answer = res_list[0][0] if res_list else oov
        correct_answer = mapp[ind][1]
        evaluate(answer, correct_answer, oov,correct_answers, ind, incorrect_answers,
                 incorrectly_corrected_word, correctly_unchanged)
    print '# of correct normalizations %s, incorrect norms %s, changed correct token %s' % (
        len(correct_answers),len(incorrect_answers),len(incorrectly_corrected_word))
    return results,correct_answers,incorrect_answers, incorrectly_corrected_word, correctly_unchanged

def run(matrix1,fmd,feat_mat,not_oov,results = constants.results,
        pos_tagged = constants.pos_tagged):
    mapp = construct_mapp(pos_tagged, results, oov_fun)
    if not_oov is None:
        bos_oov = [word[0] if word[0] == word[1] else '' for word in mapp ]
        not_oov = bos_oov
    if not matrix1:
        if with_degree:
            matrix1 = calc_score_matrix_with_degree(pos_tagged,results,oov_fun,window_size)
        elif not wo_tag:
            matrix1 = calc_score_matrix(pos_tagged,results,oov_fun,window_size)
        else:
            matrix1 = calc_score_matrix_wo_tag(pos_tagged,results,oov_fun,window_size)
    #max_val=[1.0, 1.0, 1.0, 1.0, 5.0, 1./1873142]
    fms = add_slangs(matrix1,SLANG)
    if not fmd:
        fmd = add_from_dict(fms,matrix1,distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp)
    if not feat_mat:
        feat_mat = iter_calc_lev(matrix1,fm_reduced,not_oov)
        #feat_mat2 = add_weight(feat_mat,mapp,not_oov)
    res,ans,incor, fp, tn = show_results(feat_mat, mapp, not_oov = not_oov)
    try:
        ann_and_pos_tag = tools.build_mappings(results,pos_tagged,oov_fun)
        index_list,nil,no_res = tools.top_n(res,not_oov,mapp,ann_and_pos_tag)
        num_of_normed_words = len(ans) + len(incor)
        num_of_words_req_norm = len(filter(lambda x: x[0] != x[1], mapp))
        #num_of_words_not_changed = len(filter(lambda x: x==1,[1 if ans and mapp[ind][1] != mapp[ind][0] and ans[0][0] == mapp[ind][0] else 0 for (ind,ans) in enumerate(res)]))
        tools.get_performance(len(ans),len(incor),len(fp),num_of_words_req_norm)
        tools.get_performance_old(len(ans),len(no_res),len(incor),len([oov for oov in not_oov if oov == '']))
        threshold = tools.get_score_threshold(index_list,res)
        tools.test_threshold(res,threshold)
        return [res, feat_mat, fmd, matrix1, ans, incor, nil, no_res, index_list, mapp, fp]
        #        0   1         2    3        4    5      6    7       8           9     10
    except:
        print(traceback.format_exc())
        return [res, feat_mat, fmd, matrix1, ans, incor]

def normalize(tweet):
    oov_fun = lambda x,y,z : not tools.spell_check(x)
    pos_tagged = CMUTweetTagger.runtagger_parse([tweet,])
    matrix1 = calc_mat(results = pos_tagged, pos_tagged = pos_tagged)
    mapp = construct_mapp(pos_tagged, pos_tagged, oov_fun)
    fms = add_slangs(matrix1,SLANG)
    not_oov = ['' for word in mapp ]
    fmd = add_from_dict(fms,matrix1,distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp)
    feat_mat = iter_calc_lev(matrix1,fm_reduced,not_oov)
    res = calculate_results(feat_mat, mapp)
    return " ".join([res[word[0]] if res.has_key(word[0]) else word[0] for word in pos_tagged[0]])


def calculate_results(res_mat,mapp):
    results = {}
    for ind in range (0,len(res_mat)):
        oov = mapp[ind][0]
        res_dict = res_mat[ind]
        res_list = []
        if res_dict:
            for res_ind,cand in enumerate(res_dict):
                score = calculate_score(res_dict[cand],max_val)
                if score >= threshold:
                    res_dict[cand].append(round(score,7))
                    res_line = [cand]
                    res_line.extend(res_dict[cand])
                    res_list.append(res_line)
            res_list.sort(key=lambda x: -float(x[-1]))
        answer = res_list[0][0] if res_list else oov
        results[oov] = answer
    return results

def run_old(matrix1,fmd,feat_mat,slang,not_oov,mapp,results = constants.results,
        pos_tagged = constants.pos_tagged):
    if not matrix1:
        matrix1 = calc_score_matrix(pos_tagged, results, oov_fun, window_size)
    #max_val=[1.0, 1.0, 1.0, 1.0, 5.0, 1./1873142]
    if not slang:
        slang = tools.get_slangs()
    if not not_oov:
        not_oov = [word[0] if word[0] == word[1] else '' for word in mapp ]
    fms = add_slangs(matrix1,slang)
    if not fmd:
        fmd = add_from_dict(fms,matrix1,distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp)
    if not feat_mat:
        feat_mat = iter_calc_lev(matrix1, fm_reduced, not_oov)
        #feat_mat2 = add_weight(feat_mat,mapp,not_oov)
    res,ans,incor, fp, tn = show_results(feat_mat, mapp, not_oov = not_oov)
    try:
        ann_and_pos_tag = tools.build_mappings(results,pos_tagged,oov_fun)
        index_list,nil,no_res = tools.top_n(res,not_oov,mapp,ann_and_pos_tag)
        tools.get_performance_old(len(ans),len(no_res),len(incor),len([oov for oov in not_oov if oov == '']))
        threshold = tools.get_score_threshold(index_list,res)
        tools.test_threshold(res,threshold)
        return [res, feat_mat, fmd, matrix1, ans, incor, nil, no_res, index_list]
        #        0   1         2    3        4    5      6    7       8
    except:
        print(traceback.format_exc())
        return [res, feat_mat, fmd, matrix1, ans, incor]
