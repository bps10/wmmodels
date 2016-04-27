#! /usr/bin/env python
import sys, os
import numpy as np

import plot as plot
from util.nd_read import nd_read


def main():
    '''
    '''
    option, params = parse_args(sys.argv)

    # options
    h_space = ['h1', 'h2', 'verbose', 'h_space']
    h_time = ['h_time', 'verbose']
    stack = ['siso', 'miso', 'liso', 'cone', 'coneiso', 'step']
    knn = ['knn']
    tuning = ['h_sf', 'bp_sf', 'rgc_sf', 'h_tf', 'bp_tf', 'rgc_tf', 'verbose']
    s_dist = ['s_dist']
    cone_inputs = ['cone_inputs', 'verbose']
    classify = ['vanhat', 'iso_classify', 'verbose']

    # read appropriate data and plot
    if option in h_space:
        pl_data = get_data(params, 'h_space', 'h_space')
        plot.dist(pl_data, params)

    if option in h_time:
        nd_data = get_data(params, 'h_time', 'nd')
        plot.horiz_time_const(nd_data, params)

    if option in stack:
        nd_data = get_data(params, option, 'nd')
        plot.stack(nd_data, params)

    if option in knn:
        nd_data = get_data(params, 'knn', 'nd')
        plot.knn(nd_data, params)

    if option in tuning:
        if option == 'verbose':
            params['analysis_type'] = 'sf' # only run sf analysis
        else:
            params['analysis_type'] = option.split('_')[-1]
        nd_data = get_data(params, 'sf', 'nd')
        plot.tuning_curve(nd_data, params)
                
    if option in cone_inputs:
        params['cell_type'] = 'bp'        
        params['cone_contrast'] = [48.768, 22.265, 18.576] # compute from stm file
        params['analysis_type'] = 'cone_inputs'
        nd_data = get_data(params, 'sml_iso', 'nd')
        plot.cone_inputs(nd_data, params)

    if option in classify:
        params['cell_type'] = 'bp'        
        params['cone_contrast'] = [48.768, 22.265, 18.576]
        params['analysis_type'] = 'cone_inputs'
        print 'Analyze color categories (false=LMS): ', params['color_cats_switch']
        nd_data = get_data(params, 'sml_iso', 'nd')
        plot.classify_analysis(nd_data, params)

    if 'mosaic' in option:
        plot.mosaic(params)


def get_data(params, analysis, data_type):
    model = params['model_name']
    fname = analysis
    # read nd file if necessary
    if data_type.lower() == 'nd':
        # read in the proper nd_file: model and analysis specific
        fname += get_filename(params)
        ndfilename = 'results/nd_files/' + model + '/' + fname + '.nd'
        # check if file exists:
        if os.path.isfile(ndfilename):
            print 'reading nd file: ' + ndfilename
            nd_data = nd_read(ndfilename)
        else:
            raise Exception(ndfilename + 
                            ' does not exist. Try running simulation.')
        return nd_data
        
    # get h_space data
    elif data_type.lower() ==  'h_space':
        pl_data = {}
        filepath = 'results/pl_files/' + model + '/' 

        # first load h1 data
        filename = 'h1' + get_filename(params) + '.dist.pl' 
        print 'reading pl file: ' + filepath + filename
        pl_data['h1'] = np.genfromtxt(filepath + filename, skip_header=2)

        # then load h2 data
        filename = 'h2' + get_filename(params) + '.dist.pl' 
        print 'reading pl file: ' + filepath + filename
        pl_data['h2'] = np.genfromtxt(filepath + filename, skip_header=2)

        return pl_data

    else:
        raise Exception('data_type: ' + data_type + ' not understood')


def get_filename(params):
    H1W = params['H1W']
    H2W = params['H2W']
    H2t = params['H2t']
    randomized = params['randomized']
    # handle randomized flag (passed in classify routines)
    if randomized == 'randomized':
        fname = '-H1W' + str(H1W) + '_H2W' + str(H2W) 
        fname += '_H2t' + str(H2t) + '_randomized'
        randomized = True
    elif randomized == []:
        fname = '-H1W' + str(H1W) + '_H2W' + str(H2W) 
        fname += '_H2t' + str(H2t)
        randomized = False
    else:
        raise Exception('Randomized option' + randomized + ' not understood')
    return fname


def parse_args(args):
    if 'human' in args: # or 'WT' in args:
        species = 'human'
    elif 'macaque' in args or 'WT' in args or 'BPS' in args:
        species = 'macaque'

    mosaic_file = 'mosaics/' + args[1]

    # parse plotting options
    arg2 = args[2].split('-')
    option = arg2[0]
    if option.split('_')[-1] == 'lms':
        option = option[:-4]
        color_cats_switch = False
    else:
        color_cats_switch = True

    # parse flags: put this into a function
    flags = arg2[1].split('_')
    H1W = float(parse_flags(flags, 'H1W')[0][3:])
    H2W = float(parse_flags(flags, 'H2W')[0][3:])
    H2t = float(parse_flags(flags, 'H2t')[0][3:])
    randomized = parse_flags(flags, 'randomized')
    if randomized != []: 
        randomized = randomized[0]

    # parse model name
    model = args[3] #mosaic_file.split('/')[1].split('.')[0]

    # create params dict
    params = {'H1W': H1W, 'H2W': H2W, 'H2t': H2t,
              'randomized': randomized, }
    params['model_name'] = model
    params['mosaic_file'] = mosaic_file
    params['species'] = species
    params['color_cats_switch'] = color_cats_switch

    # stimulus shape
    params['single_cone'] = True
    if 'spot' not in args: 
        # used in s_dist nearest neighbor assumption
        params['single_cone'] = False

    # decide to block plots
    params['block_plots'] = True
    if 'noblock' in args:
        params['block_plots'] = False

    # parse cell type if passed in option
    params['cell_type'] = 'bp'
    if option[-2:] in ['tf', 'sf']:
        params['cell_type'] = option.split('_')[0]
    elif option == 'verbose':
        params['cell_type'] = 'h'

    # print params
    for key in params.keys():
        print key + '=' + str(params[key]) + '\t'

    return option, params


def parse_flags(flags, var_name):
    return [s for s in flags if var_name in s]


if __name__ == '__main__':

    main()
