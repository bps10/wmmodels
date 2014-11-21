from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f
import nearest_neighbor as nn
from util.parse_txt import clean_data, parse_txt


def cone_inputs(d):
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

    '''psth = compute_psth(data[1]['rgc_on'][42], time.max(), delta_t=time_bin)
    fft =  np.fft.fft(psth)
    plt.figure(); plt.plot(np.real(fft))
    plt.figure(); plt.plot(psth)'''

    # Add in diamond boarders
    ax.plot([-1, 0], [0, 1], 'k')
    ax.plot([0, 1], [1, 0], 'k')
    ax.plot([1, 0], [0, -1], 'k')
    ax.plot([0, -1], [-1, 0], 'k')

    on_rgc = np.zeros((ncells, 3))
    off_rgc = np.zeros((ncells, 100))
    for t in data['meta']['trials']:
        for i in data[t]['rgc_on']:
            cell = data[t]['rgc_on'][i]
            psth = compute_psth(cell, time.max(), delta_t=time_bin)
            fft =  np.fft.fft(psth)

            amp = np.real(fft[tf]) * 2 / N
            on_rgc[i, t] = amp / cone_contrast[t] * -1

        for i in data[t]['rgc_off']:
            cell = data[t]['rgc_off'][i]
            psth = compute_psth(cell, time.max(), delta_t=time_bin)
            fft =  np.fft.fft(psth)

            amp = np.real(fft[tf]) * 2 / N
            off_rgc[i, t] = amp / cone_contrast[t] * -1

    on_cone_input = (on_rgc.T / np.abs(on_rgc).sum(1)).T
    off_cone_input = (off_rgc.T / np.abs(off_rgc).sum(1)).T
    
    for cone in range(0, len(on_cone_input[:, 0])):
        ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
        type = round(celldat[ind, 1])
        if type == 0.0:
            c = 'b'
        elif type == 1.0:
            c = 'g'
        else:
            c = 'r'
        ax.plot(on_cone_input[cone, 2], on_cone_input[cone, 1], 'o', color=c)
        ax.plot(off_cone_input[cone, 2], off_cone_input[cone, 1], 's', color=c)

    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    plt.show()


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
