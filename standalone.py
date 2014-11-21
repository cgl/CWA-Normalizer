import normalizer
from analysis import database,SLANG,window_size, ext_contextual_candidates, add_slangs, add_from_dict, add_nom_verbs, iter_calc_lev,show_results

def norm_one(tweet, oov_index, distance = 2,slang_threshold=1,max_val = [1., 1., 0.5, 0.0, 1.0, 0.5],):
    norm = normalizer.Normalizer([tweet],database=database)
    norm.m = window_size/2
    contextual_candidates = ext_contextual_candidates(tweet,oov_index,norm)
    fms = add_slangs([contextual_candidates],SLANG)
    mapp = [[tweet[oov_index][0],None,tweet[oov_index][1]]]
    not_oov = ['' for _ in mapp ]  # bos_oov
    fmd = add_from_dict(fms,[contextual_candidates],distance,not_oov)
    fm_reduced = add_nom_verbs(fmd,mapp,slang_threshold=slang_threshold)
    feat_mat = iter_calc_lev([contextual_candidates],fm_reduced,not_oov)
    return feat_mat
