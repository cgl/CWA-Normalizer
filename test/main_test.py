from main.tools import parseTweet, spell_check
from main import standalone
import sys
from main.conf import is_ill, is_oov, spell, ovv_fun_20_filtered_extended as EMNLP_fun
"""
Main test function
Required exports:
export PYTHONPATH=/home/cagil/repos/CWA-Normalizer:/home/cagil/repos/virtuals/movvie/lib/python2.7/site-packages/febrl-0.4.2/
/Users/cagil/virtuals/CWA2/src/febrl

see install.txt
"""

def main(argv):
    test_tagger()
    test_oov_detection(is_ill,is_oov)
    test_oov_detection(spell,EMNLP_fun)
    test_normalization()
    sys.stdout.write("All tests passed :)\n")

def test_tagger():
    text = u'You better txt me if you really need smthin'
    parse_tools = parseTweet(text)
    try:
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
    text = u'You better txt me if you really need smthin'
    norm_obj = standalone.main(text,oov_fun=spell)
    normalized = [token[0] for token in norm_obj.normalization]
    result = ['You', 'better', 'text', 'me', 'if', 'you', 'really', 'need', 'something']
    try:
        assert(normalized == result)
        assert(norm_obj.__repr__().lower().strip() == 'You better [txt] me if you really need [smthin]'.lower())
    except AssertionError:
        print("[Error] normalization not working properly")
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
