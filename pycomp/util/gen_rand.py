from __future__ import division
import numpy as np


def gen_randi(seed=27977, N=1):
    '''
    '''
    # Seed the generator
    np.random.seed(seed)
    return np.random.random_integers(0, 100000, N)


if __name__ == '__main__':
    
    out = gen_randi()
    line = ''
    for e in out:
        line += str(e) + ','
    print line
