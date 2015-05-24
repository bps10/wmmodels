from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f
from util import nearest_neighbor as nn
from util import get_cell_list, get_cell_data, num
from util.nd_read import nd_read

def knn(d):
    '''
    TO DO:

    '''
    celllist = get_cell_list(d)
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')
    cellIDs = celldat[:, 0]

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    
    pf.AxisFormat(markersize=8)
    pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

    N = num(d['const']['MOO_tn']['val']) # time steps
    tf = num(d['const']['tf']['val']) # temporal frequency (Hz)

    keys = get_cell_data(d['tr'][0], 'h2')
    for i, r in enumerate(keys):
        # find distance to S
        cellID = int(celllist[i])
        ind = np.where(cellIDs == cellID)[0]
        distance = celldat[ind, 4][0]
        
        # find amplitude of signal
        cell = d['tr'][0]['r'][r]['x']
        fft = np.fft.fft(cell)
        amp  = np.abs(fft[tf]) * 2 / N

        if celldat[ind, 1] == 0:
            ax.plot(distance, amp, 'bo')
        if celldat[ind, 1] == 1:
            ax.plot(distance, amp, 'go')
        if celldat[ind, 1] == 2:
            ax.plot(distance, amp, 'ro')

    plt.show()


def s_cone_hist(mosaic_file, single_cone=True):
    '''
    TO DO:
    * Add rgc option
    '''
    celldat = np.genfromtxt('results/nd_files/s_dist/nn_results.txt')
    cellIDs = celldat[:, 0]
    if not single_cone:
        dist2S =  nn.find_nearest_S(celldat[:, 2:4], mosaic_file)[0]
    else:
        dist2S = celldat[:, 4]

    fnames = f.getAllFiles('./results/nd_files/s_dist', suffix='.nd',
                          subdirectories=0)
    s = []
    lm = []
    for fname in fnames:
        d = nd_read(fname)
        celllist = get_cell_list(d)
        
        t = 0 # trial 0
            ####### PUT THIS INTO A FUNCTION
        N = num(d['const']['MOO_tn']['val']) # time steps
        tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
        
        keys = get_cell_data(d['tr'][t], 'h2')
        for i, r in enumerate(keys):
            # find distance to S
            cellID = int(celllist[i])
            ind = np.where(cellIDs == cellID)[0]
            distance = dist2S[ind]
            
            # find amplitude of signal
            cell = d['tr'][t]['r'][r]['x']
            fft = np.fft.fft(cell)
            amp  = np.abs(fft[tf]) * 2 / N

            if celldat[ind, 1] == 0:
                s.append([distance, amp])
            else:
                lm.append([distance, amp])
        ############### ------ END FUNCTION

    # plotting routines
    fig1 = plt.figure()
    fig1.set_tight_layout(True)
    ax = fig1.add_subplot(111)
    
    pf.AxisFormat(markersize=8)
    pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

    lm = np.asarray(lm)
    ax.plot(lm[:, 0], lm[:, 1], 'ko')

    ax.set_xlabel('distance from S-cone')
    ax.set_ylabel('amplitude')

    fig2 = plt.figure()
    fig2.set_tight_layout(True)
    ax2 = fig2.add_subplot(111)
    
    pf.AxisFormat(markersize=8)
    pf.TufteAxis(ax2, ['bottom', 'left'], [5, 5])
    
    count, bins = np.histogram(lm[:, 1], bins=20)
    count = count / count.sum()
    bins, count = pf.histOutline(count, bins)
    
    ax2.plot(bins, count, 'k-')

    ax2.set_ylabel('density')
    ax2.set_xlabel('amplitude')

    # Save plots
    fig1.savefig('results/img/s_dist_scatter.svg', edgecolor='none')
    fig2.savefig('results/img/s_dist_hist.svg', edgecolor='none')
    
    plt.show()
