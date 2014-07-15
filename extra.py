import numpy
import normalizer,graph,tools

def calc_score_matrix_wo_tag(lo_postagged_tweets,results,ovv_fun,window_size, database='tweets'):
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database=database)
    norm.m = window_size/2
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = results[tweet_ind][j]
            if ovv_fun(word[0],word[1],word[2]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                keys,score_matrix = graph.get_candidates_scores_wo_tag(tweet_pos_tagged,ovv_word)
                ovv_word_reduced = tools.get_reduced(ovv_word,count=2)
                #ovv_word_reduced = tools.get_reduced_alt(ovv_word) or ovv_word
                ovv_word_digited = tools.replace_digits(ovv_word_reduced)
                lo_candidates.append([(ovv_word_digited,ovv_tag),keys,score_matrix])
            elif word[1] == "OOV":
                lo_candidates.append([(word[0],ovv_tag),[word[0]],
                                      [[[numpy.array([    9.93355,  4191.     ]), 'new|A'],
                                        [numpy.array([  1.26120000e+00,   4.19100000e+03]), 'pix|N']]]
                                  ])
    return lo_candidates

def calc_score_matrix_with_degree(lo_postagged_tweets,results,ovv_fun,window_size, database='tweets'):
    lo_candidates = []
    norm = normalizer.Normalizer(lo_postagged_tweets,database=database)
    norm.m = window_size/2
    for tweet_ind in range(0,len(lo_postagged_tweets)):
        tweet_pos_tagged = lo_postagged_tweets[tweet_ind]
        for j in range(0,len(tweet_pos_tagged)):
            word = results[tweet_ind][j]
            if ovv_fun(word[0],word[1],word[2]):
                ovv_word = word[0]
                ovv_tag = tweet_pos_tagged[j][1]
                keys,score_matrix = graph.get_candidates_scores_with_degree(tweet_pos_tagged,ovv_word,ovv_tag)
                ovv_word_reduced = tools.get_reduced(ovv_word,count=2)
                #ovv_word_reduced = tools.get_reduced_alt(ovv_word) or ovv_word
                ovv_word_digited = tools.replace_digits(ovv_word_reduced)
                lo_candidates.append([(ovv_word_digited,ovv_tag),keys,score_matrix])
            elif word[1] == "OOV":
                lo_candidates.append([(word[0],ovv_tag),[word[0]],
                                      [[[numpy.array([    9.93355,  4191.     ]), 'new|A'],
                                        [numpy.array([  1.26120000e+00,   4.19100000e+03]), 'pix|N']]]
                                  ])
    return lo_candidates


    '''
            if trans.__class__ == str:
                ovv_word = ovv_word.replace(m.group(0),trans)
            else:
                transes = [ovv_word.replace(m.group(0),t) for t in trans]
                transes_scored = [(t,tools.get_node(t)[0]['freq'] if tools.get_node(t) else 0) for (t in transes]
                transes_scored.sort(key=lambda x: x[1])
                ovv_word = transes_scored[-1][0]
    '''
