from __future__ import division
import numpy as np

from util import get_time, get_cell_data, get_cell_list, get_cell_type, num


def response(d, cell_type, analysis_type,
             cone_contrast=[49, 22, 19]):
    '''
    '''
    # Get cell list from data keys
    celllist = get_cell_list(d)

    # Load params from meta data
    N = num(d['const']['MOO_tn']['val']) # time steps

    time = get_time(d)
    ncells = len(celllist)
    time_bin = 15

    normalize = False
    # analysis specific parameters
    if analysis_type == 'cone_inputs':
        normalize = True
        sf = num(d['const']['sf']['val']) # spatial freq (cpd)
        tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
    elif analysis_type == 'tf':
        sf = num(d['const']['sf']['val']) # spatial freq (cpd)
        tf = num(d['const']['VAR_tf']['val']) # temporal frequency (Hz)
    elif analysis_type == 'sf':
        sf = num(d['const']['VAR_sf']['val']) # spatial freq (cpd)
        tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
    else:
        raise InputError('analysis type not supported (cone_input, sf, tf)')

    cells = get_cell_type(cell_type)

    resp = {}
    for c in cells: # for each cell type
        resp[c] = np.zeros((ncells, d['ntrial']))
        data = get_cell_data(d, c) ####### JUST RETURN LIST OF KEYS

        for t in range(d['ntrial']): # for each trial
            keys = sorted(data['tr'][t]['r'].keys())
            for i, r in enumerate(keys): # for each cell
                cell = d['tr'][t]['r'][r]['x']

                if cell_type == 'rgc':
                    cell = compute_psth(cell, time.max(), delta_t=20)

                fft =  np.fft.fft(cell)
                                
                if analysis_type == 'cone_inputs':
                    amp  = np.real(fft[tf]) * 2 / N
                    resp[c][i, t] = amp / cone_contrast[t]
                else: 
                    amp  = np.abs(fft[tf]) * 2 / N
                    resp[c][i, t] = amp

        if normalize:
            resp[c] = (resp[c].T / np.abs(resp[c]).sum(1)).T

    return resp


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
