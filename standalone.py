import normalizer
from analysis import ext_contextual_candidates, add_slangs, add_from_dict, add_nom_verbs, iter_calc_lev,show_results, calculate_score, filter_and_sort_candidates
from conf import SLANG, database, window_size, distance, max_val

def norm_one(tweet, oov_index):
    database = 'tweets2'
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
