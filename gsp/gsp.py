import operator
import itertools
import sys
import string
import re
import cPickle as pickle
from check_candidates import check_candidates, check_reduced_candidates, create_alt
from sequence import nthitem, sequence_get, contiguous_subsequences, extended_data_sequence, sequence_len
from hash_tree import create_hash_tree

def predecessors(taxonomy, item):
    """
    >>> taxonomy = {1: [7], 4: [8], 7: [10], 2: []}
    >>> predecessors(taxonomy, 1) == set([7,10])
    True
    >>> predecessors(taxonomy, 4) == set([8])
    True
    >>> predecessors(taxonomy, 7) == set([10])
    True
    >>> predecessors(taxonomy, 10) == set([])
    True
    >>> taxonomy = {1: [7], 4: [8,7], 7: [10]}
    >>> predecessors(taxonomy, 1) == set([7,10])
    True
    >>> predecessors(taxonomy, 4) == set([8,7,10])
    True
    >>> predecessors(taxonomy, 7) == set([10])
    True
    >>> predecessors(taxonomy, 10) == set([])
    True
    >>> predecessors(taxonomy, 2) == set([])
    True
    """
    if item in taxonomy:
        return (set(taxonomy[item])
               | reduce(set.union, (predecessors(taxonomy, parent_item)
                                    for parent_item in taxonomy[item]), set()))
    else:
        return set()

def transformed_taxonomy(taxonomy):
    """
    >>> taxonomy = {1: [7], 4: [8], 7: [10], 8: [10]}
    >>> transformed_taxonomy(taxonomy) == {1: set([1,7,10]), 4: set([4,8,10])}
    True
    >>> taxonomy = {1: [7], 4: [8,7], 7: [10], 8: [10]}
    >>> transformed_taxonomy(taxonomy) == {1: set([1,7,10]), 4: set([4,7,8,10])}
    True
    >>> taxonomy = {1: [7], 4: [8,7], 7: [10], 8: [10], 2: []}
    >>> transformed_taxonomy(taxonomy) == {1: set([1,7,10]), 4: set([4,7,8,10]), 2: set([2])}
    True
    """
    if taxonomy is None:
        return None

    transformed_taxonomy = dict()

    for item in set(taxonomy) - set(reduce(operator.add, taxonomy.values())):
        transformed_taxonomy[item] = set([item]) | predecessors(taxonomy, item)

    return transformed_taxonomy


def powerset(iterable):
    """
    >>> set(powerset([1,2,3])) == set([(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)])
    True
    """

    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


def close_ancestors(taxonomy, sequence):
    """
    >>> taxonomy = {2: [20], 3: [30], 4: [40]}
    >>> close_ancestors(taxonomy, (frozenset([2,3]),frozenset([4]))) == set([(frozenset([3, 20]), frozenset([4])), (frozenset([2, 30]), frozenset([4])), (frozenset([2, 3]), frozenset([40])), (frozenset([20, 30]), frozenset([4])), (frozenset([3, 20]), frozenset([40])), (frozenset([2, 30]), frozenset([40])), (frozenset([20, 30]), frozenset([40]))])
    True
    >>> taxonomy = {2: [20], 3: [30,300], 4: [40]}
    >>> close_ancestors(taxonomy, (frozenset([2,3]),frozenset([4]))) == set([(frozenset([3, 20]), frozenset([4])), (frozenset([2, 30]), frozenset([4])), (frozenset([2, 300]), frozenset([4])), (frozenset([2, 3]), frozenset([40])), (frozenset([20, 30]), frozenset([4])), (frozenset([20, 300]), frozenset([4])), (frozenset([3, 20]), frozenset([40])), (frozenset([2, 30]), frozenset([40])), (frozenset([2, 300]), frozenset([40])),(frozenset([20, 30]), frozenset([40])), (frozenset([20, 300]), frozenset([40]))])
    True
    >>> close_ancestors(taxonomy, (frozenset([2,4]),frozenset([5]))) == set([(frozenset([20,4]), frozenset([5])), (frozenset([2,40]), frozenset([5])), (frozenset([20,40]), frozenset([5]))])
    True
    >>> taxonomy = {2: [20], 3: [20], 4: [40]}
    >>> close_ancestors(taxonomy, (frozenset([2,3]),frozenset([4]))) == set([(frozenset([3, 20]), frozenset([4])), (frozenset([2, 20]), frozenset([40])), (frozenset([3, 20]), frozenset([40])), (frozenset([2, 20]), frozenset([4])), (frozenset([2, 3]), frozenset([40]))])
    True
    """
    transformed_itemset = lambda itemset: itertools.product(*([item] + (taxonomy[item] if item in taxonomy else []) for item in itemset))
    transformed_sequences = (map(frozenset, transformed_itemset(itemset)) for itemset in sequence)
    close_ancestors = (close_ancestor for close_ancestor in itertools.product(*transformed_sequences) if close_ancestor != sequence and sequence_len(close_ancestor) == sequence_len(sequence))
    return set(close_ancestors)


