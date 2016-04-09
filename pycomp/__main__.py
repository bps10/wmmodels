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

    # parse plotting options
    arg2 = sys.argv[2].split('-')
    option = arg2[0]

    # parse flags
    flags = arg2[1].split('_')
    H1W = float(parse_flags(flags, 'H1W')[0][3:])
    H2W = float(parse_flags(flags, 'H2W')[0][3:])
    randomized = parse_flags(flags, 'randomized')[0]
    color_cats_switch = False
    print 'H1W=', H1W, 'H2W=', H2W, 'Random_Cones=', randomized, '\n'

    # parse model name
    model = sys.argv[3] #mosaic_file.split('/')[1].split('.')[0]

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
    classify = ['vanhat', 'iso_classify']
    single_cone = True
    block_plots = True

    if 'spot' not in sys.argv: # stimulus shape
        # used in s_dist nearest neighbor assumption
        single_cone = False

    if 'noblock' in sys.argv:
        block_plots = False

    read_nd = []
    read_nd.extend(h_time)
    read_nd.extend(stack)
    read_nd.extend(knn)
    read_nd.extend(tuning)
    read_nd.extend(cone_inputs)
    read_nd.extend(classify)

    # read nd file if necessary
    if option in read_nd:
        # read in the proper nd_file: model and analysis specific
        tmp = option.split('_')[-1]
        if tmp in ['sf', 'tf']:
            opt = tmp
        elif tmp in ['verbose']:
            opt = 'h_time'
        else:
            opt = option
            # handle randomized flag (passed in classify routines)
            if randomized == 'randomized':
                opt += '-H1W' + str(H1W) + '_H2W' + str(H2W) + '_randomized'
                randomized = True
            elif randomized == []:
                opt += '-H1W' + str(H1W) + '_H2W' + str(H2W)
                randomized = False
            else:
                raise('Randomized option' + randomized + ' not understood')

        ndfilename = 'results/nd_files/' + model + '/' + opt + '.nd'
        print 'reading nd file: ' + ndfilename
        d = nd_read(ndfilename)

    if option in h1:
        data['h1'] = np.genfromtxt('results/pl_files/' + model + 
                                   '/h1.dist.pl', skip_header=2)
        plot.dist(data, model, SPECIES, block_plots)

    if option in h2:
        data['h2'] = np.genfromtxt('results/pl_files/' + model + 
                                   '/h2.dist.pl', skip_header=2)
        plot.dist(data, model, SPECIES, block_plots)

    if option in stack:
        plot.stack(d, model, block_plots)

    if option in h_time:
        plot.horiz_time_const(d, model, block_plots)

    if option in knn:
        plot.knn(d, model, block_plots)

    if option in tuning:
        tuning_type = option.split('_')[-1]
        cell_type = option.split('_')[0]
        plot.tuning_curve(d, model, cell_type=cell_type, 
                          tuning_type=tuning_type,
                          block_plots=block_plots)
        
    if option in s_dist:
        plot.s_cone_hist(model, mosaic_file, SPECIES, single_cone, block_plots)
        
    if option in cone_inputs:
        cell_type = 'bp'
        plot.cone_inputs(d, model, mosaic_file, cell_type, block_plots, 
                         [48.768, 22.265, 18.576])

    if option in classify:
        cell_type = 'bp'
        plot.nat_image_analysis(d, model, mosaic_file, cell_type, randomized,
                                block_plots, color_cats=color_cats_switch)

    # decide what to plot
    if 'mosaic' in option:
        plot.mosaic(model, block_plot=block_plots)


def parse_flags(flags, var_name):
    return [s for s in flags if var_name in s]


if __name__ == '__main__':

    main()
