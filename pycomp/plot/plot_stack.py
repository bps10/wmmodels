from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from util.parse_txt import clean_data


def stack(d):
    '''
    TO DO:
    * Add rgc option
    '''
    data = clean_data(d)
    for t in range(d['meta']['NTRIALS']):
        fig = plt.figure(figsize=(6.5, 9))
        fig.set_tight_layout(True)
        ax = {}
        ax[0] = fig.add_subplot(311)
        ax[1] = fig.add_subplot(312)
        ax[2] = fig.add_subplot(313)
        
        pf.AxisFormat()

        pf.TufteAxis(ax[0], ['left', ], [3, 3])
        pf.TufteAxis(ax[1], ['left', ], [3, 3])
        pf.TufteAxis(ax[2], ['bottom', 'left'], [3, 3])

        time = data['time'][1:]
        # Subtract 10 points in so that zero offset

        _d = data[t]
        color = ['r', 'g', 'b', 'k', 'y']
        for i, dat in enumerate(_d['cone']):
            ax[0].plot(time, dat[1:] - dat[10], color[i])
        for i, dat in enumerate(_d['h1']):
            ax[1].plot(time, dat[1:] - dat[10] + 0.35, color[i])
        for i, dat in enumerate(_d['h2']):
            ax[1].plot(time, dat[1:] - dat[10] + 0.1, color[i])
        for i, dat in enumerate(_d['bp']):
            ax[2].plot(time, dat[1:] - dat[10], color[i])

    #ax[1].set_ylabel('response')
            ax[2].set_xlabel('time (ms)')
    
        for i in ax:
            #pf.invert(ax[i], fig, bk_color='k')

            fig.savefig('results/img/stack_t' + str(t) + '.svg',
                        facecolor=fig.get_facecolor(), 
                        edgecolor='none')

    plt.show()


def horiz_time_const(d):
    '''
    TO DO:
    '''
    data = clean_data(d)

    for t in range(d['meta']['NTRIALS']):
        fig = plt.figure()
        fig.set_tight_layout(True)
        ax = {}
        ax[0] = fig.add_subplot(111)

        pf.AxisFormat()
        time = data['time'][1:]
        for i in ax:
            pf.TufteAxis(ax[i], ['bottom', 'left'], [3, 3])
    
        # Subtract 10 points in so that zero offset
            ax[0].plot(time, data[t]['h1'][0][1:] - 
                       data[t]['h1'][0][10])
            ax[0].plot(time, data[t]['h2'][0][1:] -
                       data[t]['h2'][0][10])
    #ax[1].set_ylabel('response')
        ax[0].set_xlabel('time (ms)')
    
        for i in ax:
            #pf.invert(ax[i], fig, bk_color='k')

            fig.savefig('results/img/h_time_const' + str(t) + '.svg', 
                        facecolor=fig.get_facecolor(), 
                        edgecolor='none')

    plt.show()


if __name__ == '__main__':
    plot_stack()
