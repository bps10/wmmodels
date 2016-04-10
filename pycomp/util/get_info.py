from __future__ import division
import numpy as np

from format import num


def get_cell_type(cell_type):
    '''
    '''
    # cell type parameters
    if cell_type == 'h': # horizontal cells
        cells = ['h1', 'h2']
    elif cell_type == 'rgc':
        cells = ['rgc_on', 'rgc_off']
    elif cell_type == 'bp':
        cells = ['bp']
    else:
        raise InputError('cell_type must equal horiz or rgc')

    return cells

def get_cell_list(d):
    '''Return a list of cell names in data dictionary
    '''    
    celllist = []
    for i in d['tr'][0]['r']:
        cell = d['tr'][0]['r'][i]['name']
        cell = cell.split('_')
        if cell[-1] not in celllist:
            celllist.append(cell[-1])

    return celllist


def get_cell_data(d, cell_type):
    '''Return a new dictionary with response indices from
    only the cell type specified by cell_type. 
    '''
    ind = 0
    if cell_type == 'cone':
        ind = 1
    ctype = cell_type.split('_')[0]

    if 'tr' in d:
        cells = {}
        cells['tr'] = {}
        for t in d['tr']: # for each trial
            cells['tr'][t] = {'r': []}
            for r in d['tr'][t]['r'].keys(): # for each response
                n = d['tr'][t]['r'][r]['name']  # cell name
                name = n.split('_')[ind]
                if name == ctype: # if cell type not desired, delete
                    if name == 'rgc':
                        # handle on and off here
                        cells['tr'][t]['r'].append(r)
                    else:
                        cells['tr'][t]['r'].append(r)
                cells['tr'][t]['r'] = sorted(cells['tr'][t]['r'])

    elif 'r' in d:
        cells = []
        for r in d['r'].keys(): # for each response
            n = d['r'][r]['name']  # cell name
            name = n.split('_')[ind]
            if name == cell_type: # if cell type not desired, delete
                if name == 'rgc':
                    cells.append(r)
                else:
                    cells.append(r)
        cells = sorted(cells)

    else:
        raise InputError('Dict must contain tr or r')

    return cells


def get_nn_dat(model_name):
    filename = 'results/txt_files/' + model_name + '/nn_results.txt'
    print 'read nearest neighbors from: ' + filename

    return np.genfromtxt(filename)

def get_time(d):
    '''Return an array of time values using params from
    data dictionary
    '''
    samp = num(d['const']['stim_samp']['val'])
    tn = num(d['const']['MOO_tn']['val'])
    time = np.linspace(0, samp, tn)
    return time
