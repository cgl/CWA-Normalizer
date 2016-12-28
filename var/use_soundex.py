import Levenshtein
import soundex

def soundex_distance(ovv_snd,cand):
    try:
        lev = Levenshtein.distance(unicode(ovv_snd),soundex.soundex(cand.decode("utf-8","ignore")))
    except UnicodeEncodeError:
        print('UnicodeEncodeError[ovv_snd]: %s %s' % (ovv_snd,cand))
        lev = Levenshtein.distance(ovv_snd,soundex.soundex(cand.encode("ascii","ignore")))
    except UnicodeDecodeError:
        print('UnicodeDecodeError[ovv_snd]: %s %s' % (ovv_snd,cand))
        lev = Levenshtein.distance(ovv_snd,soundex.soundex(cand.decode("ascii","ignore")))
    except TypeError:
        print ('TypeError[ovv_snd]: %s %s' % (ovv_snd,cand))
        lev = 10.
    snd_dis = lev
    return snd_dis
