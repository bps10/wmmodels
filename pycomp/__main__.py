#! /usr/bin/env python
import sys, os
import numpy as np

import plot as plot
from util.nd_read import nd_read


def main():
    '''
    '''
    if 'human' in sys.argv: # or 'WT' in sys.argv:
        SPECIES = 'human'
    elif 'macaque' in sys.argv or 'WT' in sys.argv or 'BPS' in sys.argv:
        SPECIES = 'macaque'

    mosaic_file = 'mosaics/' + sys.argv[1]
    model = mosaic_file.split('/')[1].split('.')[0]

    plots = []
    data = {}
    h1 = ['h1', 'verbose']
    h2 = ['h2', 'verbose']
    h_time = ['h_time', 'verbose']
    stack = ['siso', 'miso', 'liso', 'cone', 'stack', 'coneiso', 'step']
    knn = ['knn']
    tuning = ['h_sf', 'bp_sf', 'rgc_sf', 'h_tf', 'bp_tf', 'rgc_tf']
    s_dist = ['s_dist']
    cone_inputs = ['cone_inputs']
    single_cone = True
    block_plots = True

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

    if 'spot' not in sys.argv: # stimulus shape
        # used in s_dist nearest neighbor assumption
        single_cone = False

    if 'noblock' in sys.argv:
        block_plots = False

    if ('stack' in plots or 'h_time' in plots or 'knn' in plots or
        'tuning' in plots or 'c_inputs' in plots):
        d = nd_read('results/nd_files/zz.nd')

    # decide what to plot
    if 'mosaic' in sys.argv:
        plot.mosaic(model, block_plot=block_plots)

    if 'stack' in plots:
        plot.stack(d, model, block_plots)

    if 'h_time' in plots:
        plot.horiz_time_const(d, model, block_plots)

    if 'horiz' in plots:
        if data is not {}:
            plot.dist(data, model, SPECIES, block_plots)

    if 'knn' in plots:
        plot.knn(d, model, block_plots)

    if 'tuning' in plots:
        plot.tuning_curve(d, model, cell_type=cell_type, 
                          tuning_type=tuning_type,
                          block_plots=block_plots)

    if 's_dist' in plots:
        # single_cone (False=nearest S cone)
        plot.s_cone_hist(model, mosaic_file, SPECIES, single_cone, block_plots)

    if 'c_inputs' in plots:
        plot.cone_inputs(d, model, mosaic_file, cell_type, block_plots, 
                         [48.768, 22.265, 18.576])


if __name__ == '__main__':

    main()
