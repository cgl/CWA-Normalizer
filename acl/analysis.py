import codecs,sys
try:
    import ujson as json
except ImportError:
    import json
from main.conf import ovv_fun_60_filtered_extended as EMNLP_fun
from multi_norm_acl import get_dict

def oov_detection_performance(training,results):
    scowl_words = get_dict()
    is_oov_lex = lambda x,y,z : True if x.lower() not in scowl_words else False
    not_detected = []
    total_norm = 0.0
    total_nsw = 0.0
    for pred, tra in zip(results, training):
        input = tra['input']
        output = tra['output']
        norms = pred['output']
        for ind in range(len(input)):
            if input[ind].lower() != output[ind].lower() and input[ind].strip():
                if is_oov_lex(input[ind],_,_):
                    total_norm += 1
                else:
                    not_detected.append(input[ind])
                total_nsw +=1
    sys.stdout.write("total_norm: %s\ntotal_nsw: %s\n" %(total_norm,total_nsw))


def process_training_file(training_filename):
    with codecs.open(training_filename,"r","utf-8") as file:
        training = json.load(file)
    return training

def process_res_file(res_filename):
    with codecs.open(res_filename,"r","utf-8") as file:
        results = json.load(file)
    return results

def main():
    parser = argparse.ArgumentParser(description = "Analysis scripts for LexNorm in W-NUT 2015")
    parser.add_argument("--pred", required = True, help = "A JSON file: Your predictions over test data formatted in JSON as training data")
    parser.add_argument("--oracle", required = True, help = "A JSON file: The oracle annotations of test data formatted in JSON as training data")
    args = parser.parse_args()

    predicates = json.load(open(args.pred))
    training_list = json.load(open(args.pred))
    oov_detection_performance(training_list,predicates)

if __name__ == "__main__":
    main()
