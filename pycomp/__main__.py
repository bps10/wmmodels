#! /usr/bin/env python
import sys, os
import numpy as np

import plot as plot
from util.nd_read import nd_read


def main():
    '''	
    '''	
    if 'human' in sys.argv:
        SPECIES = 'human'
    elif 'macaque' in sys.argv:
        SPECIES = 'macaque'

    if 'mosaic' in sys.argv:
        plot.mosaic()

    plots = []
    data = {}
    h1 = ['h1', 'verbose']
    h2 = ['h2', 'verbose']
    h_time = ['h_time', 'verbose']
    stack = ['siso', 'miso', 'liso', 'cone', 'stack', 'coneiso']
    knn = ['knn']
    tuning = ['h_sf', 'bp_sf', 'rgc_sf']
    s_dist = ['s_dist']
    cone_inputs = ['cone_inputs']

    for arg in sys.argv:
        if arg in h1:
            data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl',             
				       skip_header=2)
            if 'horiz' not in plots:
                plots.append('horiz')
        if arg in h2:
            data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', 
				       skip_header=2)            
            if 'horiz' not in plots:
                plots.append('horiz')
    
        if arg in stack:
            if 'stack' not in plots:
                plots.append('stack')
        if arg in h_time:
            if 'h_time' not in plots:
                plots.append('h_time')
        if arg in knn:
            plots.append('knn')

        if arg in tuning:
            plots.append('tuning')
            tuning_type = arg.split('_')[-1]
            cell_type = arg.split('_')[0]

        if arg in s_dist:
            plots.append('s_dist')

        if arg in cone_inputs:
            plots.append('c_inputs')
            cell_type = 'bp'

    if ('stack' in plots or 'h_time' in plots or 'knn' in plots or 
        'tuning' in plots or 'c_inputs' in plots):
        d = nd_read('results/nd_files/zz.nd')

    if 'stack' in plots:
        plot.stack(d)

    if 'h_time' in plots:
        plot.horiz_time_const(d)

    if 'horiz' in plots:
        if data is not {}:
            plot.dist(data, SPECIES)

    if 'knn' in plots:
        plot.knn(d)

    if 'tuning' in plots:
        plot.tuning_curve(d, cell_type=cell_type, tuning_type=tuning_type)

    if 's_dist' in plots:
        plot.s_cone_hist()

    if 'c_inputs' in plots:
        plot.cone_inputs(d, cell_type)


if __name__ == '__main__':

    main()