def unique_items(candidates):
    unique_items = set()
    for sequence in candidates:
        for itemset in sequence:
            for item in itemset:
                unique_items.add(item)
    return unique_items


def both_item_and_ancestor(taxonomy, sequence):
    """
    >>> taxonomy = {1: [7], 4: [8], 7: [10]}
    >>> sequence = (frozenset([1]), frozenset([1]))
    >>> both_item_and_ancestor(taxonomy, sequence)
    False
    >>> sequence = (frozenset([1,8]), frozenset([7,10]))
    >>> both_item_and_ancestor(taxonomy, sequence)
    True
    >>> sequence = (frozenset([1,4]), frozenset([7,4,10]))
    >>> both_item_and_ancestor(taxonomy, sequence)
    True
    >>> sequence = (frozenset([1,4]), frozenset([4,10]))
    >>> both_item_and_ancestor(taxonomy, sequence)
    False
    """
    item_combinations = (itertools.product(itemset, repeat=2) for itemset in sequence)
    return any(item1 in predecessors(taxonomy, item2) for item1, item2 in itertools.chain.from_iterable(item_combinations) if item1 is not item2)


def sequence_to_string(sequence):
    return "<{" + "} {".join(" ".join(map(repr, itemset)) for itemset in sequence) + "}>"


# calculate expected support among close ancestors
def expected_support(support_count, sequence, close_ancestor):
    if close_ancestor not in support_count:
        return 0.0
    return support_count[close_ancestor] * reduce(operator.mul,
           [support_count[(frozenset([nthitem(sequence, i)]),)]
            / float(support_count[(frozenset([nthitem(close_ancestor, i)]),)])
            for i in range(sequence_len(sequence))])

def join_sequences(sequence, item, separate, iteration, Ck):
    # join sequences s1 and s2
    # The candidate sequence generated by joining 1 with 2 is the sequence
    # 1 extended with the last item in 2. The added item becomes a separate
    # itemset if it was a separate itemset in 2, and part of the last itemset of
    # 1 otherwise.

    if separate or iteration == 1:
        Ck.add(sequence + (frozenset([item]), ))

    if item not in sequence[-1] and (not separate or iteration == 1):
        Ck.add(sequence[:-1] + (sequence[-1] | frozenset([item]), ))

def extend_database(database, taxonomy):
    if taxonomy:
        return [extended_data_sequence(transformed_taxonomy(taxonomy),data_sequence) for data_sequence in database]
    else:
        return database

