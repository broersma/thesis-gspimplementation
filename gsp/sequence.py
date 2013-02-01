
import itertools
import operator


def sequence_remove(sequence, from_back = False):
    """
    >>> sequence_remove((frozenset(['Ringworld Engineers','Bladiebloep']), frozenset(['Ringworld Engineers']))) == (frozenset(['Ringworld Engineers']), frozenset(['Ringworld Engineers']))
    True
    >>> sequence_remove((frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep']), )) == (frozenset(['Ringworld', 'Ringworld Engineers']), )
    True
    >>> sequence_remove((frozenset(['Ringworld Engineers']), frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep']))) == (frozenset(['Bladiebloep', 'Ringworld', 'Ringworld Engineers']), )
    True
    >>> sequence_remove((frozenset(['Ringworld Engineers']), )) == ()
    True
    >>> sequence_remove((frozenset(['Ringworld Engineers','Bladiebloep']), frozenset(['Ringworld Engineers'])), True) == (frozenset(['Bladiebloep', 'Ringworld Engineers']),)
    True
    >>> sequence_remove((frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep']), ), True) == (frozenset(['Bladiebloep', 'Ringworld']),)
    True
    >>> sequence_remove((frozenset(['Ringworld Engineers']), frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep'])), True) == (frozenset(['Ringworld Engineers']), frozenset(['Bladiebloep', 'Ringworld']))
    True
    >>> sequence_remove((frozenset(['Ringworld Engineers']), ), True) == ()
    True
    """
    index, start, end = (-1, None, -1) if from_back else (0, 1, None)
    crazy_itemset = tuple(sorted(sequence[index]))
    remaining_itemset = ()
    if len(crazy_itemset) > 1:
        remaining_itemset += (frozenset(crazy_itemset[start:end]),)
    return sequence[:-1] + remaining_itemset if from_back else remaining_itemset + sequence[1:]


def sequence_join_compare(s1, s2):
    """
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), frozenset(['Bladiebloep', 'Ringworld']))
    >>> s2 = (frozenset(['Ringworld Engineers']), frozenset(['Ringworld Engineers', 'Bladiebloep', 'Ringworld']))
    >>> sequence_join_compare(s1,s2)
    True
    >>> s1 = (frozenset(['Ringworld']), frozenset(['Ringworld Engineers']), frozenset(['Bladiebloep', 'Ringworld']))
    >>> s2 = (frozenset(['Ringworld Engineers']), frozenset(['Ringworld Engineers', 'Bladiebloep', 'Ringworld']))
    >>> sequence_join_compare(s1,s2)
    True
    >>> s1 = (frozenset(['Ringworld']), frozenset(['Ringworld Engineers']), frozenset(['Bladiebloep', 'Ringworld']))
    >>> s2 = (frozenset(['Ringworld']), frozenset(['Ringworld Engineers', 'Bladiebloep', 'Ringworld']))
    >>> sequence_join_compare(s1,s2)
    False
    >>> s1 = (frozenset(['Ringworld']), )
    >>> s2 = (frozenset(['Ringworld']), )
    >>> sequence_join_compare(s1,s2)
    True
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> s2 = (frozenset(['Ringworld']), )
    >>> sequence_join_compare(s1,s2)
    False
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> s2 = (frozenset(['Ringworld Engineers']), )
    >>> sequence_join_compare(s1,s2)
    False
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> s2 = (frozenset(['Ringworld', 'Ringworld Engineers']), frozenset(['Ringworld']),)
    >>> sequence_join_compare(s1,s2)
    False
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> s2 = (frozenset(['Ringworld Engineers']), frozenset(['Ringworld']),)
    >>> sequence_join_compare(s1,s2)
    True
    >>> s1 = (frozenset(['Ringworld Engineers', 'Ringworld']), )
    >>> s2 = (frozenset(['Ringworld Engineers']), frozenset(['Ringworld']),)
    >>> sequence_join_compare(s1,s2)
    True
    >>> s1 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> s2 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> sequence_join_compare(s1,s2)
    False
    >>> s1 = (frozenset(['Ringworld Engineers', 'Ringworld']), )
    >>> s2 = (frozenset(['Ringworld', 'Ringworld Engineers']), )
    >>> sequence_join_compare(s1,s2)
    False
    """
    return reduce(operator.add, (sorted(itemset) for itemset in s1))[1:] == reduce(operator.add, (sorted(itemset) for itemset in s2))[:-1]

