from main.tools import parseTweet, spell_check
import sys, CMUTweetTagger, standalone
from conf import is_ill, is_oov, spell, ovv_fun_20_filtered_extended as EMNLP_fun
#is_ill = lambda x,y,z : True if x != z else False
#is_oov = lambda x,y,z : True if y == 'OOV' else False
#spell = lambda x,y,z : not spell_check(x)

def main(argv):
    test_tagger()
    test_oov_detection(is_ill,is_oov)
    test_oov_detection(spell,EMNLP_fun)
    test_normalization()

def test_tagger():
    text = u'You better txt me if you really need smthin'
    parse_org = CMUTweetTagger.runtagger_parse([text,])
    parse_tools = parseTweet(text)
    try:
        assert(len(parse_org[0]) == 9)
        assert(len(parse_tools) == 9)
    except AssertionError:
        print("[Error] CMUTweetTagger Not working check tools.py")
        sys.exit(1)

def test_oov_detection(fun1,fun2):
    try:
        assert(fun1("hello","IV","hello") == False)
        assert(fun1("Hello","IV","Hello") == False)
        assert(fun1("hllo","OOV","hello") == True)
    except AssertionError:
        print("[Error] %s not working properly" %fun1)
        sys.exit(1)
    try:
        assert(fun2("hello","IV","hello") == False)
        assert(fun2("Hello","IV","Hello") == False)
        assert(fun2("hllo","OOV","hello") == True)
    except AssertionError:
        print("[Error] %s not working properly" %fun2)
        sys.exit(1)

def test_normalization():
    text = u'You better txt me if you really need somthin'
    norm_obj = standalone.main(text,oov_fun=spell)
    normalized = [token[0] for token in norm_obj.normalization]
    result = ['You', 'better', 'text', 'me', 'if', 'you', 'really', 'need', 'something']
    try:
        assert(normalized == result)
        assert(norm_obj.__repr__().lower().strip() == 'You better [txt] me if you really need [smthin]'.lower())
    except AssertionError:
        print("[Error] normalization not working properly")
        sys.exit(1)
