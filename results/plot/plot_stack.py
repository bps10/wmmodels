from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from parse_txt import clean_data


def stack(d):
    '''
    TO DO:
    * Figure out proper time range
    * Add rgc option
    '''
    data = clean_data(d)

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
        ax[0].plot(data['time'][1:], dat[1:] - dat[10])
    for dat in data['h1']:
        ax[1].plot(data['time'][1:], dat[1:] - dat[10] + 0.35)
    for dat in data['h2']:
        ax[1].plot(data['time'][1:], dat[1:] - dat[10] + 0.1)
    for dat in data['bp']:
        ax[2].plot(data['time'][1:], dat[1:] - dat[10])

    #ax[1].set_ylabel('response')
    ax[2].set_xlabel('time (ms)')
    
    for i in ax:
        pf.invert(ax[i], fig, bk_color='k')

    plt.show()


def horiz_time_const(d):
    '''
    TO DO:
    * Figure out proper time range
    * Add rgc option
    * Move data processing in beginning to a util.py
    '''
    data = clean_data(d)

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = {}
    ax[0] = fig.add_subplot(111)


    pf.AxisFormat()

    for i in ax:
        pf.TufteAxis(ax[i], ['bottom', 'left'], [3, 3])
    
        # Subtract 10 points in so that zero offset
        ax[0].plot(data['time'][1:], data['h1'][0][1:] - 
                   data['h1'][0][10])
        ax[0].plot(data['time'][1:], data['h2'][0][1:] -
                   data['h2'][0][10])
    #ax[1].set_ylabel('response')
    ax[0].set_xlabel('time (ms)')
    
    for i in ax:
        pf.invert(ax[i], fig, bk_color='k')

    plt.show()


if __name__ == '__main__':
    plot_stack()
