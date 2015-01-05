from __future__ import division
import numpy as np

from util import get_time, get_cell_data, num


def compute_cone_input(d, cell_type, celllist, cone_contrast=[49, 22, 19]):
    '''
    '''

    # Load params from meta data
    tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
    N = num(d['const']['MOO_tn']['val']) # time steps
    sf = num(d['const']['sf']['val']) # spatial freq (cpd)
    deg2um = 0.00534 # macaque conversion (cpd to micron)

    time = get_time(d)
    ncells = len(celllist)
    time_bin = 15

    on_rgc = np.zeros((ncells, 3))
    off_rgc = np.zeros((ncells, 3))

    if cell_type == 'h': # horizontal cells
        cells = ['h1', 'h2']
    elif cell_type == 'rgc':
        cells = ['rgc_on', 'rgc_off']
    elif cell_type == 'bp':
        cells = ['bp']
    else:
        raise InputError('cell_type must equal horiz or rgc')
    
    r = {}
    for c in cells:
        r[c] = np.zeros((ncells, 3))

    for c in cells: # for each cell type
        data = get_cell_data(d, c)
        for t in range(d['ntrial']): # for each trial
            j = 0
            for i in d['tr'][t]['r']: # for each cell
                cell = d['tr'][t]['r'][i]['x']

                if cell_type == 'rgc':
                    cell = d['tr'][t]['r'][i]['p']
                    cell = compute_psth(cell, time.max(), delta_t=20)
                
                fft =  np.fft.fft(cell)
                amp  = np.real(fft[tf]) * 2 / N
                # take abs because phase doesn't matter
                r[c][j, t] = amp / cone_contrast[t]
                j += 1

        # normalize
        r[c] = (r[c].T / np.abs(r[c]).sum(1)).T

    return r


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
