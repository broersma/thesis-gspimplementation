import collections
import functools
import sys

def create_alt(data_sequence):

    # make an alternative representation of data_sequence
    alt_data_sequence = dict()
    for time, element in data_sequence:
        for item in element:
            if item not in alt_data_sequence:
                alt_data_sequence[item] = list()
            alt_data_sequence[item].append(time)
    # sort the times for each item
    alt_data_sequence = {item: sorted(alt_data_sequence[item]) for item in alt_data_sequence}
    return alt_data_sequence

# fixture for doctests
data = [(10, frozenset([1, 2])),
        (25, frozenset([4, 6])),
        (45, frozenset([3])),
        (50, frozenset([1, 2])),
        (65, frozenset([3])),
        (90, frozenset([2, 4])),
        (95, frozenset([6]))]
data_alt = create_alt(data)


def _iter_items(data_sequence):
    """
    >>> list(_iter_items(data))
    [(10, 1), (10, 2), (25, 4), (25, 6), (45, 3), (50, 1), (50, 2), (65, 3), (90, 2), (90, 4), (95, 6)]
    """
    for time, element in data_sequence:
        for item in element:
            yield time, item


def item_t(data_alt, item, min_t):
    """
    >>> item_t(data_alt, 1, 0)
    10
    >>> item_t(data_alt, 1, 10)
    10
    >>> item_t(data_alt, 1, 20)
    50
    """
    for t in data_alt[item]:
        if t >= min_t:
            return t
    return None

def _find_element(data_alt, element, window_size, min_t):
    """
    procedure to see if an element exists in the data_sequence
    which is transformed to an alternate representation
    after time min_t given a certain window_size

    >>> _find_element(data_alt, (1,2), 0, 0)
    (10, 10)
    >>> _find_element(data_alt, (3,), 0, 10)
    (45, 45)
    >>> _find_element(data_alt, (1,2), 0, 15)
    (50, 50)
    >>> _find_element(data_alt, (1,2), 0, 15)
    (50, 50)
    >>> _find_element(data_alt, (3,), 0, 55)
    (65, 65)
    >>> _find_element(data_alt, (4,), 0, 70)
    (90, 90)
    """
    while True:
        ## This:
        #min_times = [item_t(data_alt, item, min_t) for item in element]
        #max_min_times = max(min_times)
        #min_min_times = min(min_times)
        #if None in min_times:
        #   return None
        ## Is optimized as:
        max_min_times = -(sys.maxint-1)
        min_min_times = sys.maxint
        for item in element:
            if item not in data_alt:
                return None
            time = item_t(data_alt, item, min_t)
            if time is None:
                return None
            if time > max_min_times:
                max_min_times = time
            if time < min_min_times:
                min_min_times = time
        ##

        if max_min_times-min_min_times <= window_size:
            return min_min_times, max_min_times

        else:
            min_t = max_min_times - window_size

    return None

def check_candidates(alt_data_sequence, sequence, min_gap, max_gap, window_size):
    """
    >>> check_candidates(data_alt, (frozenset([1,2]),frozenset([3,]),frozenset([4])), 5, 30, 0)
    True
    >>> check_candidates(data_alt, (frozenset([1,2]),frozenset([1,2]),frozenset([1,2])), 5, 30, 0)
    False
    >>> check_candidates(data_alt, (frozenset([1,2]),frozenset([1,2])), 5, 30, 0)
    False
    >>> check_candidates(data_alt, (frozenset([1,2]),frozenset([1,2])), 5, 40, 0)
    True
    >>> check_candidates(data_alt, (frozenset([1,2]),frozenset([1,2])), 1, 0, 0)
    False
    >>> from sequence import contiguous_subsequences
    >>> all(map(lambda seq: check_candidates(data_alt, seq, 0, 1000, 0), contiguous_subsequences((frozenset([1,2]),frozenset([4,6]),frozenset([3]),frozenset([1,2]),frozenset([3]),frozenset([2,4]),frozenset([6])), -5)))
    True
    >>> all(map(lambda seq: not check_candidates(data_alt, seq, 0, 1000, 0), contiguous_subsequences((frozenset([10,20]),frozenset([40,60]),frozenset([30]),frozenset([10,20]),frozenset([30]),frozenset([20,40]),frozenset([60])), -5)))
    True
    >>> check_candidates(data_alt, (frozenset([1,2,4,6]),), 0, 10000, 14)
    False
    >>> check_candidates(data_alt, (frozenset([1,2,4,6]),), 0, 10000, 15)
    True
    >>> check_candidates(data_alt, (frozenset([3,4,6]),), 0, 10000, 19)
    False
    >>> check_candidates(data_alt, (frozenset([3,4,6]),), 0, 10000, 20)
    True
    >>> check_candidates(data_alt, (frozenset([4,6]),frozenset([3])), 0, 10000, 20)
    True
    >>> check_candidates(data_alt, (frozenset([4,6]),frozenset([3])), 0, 10000, 0)
    True
    >>> check_candidates(data_alt, (frozenset([4,6]),frozenset([3,1])), 0, 10000, 0)
    False
    >>> check_candidates(data_alt, (frozenset([4,6]),frozenset([3,1])), 0, 10000, 5)
    True
    """

    t = i = 0
    times = dict()
    len_sequence = len(sequence)
    while 0 <= i < len_sequence:
        found_element = _find_element(alt_data_sequence, sequence[i], window_size, t)
        if found_element is not None:
            times[i] = found_element
            if i == 0 or abs(times[i][1]-times[i-1][0]) <= max_gap:
                # forward phase, + 1 to prevent infinite loop
                t = times[i][1] + min_gap + 1
                i += 1
            else:
                # backward phase
                t = times[i][1] - max_gap
                i -= 1
        else:
            return False

    return True


def _check_reduced_candidates_non_root(hash_tree, alt_data_sequence, min_gap, max_gap, window_size, parent_time):
    # returns only sequences from hash_tree which have elements that occur in data_sequence

    if isinstance(hash_tree, list):
        # leaf node
        for sequence in hash_tree:
            if check_candidates(alt_data_sequence, sequence, min_gap, max_gap, window_size):
                yield sequence
    else:
        # non-leaf node
        for item in alt_data_sequence:
            for time in alt_data_sequence[item]:
                if item in hash_tree and (parent_time - window_size) <= time <= (parent_time + max(window_size, max_gap)):
                    for sequence in _check_reduced_candidates_non_root(hash_tree[item], alt_data_sequence, min_gap, max_gap, window_size, time):
                        yield sequence
        if None in hash_tree:
            for sequence in hash_tree[None]:
                if check_candidates(alt_data_sequence, sequence, min_gap, max_gap, window_size):
                    yield sequence


def check_reduced_candidates(alt_data_sequence, hash_tree, min_gap, max_gap, window_size):
    for item in alt_data_sequence:
        for time in alt_data_sequence[item]:
            if item in hash_tree:
                for sequence in _check_reduced_candidates_non_root(hash_tree[item], alt_data_sequence, min_gap, max_gap, window_size, time):
                    yield sequence
