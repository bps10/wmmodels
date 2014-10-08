from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf


def plot_stack(d):
    
    data = {}
    data['cone'] = []
    data['h1'] = []
    data['h2'] = []
    data['bp'] = []
    data['rgc'] = []
    for key in d.keys():
        if key[2:6] == 'cone':
            data['cone'].append(d[key]['vals'])
        elif key[:2] == 'h1':
            data['h1'].append(d[key]['vals'])
        elif key[:2] == 'h2':
            data['h2'].append(d[key]['vals'])
        elif key[:2] == 'bp':
            data['bp'].append(d[key]['vals'])
        elif key[:3] == 'rgc':
            data['rgc'].append(d[key]['vals'])
    time = np.arange(len(d[key]['vals']))

    fig = plt.figure(figsize=(6.5, 9))
    fig.set_tight_layout(True)
    ax = {}
    ax[0] = fig.add_subplot(311)
    ax[1] = fig.add_subplot(312)
    ax[2] = fig.add_subplot(313)


    pf.AxisFormat()
    for i in ax:
        pf.TufteAxis(ax[i], ['bottom', 'left'], [3, 3])
    
    for dat in data['cone']:
        # Subtract 10 points in so that zero offset
        ax[0].plot(time[1:], dat[1:] - dat[10])
    for dat in data['h1']:
        ax[1].plot(time[1:], dat[1:] - dat[10] + 0.35)
    for dat in data['h2']:
        ax[1].plot(time[1:], dat[1:] - dat[10] + 0.1)
    for dat in data['bp']:
        ax[2].plot(time, dat - dat[10])

    #ax[1].set_ylabel('response')
    ax[2].set_xlabel('time (ms)')
    
    for i in ax:
        pf.invert(ax[i], fig, bk_color='k')

    plt.show()

if __name__ == '__main__':
    plot_stack()
