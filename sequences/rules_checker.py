# add relative module folders to sys.path
import os, sys, inspect
module_folders = ["../database", "../gsp"]
for module_folder in module_folders:
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], module_folder)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

import operator
import time
import random
import argparse
import cPickle as pickle
from get_conversation_sequences import get_cached_database
from print_conversation_sequences import get_rules
from check_candidates import check_candidates, create_alt
from gsp import extend_database
from grammar_taxonomy import get_taxonomy

def matching_rules(history, rules, max_gap):
    alt_history = create_alt(history)
    for rule in rules:
        if check_candidates(create_alt(history[-len(rule[0])*max_gap:]), rule[0], max_gap = max_gap, min_gap = 0, window_size = 0):
            yield rule

    #return (rule for rule in rules if check_candidates(create_alt(history[-len(rule[0])*max(1,max_gap):]), rule[0], max_gap = max_gap, min_gap = 0, window_size = 0))

def predict(history, rules, max_gap, specificity):
    matches = list(matching_rules(history, rules, max_gap))
    matches = sorted(matches, key=lambda rule: (len(rule[0]), rule[2]), reverse = True) if specificity else sorted(matches, key=lambda rule: rule[2], reverse = True)
    return list(rule[1][0] for rule in matches)

    matches = list((rule[1], rule[2]) for rule in matching_rules(history, rules, max_gap))
    conclusion_confidence = dict()

    conclusion_number = dict()
    for conclusion, confidence in matches:
        if conclusion not in conclusion_confidence:
            conclusion_confidence[conclusion] = 0.0
            conclusion_number[conclusion] = 0
        #  we take the average of the confidence of all rules for each conclusion
        conclusion_confidence[conclusion] += confidence
        conclusion_number[conclusion] += 1

    # sorting, highest confidence first
    conclusions = sorted(conclusion_confidence, key=lambda x: conclusion_confidence[x] / float(conclusion_number[x]), reverse = True)

    return list(conclusion[0] for conclusion in conclusions)

# for the insubset measure, use subsets of specific length
num_ltd_subset_right_range = range(1,11)

def test(data_sequence, rules, max_gap, taxonomy, tp, fp, fn, specificity):
    sub_data_sequence = []
    taxonomy_leafs = set(taxonomy.keys()) - set(reduce(operator.add, taxonomy.values()))
    num_first_right = 0
    num_last_right = 0
    num_subset_right = 0
    num_ltd_subset_right = dict()
    for i in num_ltd_subset_right_range:
        num_ltd_subset_right[i] = 0
    num_not_none = 0
    num_predictions = 0
    for element in data_sequence:
        if all(item[0] == 1 for item in element[1]):
            expected = frozenset(item for item in element[1] if item in taxonomy_leafs)

            if expected not in tp:
                tp[expected] = 0
            if expected not in fp:
                fp[expected] = 0
            if expected not in fn:
                fn[expected] = 0

            predictions = predict(sub_data_sequence, rules, max_gap, specificity)
            if predictions:

                num_not_none += 1

                first_prediction = predictions[0]

                if first_prediction not in tp:
                    tp[first_prediction] = 0
                if first_prediction not in fp:
                    fp[first_prediction] = 0
                if first_prediction not in fn:
                    fn[first_prediction] = 0

                if expected == first_prediction:
                    num_first_right += 1
                    tp[first_prediction] += 1
                else:
                    fp[first_prediction] += 1
                    fn[expected] += 1

                if expected <= reduce(frozenset.union, predictions, frozenset()):
                    num_subset_right += 1

                for i in num_ltd_subset_right_range:
                    if expected <= reduce(frozenset.union, predictions[:i], frozenset()):
                        num_ltd_subset_right[i] += 1

            # remove rules from rules
            #if prediction:
            #    rules = list(rule for rule in rules if rule[1][0] != prediction[-1])
            #print len(rules)

            #print ">",sub_data_sequence[-1][1]
            #print "<",expected
            #print "c", predictions, reduce(frozenset.union, predictions, frozenset())
            #print
            num_predictions+=1
        sub_data_sequence.append(element)
    return num_first_right, num_subset_right, num_ltd_subset_right, num_not_none, num_predictions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--specificity", help="use specificity to sort matching rules", action="store_true")
    parser.add_argument("database", help="database input file")
    parser.add_argument("sequences", nargs='+', help="sequences input files to use for printing sequences")
    args = parser.parse_args()

    print "#seq\t#rules\tsupp\tgap\tfirst\tsubset\tnotnone\ttotal\tpr+\trc+\tpr-\trc-\t" + "\t".join(map(str, num_ltd_subset_right_range))
    for sequence_file in args.sequences:
        frequent_sequences = pickle.load(open(sequence_file,'rb'))

        sequences = frequent_sequences['sequences']
        min_support  = frequent_sequences['min_support']
        max_gap  = frequent_sequences['max_gap']
        min_interest = frequent_sequences['min_interest']
        #print "num sequences",len(sequences)

        taxonomy = get_taxonomy()

        database = get_cached_database(args.database)
        database = extend_database(database,taxonomy)
        #print "num data-sequences",len(database)

        rules = get_rules(sequences)
        #print "num rules",len(rules)

        total_num_first_right = total_num_subset_right = total_num_not_none = total_num_predictions = 0
        total_num_ltd_subset_right = dict()
        for i in num_ltd_subset_right_range:
            total_num_ltd_subset_right[i] = 0
        tp = dict()
        fp = dict()
        fn = dict()
        for i in range(0, len(database)):
            num_first_right, num_subset_right, num_ltd_subset_right, num_not_none, num_predictions = test(database[i], rules, max_gap, taxonomy, tp, fp, fn, args.specificity)
            #print i, num_first_right, num_subset_right, num_predictions
            total_num_first_right += num_first_right
            total_num_subset_right += num_subset_right
            for j in num_ltd_subset_right_range:
                total_num_ltd_subset_right[j] += num_ltd_subset_right[j]
            total_num_not_none += num_not_none
            total_num_predictions += num_predictions

        # calculate macro average precision and recall
        precision_sum = 0.0
        recall_sum = 0.0
        n = 0
        for element in tp:
            n+=1
            precision_sum += float(tp[element]) / float( tp[element] + fp[element]) if tp[element] else 0.0
            recall_sum += float(tp[element]) / float( tp[element] + fn[element] ) if tp[element] else 0.0
        precision_macro = precision_sum / n
        recall_macro = recall_sum / n

        # calculate micro average precision and recall
        sum_tp_values = float(sum(tp.values()))
        precision_micro = sum_tp_values / float( sum_tp_values + sum(fp.values()) )
        recall_micro = sum_tp_values / float( sum_tp_values + sum(fn.values()) )

        print "\t".join(map(str, [len(sequences), len(rules), min_support, max_gap, total_num_first_right, total_num_subset_right, total_num_not_none, total_num_predictions, '%.4f' % precision_macro, '%.4f' % recall_macro, '%.4f' % precision_micro, '%.4f' % recall_micro] + total_num_ltd_subset_right.values()))
