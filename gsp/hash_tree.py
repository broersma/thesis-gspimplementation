from sequence import nthitem

def _add_to_hash_tree(hash_tree, sequence, n, d):
    key = nthitem(sequence,d)
    if key not in hash_tree:
        hash_tree[key] = list()
    
    if isinstance(hash_tree[key], list):
        hash_tree[key].append(sequence)
        if len(hash_tree[key]) > n and key is not None:
            hash_tree[key] = create_hash_tree(hash_tree[key], n, d+1)
            
    else:
        _add_to_hash_tree(hash_tree[key], sequence, n, d+1)

# in    set of sequences
# out   hash tree
def create_hash_tree(sequences, n, d = 0):
    """
    >>> print (create_hash_tree([((1,2),(3,)), ((1,),(2,),(3,)), ((1,),(2,),(3,4))], 1) ==
    ...       {1: {2: {3: {None: [((1, 2), (3,)), ((1,), (2,), (3,))], 4: [((1,), (2,), (3, 4))]}}}})
    True
    >>> print (create_hash_tree([((1,2),(3,)), ((1,),(2,),(3,4))], 1) ==
    ...       {1: {2: {3: {None: [((1, 2), (3,))], 4: [((1,), (2,), (3, 4))]}}}})
    True
    """
    if n <= 0:
        raise Exception("Sequence number per node threshold must be a non-zero positive integer.")

    root = dict()
    for sequence in sequences:
        _add_to_hash_tree(root, sequence, n, d)
    return root

def print_hash_tree(hash_tree, d = 0):
    """
    """
    if d == 0:
        print "(root)"
    for key in hash_tree:
        print "\t"*(d+1)+str(key),
        if isinstance(hash_tree[key],list):
            print hash_tree[key]
        else:
            print
            print_hash_tree(hash_tree[key],d+1)
