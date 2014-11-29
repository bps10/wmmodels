from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f
import nearest_neighbor as nn
from util.parse_txt import clean_data, parse_txt


def cone_inputs(d, cell_type='bp'):
    '''
    '''
    data, celllist = clean_data(d, True)
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')

    t = 0

    fig = plt.figure(figsize=(6,6))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    
    pf.AxisFormat(markersize=8, fontsize=20)
    pf.centerAxes(ax)
    ax.spines['left'].set_smart_bounds(False)
    ax.spines['bottom'].set_smart_bounds(False)
    ax.axis('equal')

    # Load params from meta data
    tf = data['meta']['tf'] # temporal frequency (Hz)
    N = data['meta']['MOO_tn'] # time steps
    sf = data['meta']['sf'] # spatial freq (cpd)
    deg2um = 0.00534 # macaque conversion (cpd to micron)

    cone_contrast = [49, 22, 19]
    time = data['time']
    ncells = len(celllist)
    time_bin = 15

    # Add in diamond boarders
    ax.plot([-1, 0], [0, 1], 'k')
    ax.plot([0, 1], [1, 0], 'k')
    ax.plot([1, 0], [0, -1], 'k')
    ax.plot([0, -1], [-1, 0], 'k')

    on_rgc = np.zeros((ncells, 3))
    off_rgc = np.zeros((ncells, 3))

    if cell_type == 'h': # horizontal cells
        cells = ['h1', 'h2']
    elif cell_type == 'rgc':
        cells = ['rgc_on', 'rgc_off']
        bins = np.arange(0, time.max(), 20)
    elif cell_type == 'bp':
        cells = ['bp']
    else:
        raise InputError('cell_type must equal horiz or rgc')
    
    r = {}
    for c in cells:
        r[c] = np.zeros((ncells, 3))

    for t in data['meta']['trials']: # for each trial
        for c in cells: # for each cell type
            for i in range(ncells): # for each cell
                cell = data[t][c][i]
                if cell_type == 'rgc':
                    cell = compute_psth(cell, time.max(), delta_t=20)
                
                fft =  np.fft.fft(cell)
                amp  = np.real(fft[tf]) * 2 / N
                # take abs because phase doesn't matter
                r[c][i, t] = amp / cone_contrast[t]
    for c in cells:
        r[c] = (r[c].T / np.abs(r[c]).sum(1)).T

        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
            type = round(celldat[ind, 1])
            sym = find_shape_color(type, c)
            ax.plot(r[c][cone, 2], r[c][cone, 1], sym)

    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    plt.show()


def find_shape_color(type, c):
    if type == 0.0:
        color = 'b'
    elif type == 1.0:
        color = 'g'
    else:
        color = 'r'
    onoff = c.split('_')
    if 'off' in onoff:
        sym = 's'
    else:
        sym = 'o'
    return sym + color


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
