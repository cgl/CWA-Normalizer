#!/usr/bin/env python
"""
Evaluation scripts for English Lexical Normalisation shared task in W-NUT 2015.
"""


import sys
import argparse
try:
    import ujson as json
except ImportError:
    import json


def evaluate(pred_file, oracle_file):
    pred_list = json.load(open(pred_file))
    oracle_list = json.load(open(oracle_file))

    correct_norm = 0.0
    total_norm = 0.0
    total_nsw = 0.0
    for pred, oracle in zip(pred_list, oracle_list):
        try:
            assert(pred["tid"] == oracle["tid"])
            input_tokens = pred["input"]
            pred_tokens = pred["output"]
            oracle_tokens = oracle["output"]
            sent_length = len(input_tokens)
            for i in range(sent_length):
                if pred_tokens[i].lower() != input_tokens[i].lower() and oracle_tokens[i].lower() == pred_tokens[i].lower() and oracle_tokens[i].strip():
                    correct_norm += 1
                if oracle_tokens[i].lower() != input_tokens[i].lower() and oracle_tokens[i].strip():
                    total_nsw += 1
                if pred_tokens[i].lower() != input_tokens[i].lower() and pred_tokens[i].strip():
                    total_norm += 1
        except AssertionError:
            print "Invalid data format"
            sys.exit(1)
    # calc p, r, f
    p = correct_norm / total_norm
    r = correct_norm / total_nsw
    print "Evaluating", pred_file
    if p != 0 and r != 0:
        f1 =  (2 * p * r) / (p + r)
        print "precision:", round(p, 4)
        print "recall:   ", round(r, 4)
        print "F1:       ", round(f1, 4)
    else:
        print "precision:", round(p, 4)
        print "recall:   ", round(r, 4)


def main():
    parser = argparse.ArgumentParser(description = "Evaluation scripts for LexNorm in W-NUT 2015")
    parser.add_argument("--pred", required = True, help = "A JSON file: Your predictions over test data formatted in JSON as training data")
    parser.add_argument("--oracle", required = True, help = "A JSON file: The oracle annotations of test data formatted in JSON as training data")
    args = parser.parse_args()

    evaluate(args.pred, args.oracle)


if __name__ == "__main__":
    main()
