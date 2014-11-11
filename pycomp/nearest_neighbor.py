from __future__ import division
import sys
import numpy as np
import scipy.spatial as spat


def find_neighbors(FILE='results/txt_files/zz.mosaic', cone=4065, K=10):
    '''
    '''

    mosaic = np.genfromtxt(FILE)
    c_ind = mosaic[cone, 2:]
    #print mosaic.shape[0] # number of cones

    tree = spat.KDTree(mosaic[:, 2:])
    nn = tree.query(c_ind, K)
    
    # print out results
    print ('\nsave_pop_unit_as_cone_' + str(cone) + ' f 500 bipolar ' + 
           str(cone) + ' 0 0 photo\n')
    dat = np.zeros((K, 5))
    base = 'save_pop_unit_as_'
    horiz = ['h1_', 'h2_']
    for i, n in enumerate(nn[1]):
        for j, cell in enumerate(['horiz', 'h2']):
            line = base + horiz[j] +  str(n)
            line += ' f 500 bipolar ' + str(n) + ' 0 0 ' + cell + '\n'
            print line 
            dat[i, 0:4] = mosaic[n] # ID, x, y, type
            dat[i, 4] = nn[0][i] # distance
    
    # save results to file for analysis later
    np.savetxt('results/txt_files/nn_results.txt', dat)

if __name__ == '__main__':

    cone = int(sys.argv[1])
    K = int(sys.argv[2])

    find_neighbors(cone=cone, K=K)
