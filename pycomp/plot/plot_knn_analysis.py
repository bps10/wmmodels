from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f
import nearest_neighbor as nn
from util.parse_txt import clean_data, parse_txt


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

        amp = cell.max() - cell[20]
        distance = celldat[ind, 4][0]
        if celldat[ind, 1] == 0:
            ax.plot(distance, amp, 'bo')
        if celldat[ind, 1] == 1:
            ax.plot(distance, amp, 'go')
        if celldat[ind, 1] == 2:
            ax.plot(distance, amp, 'ro')

    plt.show()


def s_cone_hist():
    '''
    TO DO:
    * Add rgc option
    '''
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')
    cellIDs = celldat[:, 0]
    dist2S =  nn.find_nearest_S(celldat[:, 2:4])[0]

    names = f.getAllFiles('./results/txt_files/s_dist', suffix='/*.txt',
                          subdirectories=0)
    s = []
    lm = []
    for fname in names:
        if fname[-10:] != 'params.txt':
            d = parse_txt(fname)
            data, celllist = clean_data(d, True)

            t = 0 # trial 0
            for i, cell in enumerate(data[t]['h2']):
                # get cell info
                cellID = int(celllist[i])
                ind = np.where(cellIDs == cellID)[0]

                # compute amplitude and find distance to S-cone
                amp = cell.max() - cell[20]
                # if stim == 'spot':
                #distance = celldat[ind, 4][0] # relative to 1 S-cone
                # else:
                distance = dist2S[ind] # relative to any S-cone

                if celldat[ind, 1] == 0:
                    s.append([distance, amp])
                else:
                    lm.append([distance, amp])

    # plotting routines
    fig1 = plt.figure()
    fig1.set_tight_layout(True)
    ax = fig1.add_subplot(111)
    
    pf.AxisFormat(markersize=8)
    pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

    lm = np.asarray(lm)
    ax.plot(lm[:, 0], lm[:, 1], 'ko')

    # if stim != 'spot':
    ax.set_xlim([0.8, 5.2])
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

    # Save plots
    fig1.savefig('results/img/s_dist_scatter.svg', edgecolor='none')
    fig2.savefig('results/img/s_dist_hist.svg', edgecolor='none')
    
    plt.show()

