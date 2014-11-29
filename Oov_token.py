import normalizer
from analysis import ext_contextual_candidates, add_slangs, add_from_dict, add_nom_verbs, iter_calc_lev, filter_and_sort_candidates
from conf import SLANG, database, window_size, distance

class Oov_token:
    def __init__(self,oov,ind,tag,canonical,tweet):
        self.oov = oov
        self.oov_tag = tag
        self.oov_ind = ind
        self.canonical = canonical
        self.tweet = tweet
        self.answer = ''
        self.contextual_candidates = []
        self.fms = []
        self.mapp = []
        self.not_oov = []
        self.fmd = []
        self.fm_reduced = []
        self.feat_mat = []
        self.score_mat = []
        self.norm = normalizer.Normalizer([],database)
        self.norm.m = window_size/2

    def norm_one(self):
        tweet = self.tweet.normalization
        self.contextual_candidates = ext_contextual_candidates(tweet,self.oov_ind,self.norm)
        self.fms = add_slangs([self.contextual_candidates],SLANG)
        self.mapp = [[self.oov,None,self.oov_tag]]
        self.not_oov = ['' for a in self.mapp ]  # bos_oov
        self.fmd = add_from_dict(self.fms, [self.contextual_candidates],distance,self.not_oov)
        self.fm_reduced = add_nom_verbs(self.fmd,self.mapp)
        self.feat_mat = iter_calc_lev([self.contextual_candidates],self.fm_reduced,self.not_oov)
        res_dict = self.feat_mat[0]
        self.score_mat = filter_and_sort_candidates(res_dict,self.oov)
        if self.score_mat:
            self.answer = self.score_mat[0][0]

    def __repr__(self):
        return "<Oov Token:%-15s tag:%s canonical:%-15s normalization:%s>" % (self.oov,
                                                                        self.oov_tag,
                                                                        self.canonical,
                                                                        self.answer)

    def __details__(self):
        print('%-15s %2s %2.2s %-15s %5s %4d %3s %-15s' %('Oov','Tag','Index','Answer','Cont. Cands',
                                                       'Lexical Cands','Filt Cands','Canonical'))
        print('%-15s %2s %2.2d %-15s %5d %4d %3d %-15s' %(self.oov,self.oov_tag,
                            self.oov_ind, self.answer or '-',
                            len(self.contextual_candidates[1]),
                            len(self.fmd[0]),
                            len(self.score_mat),
                            '' if self.canonical.lower() ==  self.answer else self.canonical,))
