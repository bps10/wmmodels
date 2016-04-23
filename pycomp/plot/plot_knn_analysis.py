from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f

from util import nearest_neighbor as nn
from util import get_cell_list, get_cell_data, num, conversion_factors
from util.nd_read import nd_read


def knn(d, params):
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

    savedir = util.get_save_dirname(params, check_randomized=True)
    fig.savefig(savedir + 'knn.svg', edgecolor='none')
    plt.show(block=params['block_plots'])
