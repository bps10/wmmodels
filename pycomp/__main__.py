#! /usr/bin/env python
import sys, os
import numpy as np

import plot as plot
from util.nd_read import nd_read


def get_filename(params):
    H1W = params['H1W']
    H2W = params['H2W']
    H2t = params['H2t']
    randomized = params['randomized']
    # handle randomized flag (passed in classify routines)
    if randomized == 'randomized':
        fname += '-H1W' + str(H1W) + '_H2W' + str(H2W) 
        fname += '_H2t' + str(H2t) + '_randomized'
        randomized = True
    elif randomized == []:
        fname = '-H1W' + str(H1W) + '_H2W' + str(H2W) 
        fname += '_H2t' + str(H2t)
        randomized = False
    else:
        raise Exception('Randomized option' + randomized + ' not understood')
    return fname

def main():
    '''
    '''
    if 'human' in sys.argv: # or 'WT' in sys.argv:
        species = 'human'
    elif 'macaque' in sys.argv or 'WT' in sys.argv or 'BPS' in sys.argv:
        species = 'macaque'

    mosaic_file = 'mosaics/' + sys.argv[1]

    # parse plotting options
    arg2 = sys.argv[2].split('-')
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
    if randomized != []: randomized = randomized[0]

    # parse model name
    model = sys.argv[3] #mosaic_file.split('/')[1].split('.')[0]

    # create params dict
    params = {'H1W': H1W, 'H2W': H2W, 'H2t': H2t,
              'randomized': randomized, }
    params['model_name'] = model
    params['mosaic_file'] = mosaic_file
    params['species'] = species
    params['single_cone'] = True
    params['block_plots'] = True
    if 'spot' not in sys.argv: # stimulus shape
        # used in s_dist nearest neighbor assumption
        params['single_cone'] = False

    if 'noblock' in sys.argv:
        params['block_plots'] = False
    for key in params.keys():
        print key + '=' + str(params[key]) + '\t'

    # options
    data = {}
    h1 = ['h1', 'verbose']
    h2 = ['h2', 'verbose']
    h_time = ['h_time', 'verbose']
    stack = ['siso', 'miso', 'liso', 'cone', 'coneiso', 'step']
    knn = ['knn']
    tuning = ['h_sf', 'bp_sf', 'rgc_sf', 'h_tf', 'bp_tf', 'rgc_tf']
    s_dist = ['s_dist']
    cone_inputs = ['cone_inputs']
    classify = ['vanhat', 'iso_classify']

    # read nd file if appropriate
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
            fname = tmp
        elif tmp in ['verbose']:
            fname = 'h_time'
        else:
            fname = option
            # these two share the same nd files
            if fname == 'cone_inputs' or fname == 'iso_classify':
                fname = 'sml_iso'

            fname += get_filename(params)
        ndfilename = 'results/nd_files/' + model + '/' + fname + '.nd'
        # check if file exists:
        if os.path.isfile(ndfilename):
            print 'reading nd file: ' + ndfilename
            d = nd_read(ndfilename)
        else:
            raise Exception(ndfilename + 
                            ' does not exist. Try running simulation.')

    # run plotting routines
    if option in h1 or option in h2:
        if option in h1:
            filepath = 'results/pl_files/' + model + '/' 
            filename = 'h1' + get_filename(params) + '.dist.pl' 
            print 'reading pl file: ' + filepath + filename
            data['h1'] = np.genfromtxt(filepath + filename, skip_header=2)

        if option in h2:
            filepath = 'results/pl_files/' + model + '/' 
            filename = 'h2' + get_filename(params) + '.dist.pl' 
            print 'reading pl file: ' + filepath + filename
            data['h2'] = np.genfromtxt(filepath + filename, skip_header=2)
        plot.dist(data, params)

    if option in h_time:
        plot.horiz_time_const(d, params)

    if option in stack:
        plot.stack(d, params)

    if option in knn:
        plot.knn(d, params)

    if option in tuning:
        params['cell_type'] = option.split('_')[0]
        params['analysis_type'] = option.split('_')[-1]
        plot.tuning_curve(d, params)
                
    if option in cone_inputs:
        params['cell_type'] = 'bp'
        params['cone_contrast'] = [48.768, 22.265, 18.576]
        params['analysis_type'] = 'cone_inputs'
        plot.cone_inputs(d, params)

    if option in classify:
        params['cell_type'] = 'bp'        
        params['cone_contrast'] = [48.768, 22.265, 18.576]
        params['analysis_type'] = 'cone_inputs'
        print 'Analyze color categories (false=LMS): ', color_cats_switch
        plot.classify_analysis(d, params, color_cats=color_cats_switch)

    # decide what to plot
    if 'mosaic' in option:
        plot.mosaic(params)


def parse_flags(flags, var_name):
    return [s for s in flags if var_name in s]


if __name__ == '__main__':

    main()
