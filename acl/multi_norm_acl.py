import os,sys,codecs,json
from main import standalone
from evaluation import evaluate
FILEPATH = os.path.dirname(os.path.realpath(__file__))

def main(argv):
    training_filename = FILEPATH +"/train_data_20150413.json"
    res_filename = FILEPATH +'/demo.cwa3.json'
    training,results = process_tra_file(training_filename)
    scowl_words = get_dict()
    if len(argv) >= 1: #test
        sys.stdout.write("Testing with first 10 tweet\n")
        training = training[:10]
        results = results[:10]
        training_filename = write_to_file(training_filename+".test.training",training)
        res_filename = training_filename+".test.results"
    get_norms(scowl_words,training,results)
    write_to_file(res_filename,results)
    sys.stdout.write("Answers written to file\n")
    evaluate(res_filename,training_filename)
    sys.stdout.write("Completed Successfully\n")

def process_tra_file(training_filename):
    with codecs.open(training_filename,"r","utf-8") as file:
        training = json.load(file)
    with codecs.open(training_filename,"r","utf-8") as file:
        results = json.load(file)
    return training,results

def get_dict():
    dic_filename = FILEPATH +"/scowl.american.70"
    scowl_words = []
    with codecs.open(dic_filename, "r","iso-8859-1") as file:
        word = "None"
        try:
            while word:
                word = file.readline()
                scowl_words.append(word.strip())
        except UnicodeDecodeError:
            pass
    return scowl_words

def get_norms(scowl_words,training,results):
    is_oov_lex = lambda x,y,z : True if x.lower() not in scowl_words else False

    is_ill = lambda x,y,z : True if x != z else False
    is_oov = lambda x,y,z : True if y == 'OOV' else False
    spell = lambda x,y,z : not standalone.tools.spell_check(x)

    test_oov_detection(is_ill,is_oov_lex)
    test_oov_detection(is_oov,is_oov_lex)
    test_oov_detection(spell,is_oov_lex)

    for ind in range(0,len(training)):
	calculate_norm(training,results,ind,is_oov_lex)

def calculate_norm(training,results,ind,is_oov_lex):
    norm_obj = standalone.main(" ".join(training[ind]['input']),oov_fun=is_oov_lex)
    results[ind]['output'] = [token[0] for token in norm_obj.normalization]

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

def test_normalization(is_oov_lex):
    text = u'You better txt me if you really need smthin'
    test_training = []
    test_training.append({u'tid': u'471697522197794816', u'index': u'6837', u'input': [u'You', u'better', u'txt', u'me', u'if', u'you', u'really', u'need', u'somthin'], u'output': [u'you', u'better', u'text', u'me', u'if', u'you', u'really', u'need', u'something']})
    test_results = []
    test_results.append({u'tid': u'471697522197794816', u'index': u'6837', u'input': [u'You', u'better', u'txt', u'me', u'if', u'you', u'really', u'need', u'somthin'], u'output': [u'you', u'better', u'text', u'me', u'if', u'you', u'really', u'need', u'something']})
    calculate_norm(test_training,test_results,0,is_oov_lex)
    for word_ind in range(len(test_training[0]['output'])):
        try:
            assert(test_training[0]['output'][word_ind].lower() == test_results[0]['output'][word_ind].lower())
        except AssertionError:
            print("[Error] %s not working properly" "normalization")
            sys.exit(1)

def write_to_file(res_filename,results):
    #if  os.path.exists(res_filename):
    with open(res_filename, 'w') as outfile:
        json.dump(results,outfile)
    return res_filename

if __name__ == '__main__':
    #pool = Pool(processes=4)              # process per core
    #pool.map(process_image, data_inputs)  # proces data_inputs iterable with pool
    main(sys.argv)
#from multiprocessing import Pool

#def process_image(name):
    #sci=fits.open('{}.fits'.format(name))
    #<process>
