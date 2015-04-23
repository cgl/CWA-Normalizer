import conf, standalone, time, analysis,operator
from data import han
import tools

ANNOTATED = standalone.construct_annotated(han.POS_TAGGED, han.RESULTS, conf.OOVFUNC)
ANNOTATED01 = standalone.construct_annotated(han.POS_TAGGED[0:1], han.RESULTS[0:1], conf.OOVFUNC)
#ANNOTATED05 = standalone.construct_annotated(han.POS_TAGGED[0:5],
#                                             han.RESULTS[0:5], conf.OOVFUNC)
#ANNOTATED010 = standalone.construct_annotated(han.POS_TAGGED[0:10],
#                                             han.RESULTS[0:10], conf.OOVFUNC)
#ANNOTATED0100 = standalone.construct_annotated(han.POS_TAGGED[0:100],
#                                              han.RESULTS[0:100], conf.OOVFUNC)
#ANNOTATED0200 = standalone.construct_annotated(han.POS_TAGGED[0:200],
#                                              han.RESULTS[0:200], conf.OOVFUNC)

# ord549 = snippets.ordered(0,549)

# unord549 = snippets.un_ordered(0,549)

def all_ordered():
    return all_un_ordered(is_ordered=True)

def all_un_ordered(is_ordered=False):
    start = time.time()
    lo_tweets,evl = standalone.norm_all(ANNOTATED,is_ordered)
    end = time.time()
    print("Time: %d" %(end - start))
    return lo_tweets,evl

def ordered(i,j):
    lo_tweets,evl = standalone.norm_all(ANNOTATED[i:j],True)
    return lo_tweets,evl

def un_ordered(i,j):
    lo_tweets,evl = standalone.norm_all(ANNOTATED[i:j],False)
    return lo_tweets,evl

def run(i,j):
    start = time.time()
    if i == 9 and j == 9:
        setcurrent = analysis.run([],[],[],None)
    else:
        setcurrent = analysis.run([],[],[],None,
                                  pos_tagged = han.POS_TAGGED[i:j],
                                  results = han.RESULTS[i:j])
    end = time.time()
    print("Time: %d" %(end - start))
    return setcurrent

def oov_statistics(lo_tweets):
    print('%-15s %2s %2.2s %-15s %5s %4s %3s %-15s' %('Oov','Tag','Index','Answer','Cont. Cands',
                                                       'Lexical Cands','Filt Cands','Canonical'))
    for tweet in lo_tweets:
        for oov in tweet.oov_tokens:
            oov.__details__()

# Lists the frequencies of the tags in the lo_tweets given
def tag_statistics(lo_tweets):
    corrects = {'N':0, 'V':0, 'A':0, '!':0, 'P':0, 'G':0, 'L':0, '^':0, 'D':0, '$':0, 'T':0,
                '&':0, ',':0, 'R':0, 'X':0, '~':0, 'O':0, 'Z':0, 'E':0}
    incorrects = {'N':0, 'V':0, 'A':0, '!':0, 'P':0, 'G':0, 'L':0, '^':0, 'D':0, '$':0, 'T':0,
                  '&':0, ',':0, 'R':0, 'X':0, '~':0, 'O':0, 'Z':0, 'E':0}
    no_answer = {'N':0, 'V':0, 'A':0, '!':0, 'P':0, 'G':0, 'L':0, '^':0, 'D':0, '$':0, 'T':0,
                 '&':0, ',':0, 'R':0, 'X':0, '~':0, 'O':0, 'Z':0, 'E':0}
    for tweet in lo_tweets:
        for oov in tweet.oov_tokens:
            if oov.answer is '':
                no_answer[oov.oov_tag] += 1
            elif oov.canonical.lower() ==  oov.answer:
                corrects[oov.oov_tag] += 1
            else:
                incorrects[oov.oov_tag] += 1
    sorted_corr = sorted(corrects.items(), key=operator.itemgetter(1),reverse=True)
    print(' ','| ','%-3s' %'Corr','%-3s' %'Inc', '%-3s' %'No', '%-3s' %'Tot')
    for (tag,freq) in sorted_corr:
        print(tag,': ','%-3d' %freq,'%-3d' %incorrects[tag],'%-3d' %no_answer[tag],
              '%-3d' %(freq+incorrects[tag]+no_answer[tag]))

# lambda x: x[-1] == 'IV'
def neighbours(lo_tweets):
    i = 0
    fun = lambda x: x[1] not in conf.NA_TAGS
    fun_IV = lambda x: x[-1] == 'IV'
    fun_OOV = lambda x: x[-1] == 'OOV'
    print("%-4s %s \t %s \t %s \t %s \t %s \t %s" %("TID","ANS","CONT","#IV","#OOV","T_LEN","T_#OOV"))
    for ind,tweet in enumerate(lo_tweets):
        tweet_len = len(filter(fun, tweet.normalization))
        tweet_oov_count = len(filter(lambda x: x[0] != x[2] , tweet.normalization))
        for oov in tweet.oov_tokens:
            result = oov.answer
            cont_answer = '-'
            iv_count = len(filter(fun_IV, oov.neighbours))
            oov_count = len(filter(fun_OOV, oov.neighbours))
            neigh_count = len(oov.neighbours)
            if not result is '':
                result = oov.answer.lower() == oov.canonical.lower()
                cont_answer = oov.score_mat[0][1] != 0.0
            print("%-4d %s \t %s \t %d \t %d \t %d \t %d \t %d" %(ind, '-' if result is '' else result,cont_answer,iv_count,oov_count,neigh_count,tweet_len,tweet_oov_count))


def performance(evl):
    correct = len(evl['correct_answers'])
    #evl['correctly_unchanged']
    incorrect = len(evl['incorrect_answers'])
    num_of_words_req_norm = evl['num_of_words_req_norm']
    fp = len(evl['incorrectly_corrected_word'])
    print(correct,incorrect,fp,num_of_words_req_norm)
    tools.get_performance(correct,incorrect,fp,num_of_words_req_norm)

def compare(lo_tweets_1,lo_tweets_2):
    for ind in range(0,549):
        for oov_ind in range(0,len(lo_tweets_1[ind].oov_tokens)):
            if lo_tweets_1[ind].oov_tokens[oov_ind].answer != lo_tweets_2[ind].oov_tokens[oov_ind].answer:
                print(ind,oov_ind,'[',lo_tweets_1[ind].oov_tokens[oov_ind].canonical,']',lo_tweets_1[ind].oov_tokens[oov_ind].answer or "-", lo_tweets_2[ind].oov_tokens[oov_ind].answer or "-")
