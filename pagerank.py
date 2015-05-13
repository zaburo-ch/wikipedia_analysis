# -*- coding: utf-8 -*-
import numpy as np
import scipy.sparse.linalg


def get_pagerank(M, alpha=0.85, return_P=False):
    """
    calculate pagerank usding scipy.sparse.linalg
    Args:
        M: transition probability matrix
        alpha: damping factor
        return_P: whether to return P
    Returns:
        array of index in ascending order of PageRank
    """
    n = len(M)
    M += np.ones([n, n]) * alpha / n
    la, v = scipy.sparse.linalg.eigs(M, k=1)
    P = v[:, 0]
    P /= P.sum()
    if return_P:
        return np.argsort(P)[-1::-1], P
    else:
        return np.argsort(P)[-1::-1]


def get_pagerank_simple(M, alpha=0.85, err_dist=0.001, return_P=False):
    """
    calculate pagerank using simply method
    Args:
        M: transition probability matrix
        return_P: whether to return P
        alpha: damping factor
        err_dist: error size target value
        return_P: whether to return P
    Returns:
        index array in ascending order of PageRank
    """
    n = len(M)
    M += np.ones([n, n]) * alpha / n
    P = np.matrix([1./n]*n).T
    while True:
        prev = P.copy()
        P = M.dot(P)
        P /= P.sum()
        err = np.abs(P-prev).sum()
        if err <= err_dist:
            break
        M = M.dot(M)
    if return_P:
        P = np.array(P.T)[0]
        return np.argsort(P)[-1::-1], P
    else:
        return np.argsort(np.array(P.T)[0])[-1::-1]


if __name__ == "__main__":
    M = np.array([[   0,   1, 1./2,    0, 1./4, 1./2,   0],
                  [1./5,   0, 1./2, 1./3,    0,    0,   0],
                  [1./5,   0,    0, 1./3, 1./4,    0,   0],
                  [1./5,   0,    0,    0, 1./4,    0,   0],
                  [1./5,   0,    0, 1./3,    0, 1./2,   1],
                  [   0,   0,    0,    0, 1./4,    0,   0],
                  [1./5,   0,    0,    0,    0,    0,   0]])
    print get_pagerank(M, alpha=0)
    print get_pagerank_simple(M, alpha=0)

    """
    import time
    n = 20000
    print "test : n = {0}".format(n)

    start = time.time()
    a = get_pagerank(np.eye(n), alpha=0)
    print "   ", time.time()-start

    start = time.time()
    b = get_pagerank_simple(np.eye(n), alpha=0)
    print "   ", time.time()-start

    print "   ", a
    print "   ", b
    """
