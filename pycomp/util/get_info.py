from __future__ import division
import numpy as np

from format import num


def get_cell_list(d, return_celllist=False):
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
    '''Return a new dictionary with metadata and response data from
    only the cell type specified by cell_type.
    '''
    cells = d.copy()
    for t in d['tr']: # for each trial
        for r in d['tr'][t]['r'].keys(): # for each response
            name = d['tr'][t]['r'][r]['name']  # cell name
            name = name.split('_')
            if name[0] != cell_type: # if cell type not desired, delete
                del cells['tr'][t]['r'][r] # delete response

    return cells


def get_time(d):
    '''Return an array of time values using params from
    data dictionary
    '''
    samp = num(d['const']['stim_samp']['val'])
    tn = num(d['const']['MOO_tn']['val'])
    time = np.linspace(0, samp, tn)
    return time