def sequence_get(sequence, from_back = False):
    # returns a sequence itemset from the front or back
    # and whether it was a separate item
    """
    >>> sequence_get((frozenset(['Ringworld Engineers','Bladiebloep']), frozenset(['Ringworld Engineers'])))
    ('Bladiebloep', False)
    >>> sequence_get((frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep']), ))
    ('Bladiebloep', False)
    >>> sequence_get((frozenset(['Ringworld Engineers']), frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep'])))
    ('Ringworld Engineers', True)
    >>> sequence_get((frozenset(['Ringworld Engineers']), ))
    ('Ringworld Engineers', True)
    >>> sequence_get((frozenset(['Ringworld Engineers','Bladiebloep']), frozenset(['Ringworld Engineers'])), True)
    ('Ringworld Engineers', True)
    >>> sequence_get((frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep']), ), True)
    ('Ringworld Engineers', False)
    >>> sequence_get((frozenset(['Ringworld Engineers']), frozenset(['Ringworld', 'Ringworld Engineers', 'Bladiebloep'])), True)
    ('Ringworld Engineers', False)
    >>> sequence_get((frozenset(['Ringworld Engineers']), ), True)
    ('Ringworld Engineers', True)
    """
    index = -1 if from_back else 0
    itemset = sorted(sequence[index])
    return itemset[index], len(itemset) == 1


def nthitem(sequence, n):
    """
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),-1)
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),0)
    1
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),1)
    2
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),3)
    4
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),5)
    6
    >>> nthitem((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])),6)
    """
    if n >= 0:
        for itemset in sequence:
            l = len(itemset)
            if n < l:
                return sorted(itemset)[n]
            n -= l
    return None


def sequence_len(sequence):
    """
    >>> sequence_len((frozenset([1,2,3]),frozenset([4,5]),frozenset([6])))
    6
    """
    return sum(map(len, sequence))

def extended_data_sequence(transformed_taxonomy, data_sequence):
    """
    [( 1,('Ringworld', )),
      ( 2,('Foundation', 'Ringworld')),
      (15,('Ringworld Engineers', 'Second Foundation'))
      ]
    """
    if transformed_taxonomy is None:
        return set(data_sequence)
    else:
        return [(t, reduce(frozenset.union, (transformed_taxonomy[item] for item in itemset if item in transformed_taxonomy), frozenset())) for t, itemset in data_sequence]


def contiguous_subsequences(sequence, k = -10**6):
    """
    >>> (frozenset([2]),frozenset([3,4]),frozenset([5])) in contiguous_subsequences((frozenset([1,2]),frozenset([3,4]),frozenset([5]),frozenset([6]) ))
    True
    >>> (frozenset([1,2]),frozenset([3]),frozenset([5]),frozenset([6])) in contiguous_subsequences((frozenset([1,2]),frozenset([3,4]),frozenset([5]),frozenset([6]) ))
    True
    >>> (frozenset([3]),frozenset([5])) in contiguous_subsequences((frozenset([1,2]),frozenset([3,4]),frozenset([5]),frozenset([6]) ))
    True
    >>> (frozenset([1,2]),frozenset([3,4]),frozenset([6])) in contiguous_subsequences((frozenset([1,2]),frozenset([3,4]),frozenset([5]),frozenset([6]) ))
    False
    >>> (frozenset([1]),frozenset([5]),frozenset([6])) in contiguous_subsequences((frozenset([1,2]),frozenset([3,4]),frozenset([5]),frozenset([6]) ))
    False
    """
    ret = set()
    for i, itemset in enumerate(sequence):
        if i == 0 or i == len(sequence)-1 or len(itemset) > 1:
            for c in itertools.combinations(itemset, len(itemset)-1):
                css = sequence[:i] + ((frozenset(c),) if c else ()) + sequence[i+1:]
                ret |= set([css])
                if k < -1:
                    ret |= contiguous_subsequences(css, k+1)
    return ret
