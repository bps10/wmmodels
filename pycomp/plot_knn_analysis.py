from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from util.parse_txt import clean_data


def knn(d):
    '''
    TO DO:
    * Add rgc option
    '''
    #print d
    data, celllist = clean_data(d, True)
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')
    cellIDs = celldat[:, 0]

    t = 0

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    
    pf.AxisFormat(markersize=8)
    pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

    for i, cell in enumerate(data[t]['h2']):
        cellID = int(celllist[i])
        ind = np.where(cellIDs == cellID)[0]
        #print cell.max() - cell[20], cellID, dist[ind, 4][0]
        amp = cell.max() - cell[20]
        distance = celldat[ind, 4][0]
        if celldat[ind, 1] == 0:
            ax.plot(distance, amp, 'bo')
        if celldat[ind, 1] == 1:
            ax.plot(distance, amp, 'go')
        if celldat[ind, 1] == 2:
            ax.plot(distance, amp, 'ro')

    plt.show()
