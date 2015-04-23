from scoring import han
import tools
from fuzzy import DMetaphone
import enchant
import CMUTweetTagger

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

def check(results,oov,method):
    for tweet in results:
        for word in tweet:
            if oov(word[0],word[1]):
                method(results,oov)

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

def run_old(matrix1,fmd,feat_mat,slang,not_oov,mapp,results = han.RESULTS,
        pos_tagged = han.POS_TAGGED):
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
