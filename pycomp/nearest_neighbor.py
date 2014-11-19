from __future__ import division
import sys
import numpy as np
import scipy.spatial as spat


def find_neighbors(FILE='mosaics/model.mosaic', cone=4065, K=10, 
                   cell_type='horiz'):
    '''
    '''
    # get all cone locations
    mosaic = np.genfromtxt(FILE)
    
    # get the index of the specified cone
    c_ind = mosaic[cone, 2:]

    # get the nearest neighbors to the specified cone
    tree = spat.KDTree(mosaic[:, 2:])
    nn = tree.query(c_ind, K)
    
    # print out results for cone specified
    print ('\nsave_pop_unit_as_cone_' + str(cone) + ' f 500 bipolar ' + 
           str(cone) + ' 0 0 photo\n')

    # data container for saving later
    dat = np.zeros((K, 5))
    
    # base name used to save a pop cell
    base = 'save_pop_unit_as_'

    # setup based on cell type desired
    if cell_type == 'horiz':
        cells = {'h1': 'h1_', 'h2': 'h2_', }
        lFunc = lambda name, n, c: (base + name + n + ' f 500 bipolar ' + 
                                        n + ' 0 0 ' + c + '\n')
    if cell_type == 'rgc':
        cells = {'rgc': ['rgc_on_', 'rgc_off_'], }
        lFunc = lambda name, n, c: (base + name[0] + n + ' s 1000 rgc ' + 
                                        n + ' 0 1 ' + 'spikes\n' + 
                                        base + name[1] + n + ' s 1000 rgc ' + 
                                        n + ' 0 0 ' + 'spikes\n')

    # iterate through each cell in nearest neighbors
    for i, n in enumerate(nn[1]):
        for cell in cells:

            # construct print output
            line = lFunc(cells[cell], str(n), cell) 

            # print output
            print line 

            # record data for saving
            dat[i, 0:4] = mosaic[n] # ID, x, y, type
            dat[i, 4] = nn[0][i] # distance
    
    # save results to file for analysis later
    np.savetxt('results/txt_files/nn_results.txt', dat)


def find_nearest_S(cone_locations, FILE='mosaics/model.mosaic'):
    '''
    '''
    mosaic = np.genfromtxt(FILE)
    s_ind = mosaic[:, 1] == 0 # location of S-cones
    scones = mosaic[s_ind, 2:]

    tree = spat.KDTree(scones)
    nn = tree.query(cone_locations, 1) # find closest S-cone
    return nn

if __name__ == '__main__':

    cone = int(sys.argv[1])
    K = int(sys.argv[2])
    cell_type = 'horiz'
    try:
        cell_type = sys.argv[3]
    except IndexError:
        pass
    find_neighbors(cone=cone, K=K, cell_type=cell_type)