def gsp(database, min_support, taxonomy = None, min_gap = 0, max_gap = float("inf"), window_size = 0, min_interest = 0, hash_tree_threshold = 0, memory_efficient = False, continue_file = None):
    """
        Returns a dictionary with frequent_sequences as keys, and 3-tuples as values. The 3-tuples consist of: support count, partial expected support, total expected support. The latter two values are only meaningful when taxonomy is not None.

        The partially expected support is the minimum expected support among close ancestors. A sequence's support has to be R-bigger than this value to be partially interesting.
        The total expected support is the maximum expected support among close ancestors. A sequence's support has to be R-bigger than this value to be (totally) interesting.)
    """

    # extend the database with the taxonomy
    database = extend_database(database, taxonomy)

    # populating L[0]
    support_count = dict()
    interest_support = dict()
    for data_sequence in database:
        for item in reduce(frozenset.union, (itemset for time, itemset in data_sequence)):
            sequence = (frozenset([item]), )
            if sequence not in support_count:
                support_count[sequence] = 1
            else:
                support_count[sequence] += 1
            interest_support[sequence] = (0.0,0.0)

    Lprev = set(sequence for sequence in support_count if sequence_len(sequence) == 1 and support_count[sequence] >= min_support)
    iteration = 1
    do_not_return_iteration = False
    # enable to continue with existing file
    if continue_file:
        match = re.match('.*?(\d{3})\.dat', continue_file)
        if match:
            iteration = int(match.group(1))

            frequent_sequences = pickle.load(open(continue_file,'rb'))

            Lprev = set(frequent_sequence[0] for frequent_sequence in frequent_sequences['sequences'])

            min_support  = frequent_sequences['min_support']
            max_gap  = frequent_sequences['max_gap']
            min_interest = frequent_sequences['min_interest']

            do_not_return_iteration = True

            print "continuing with " + continue_file

    while True:
        if __debug__:
            print "->",len(Lprev), "(%d)" % iteration

        # yield all sequences in Lprev, with support_count[sequence] and interest_support[sequence]
        if not do_not_return_iteration:
            for sequence in Lprev:
                if sequence not in interest_support:
                    interest_support[sequence] = (0.0,0.0)
                yield (sequence, support_count[sequence]) + interest_support[sequence]
            if memory_efficient:
                yield None
        else:
            do_not_return_iteration = False

        # clear useless values, but keeping support_count for 1-sequences for interest measure application
        support_count = {sequence: support_count[sequence] for sequence in support_count if sequence_len(sequence) == 1}
        interest_support.clear()

        # generate candidates: join-phase
        Ck = set()
        s1s = dict()
        s2s = dict()
        counter = 0
        skip = max(1, int((len(Lprev)+1) / 100))
        for sequence in Lprev:
            s2 = tuple(reduce(operator.add, (sorted(itemset) for itemset in sequence)))
            s1 = s2[1:]
            last_item = s2[-1]
            s2 = s2[:-1]

            if s1 not in s1s:
                s1s[s1] = list()
            s1s[s1].append(sequence)
            if s1 in s2s:
                for item,separate in s2s[s1]:
                        join_sequences(sequence, item, separate, iteration, Ck)

            if s2 not in s2s:
                s2s[s2] = list()
            s2s[s2].append((last_item, len(sequence[-1]) == 1))
            if s2 in s1s:
                for sequencea in s1s[s2]:
                        join_sequences(sequencea, last_item, len(sequence[-1]) == 1, iteration, Ck)
            if counter % skip == 0:
                sys.stdout.write(".")
            counter += 1
        s1s.clear()
        s2s.clear()
        print


        # generate candidates: prune-phase
        Ck = list(sequence for sequence in Ck if (taxonomy is None or not both_item_and_ancestor(taxonomy, sequence)) and all(subsequence in Lprev for subsequence in contiguous_subsequences(sequence, -1)))

        Lprev = []

        if __debug__:
            print len(Ck)

        # count candidates
        unique_items_ck = unique_items(Ck)
        if hash_tree_threshold > 0:
            hash_tree = create_hash_tree(Ck, hash_tree_threshold)
            #Ck = []
        for data_sequence in database:
            # filter out items that are not in unique_items(Ck2) from the data_sequence
            data_sequence = [(time, filter(lambda x: x in unique_items_ck, itemset)) for time, itemset in data_sequence]
            alt_data_sequence = create_alt(data_sequence)
            if hash_tree_threshold > 0:
                for sequence in set(check_reduced_candidates(alt_data_sequence, hash_tree, min_gap, max_gap, window_size)):
                    if sequence not in support_count:
                        support_count[sequence] = 1
                    else:
                        support_count[sequence] += 1
            else:
                for sequence in Ck:
                    if check_candidates(alt_data_sequence, sequence, min_gap, max_gap, window_size):
                        if sequence not in support_count:
                            support_count[sequence] = 1
                        else:
                            support_count[sequence] += 1
            sys.stdout.write(".")
        print
        Lk = set(sequence for sequence in support_count if sequence_len(sequence) > iteration and support_count[sequence] >= min_support)
        unique_items_ck.clear()

        # apply interest measure
        Lk2 = Lk
        if taxonomy and min_interest > 0:
            Lk2 = set()
            for sequence in Lk:

                expected_supports = [expected_support(support_count, sequence, close_ancestor)
                                     for close_ancestor in close_ancestors(taxonomy, sequence)]

                # check if the sequence is interesting enough based on min_interest
                if not expected_supports or support_count[sequence] > float(min_interest) * min(expected_supports):
                    Lk2.add(sequence)
                    interest_support[sequence] = (min(expected_supports), max(expected_supports)) if expected_supports else (0.0,0.0)

        # if there are any new sequences found in this iteration, add them to L, otherwise terminate
        if Lk2:

            # set Lprev to Lk2
            Lprev = Lk2
            iteration+=1
        else:
            break

if __name__ == "__main__":
    database = [[(1, frozenset(['Ringworld'])),
                 (2, frozenset(['Foundation'])),
                 (15, frozenset(['Ringworld Engineers', 'Second Foundation']))
                ],
                [(1, frozenset(['Foundation', 'Ringworld'])),
                 (20, frozenset(['Foundation and Empire'])),
                 (50, frozenset(['Ringworld Engineers']))
                ],
                [(5, frozenset(['Foundation', 'Ringworld'])),
                 (10, frozenset(['Foundation and Empire']))
                ]]

    taxonomy = {'Foundation': ['Asimov'],
                'Foundation and Empire': ['Asimov'],
                'Second Foundation': ['Asimov'],
                'Ringworld': ['Niven'],
                'Ringworld Engineers': ['Niven']}

    min_support = 2
    min_gap = 0
    max_gap = 10000
    window_size = 0
    min_interest = 0    # only meaningful when not 0 and taxonomy is not None
    hash_tree_threshold = 0

    sequences = sorted(gsp(database, min_support, taxonomy, min_gap, max_gap, window_size, min_interest, hash_tree_threshold), key=lambda sequence: sequence[1:], reverse=True)
    #for sequence in gsp(database, min_support, taxonomy, min_gap, max_gap, window_size, min_interest, hash_tree_threshold):
    #    print sequence[1:], sequence_to_string(sequence[0]), "(%d)" % sequence_len(sequence[0])
    print "(%d sequences)" % len(sequences)
