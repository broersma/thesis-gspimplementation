# add relative module folders to sys.path
import os, sys, inspect
module_folders = ["../database", "../gsp"]
for module_folder in module_folders:
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], module_folder)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

import cPickle as pickle
import gsp
import grammar_taxonomy
import argparse

def get_cached_database(filename):
    key = 'conversation_database'
    database = None
    with open(filename,'rb') as file:
        wrapper = pickle.load(open(filename,'rb'))
        database = wrapper[key]
    return database

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate sequential patterns from a database")
    parser.add_argument("input", help="database input file")
    parser.add_argument("output", help="sequences output file")
    parser.add_argument("-s", "--min_support", help="minimum support count", type=int, default=10)      # scales linearly, larger = shorter, finds less
    parser.add_argument("-i", "--min_gap", help="minimum gap size", type=int, default=0)                # ???, larger = ???
    parser.add_argument("-x", "--max_gap", help="maximum gap size", type=int, default=1)                # ???, larger = longer, finds more
    parser.add_argument("-n", "--min_interest", help="minimum interest value", type=float, default=1.0) # ???, larger = shorter, finds less
    parser.add_argument("-y", "--no_taxonomy", help="do not use a taxonomy", action="store_true")
    parser.add_argument("-w", "--window_size", help="window size", type=int, default=0)                 # ???, larger = ???
    parser.add_argument("-t", "--hash_tree_threshold", help="hash tree threshold", type=int, default=2) # 2 or larger seems to result in nice speedups
    parser.add_argument("-m", "--memory-efficient", dest="memory_efficient", help="try to use as less memory as possible", action="store_true")
    parser.add_argument("-c", "--continue_file", help="continue with file (overrides GSP parameters)")
    args = parser.parse_args()

    import pprint
    pp = pprint.PrettyPrinter(indent=4, depth=5, width=100)

    database = get_cached_database(args.input)
    #pp.pprint(database)

    if args.no_taxonomy:
        taxonomy = None
    else:
        utterance_taxonomy = grammar_taxonomy.get_taxonomy()
        #pp.pprint(taxonomy)
        taxonomy = dict()
        for child,parents in utterance_taxonomy.items():
            taxonomy[child] = [parent for parent in parents if parent[1] != 'utterance']

    sequence_counter = 0
    if args.memory_efficient:
        sequences = list()
        file_counter = 1
        for sequence in gsp.gsp(database, args.min_support, taxonomy, args.min_gap, args.max_gap, args.window_size, args.min_interest, args.hash_tree_threshold, memory_efficient = True):
            if sequence is None:
                pickle.dump({'min_support': args.min_support,
                             'max_gap': args.max_gap,
                             'min_interest': args.min_interest,
                             'sequences': sequences}, open(args.output + '{:03d}'.format(file_counter) + '.dat', 'wb'))
                sequences = list()
                file_counter += 1
            else:
                sequences.append(sequence)
                sequence_counter += 1
            
    else:
        sequences = list(gsp.gsp(database, args.min_support, taxonomy, args.min_gap, args.max_gap, args.window_size, args.min_interest, args.hash_tree_threshold, continue_file = args.continue_file))

        pickle.dump({'min_support': args.min_support,
                     'max_gap': args.max_gap,
                     'min_interest': args.min_interest,
                     'sequences': sequences}, open(args.output, 'wb'))
        sequence_counter = len(sequences)

    if __debug__:
        print "%d sequences, min_support=%d, max_gap=%d, min_interest=%f" % (sequence_counter, args.min_support, args.max_gap, args.min_interest)

    """
    from timeit import Timer
    import itertools
    #for min_support, max_gap, min_interest,hash_tree_threshold in itertools.product(range(7, 4, -1), range(1, 2), [x/2.5 for x in range(0, 6)],range(2, 4)):
    for max_gap in range(1,5):
            #hash_tree_threshold
            t = Timer("list(gsp.gsp(database, min_support, taxonomy, min_gap, max_gap, window_size, min_interest, hash_tree_threshold))", "from __main__ import gsp, database, min_support, taxonomy, min_gap, max_gap, window_size, min_interest, hash_tree_threshold")
            print min_support, max_gap, min_interest,hash_tree_threshold,
            print "->",t.timeit(number=1)
            if hash_tree_threshold == 3:
                print "-----------------"
    """
