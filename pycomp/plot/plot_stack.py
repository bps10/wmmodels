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
    ylim = [[0, 0], [0, 0], [0, 0]]
    figs = {}
    for t in range(d['meta']['NTRIALS']):
        figs[t] = {}
        figs[t]['f'] = plt.figure(figsize=(6.5, 9))
        figs[t]['f'].set_tight_layout(True)
        ax = {}
        ax[0] = figs[t]['f'].add_subplot(311)
        ax[1] = figs[t]['f'].add_subplot(312)
        ax[2] = figs[t]['f'].add_subplot(313)
        
        pf.AxisFormat()

        pf.TufteAxis(ax[0], ['left', ], [3, 3])
        pf.TufteAxis(ax[1], ['left', ], [3, 3])
        pf.TufteAxis(ax[2], ['bottom', 'left'], [3, 3])

        time = data['time'][1:]
        # Subtract 10 points in so that zero offset
        _d = data[t]
        color = ['r', 'g', 'b', 'k', 'y']
        for i, dat in enumerate(_d['cone']):
            y = dat[1:] - dat[10]
            ax[0].plot(time, y, color[i])
            ylim = check_lims(y, ylim, 0)

        for i, dat in enumerate(_d['h1']):
            y = dat[1:] - dat[10] + 0.2
            ax[1].plot(time, y, color[i])
            ylim = check_lims(y, ylim, 1)

        for i, dat in enumerate(_d['h2']):
            y = dat[1:] - dat[10] + 0.1
            ax[1].plot(time, y, color[i])
            ylim = check_lims(y, ylim, 1)

        for i, dat in enumerate(_d['bp']):
            y = dat[1:] - dat[10]
            ax[2].plot(time, y, color[i])
            ylim = check_lims(y, ylim, 2)

        ax[2].set_xlabel('time (ms)')        
        figs[t]['ax'] = ax
    
    for t in figs:
        for i in ax:
            figs[t]['ax'][i].set_ylim(ylim[i])
    
        for i in ax:
            #pf.invert(ax[i], fig, bk_color='k')
            figs[t]['f'].savefig('results/img/stack_t' + str(t) + '.svg',
                                 #facecolor=fig.get_facecolor(), 
                                 edgecolor='none')

    plt.show()


def check_lims(dat, lim, ind):
    if dat.min() < lim[ind][0]:
        lim[ind][0] = dat.min()
    if dat.max() > lim[ind][1]:
        lim[ind][1] = dat.max()
    return lim


def horiz_time_const(d):
    '''
    TO DO:
    '''
    data = clean_data(d)
    time = data['time'][1:]

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    pf.AxisFormat()
    pf.TufteAxis(ax, ['bottom', 'left'], [3, 3])

    for t in range(d['meta']['NTRIALS']):
    
        # Subtract 10 points in so that zero offset
        ax.plot(time, data[t]['h1'][0][1:] - 
                   data[t]['h1'][0][10])
        ax.plot(time, data[t]['h2'][0][1:] -
                   data[t]['h2'][0][10])
    
    #ax[1].set_ylabel('response')
    ax.set_xlabel('time (ms)')
    
    #pf.invert(ax[i], fig, bk_color='k')

    fig.savefig('results/img/h_time_const' + str(t) + '.svg', 
                #facecolor=fig.get_facecolor(), 
                edgecolor='none')

    plt.show()


def sf_tuning_curve(d):
    '''
    '''
    data = clean_data(d)
    time = data['time'][1:]
    ncells = len(data[0].keys()) - 1 # remove 1 for time

    fig = plt.figure(figsize=(7,7))
    fig.set_tight_layout(True)
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    pf.AxisFormat()
    pf.TufteAxis(ax1, ['bottom', 'left', ], [4, 4])
    pf.TufteAxis(ax2, ['top', ], [4, 4])

    # Load these from param files? Or send from retina.sh?
    tf = 5 # temporal frequency (Hz)
    N = 512 # time steps
    sf = np.array([0.1, 0.25, 0.5, 1.0, 2.0, 4.0]) # switch to microns
    deg2um = 0.00534 # macaque conversion

    h1cells = np.zeros((ncells, len(sf)))
    h2cells = np.zeros((ncells, len(sf)))
    for t in data:
        if t != 'time': 
            for i, cell in enumerate(data[t]['h1']):
                fft =  np.fft.fft(cell)
                # take abs because phase doesn't matter
                h1cells[i, t] = np.abs(fft[tf]) * 2 / N

            for i, cell in enumerate(data[t]['h2']):
                fft = np.fft.fft(cell)
                h2cells[i, t] = np.abs(fft[tf]) * 2 / N
                
    ax1.loglog(sf, h1cells.T, 'ko-')
    ax1.loglog(sf, h2cells.T, 'ro-')

    h1vec = np.reshape(h1cells, -1)
    h2vec = np.reshape(h2cells, -1)
    ymax = np.max([np.max(h1vec), np.max(h2vec)]) + 0.1
    ymin = np.min([np.min(h1vec), np.min(h2vec)]) - 0.1

    ax1.axis([sf[0] - 0.05, sf[-1] + 1, ymin, ymax])
    ax1.set_ylabel('amplitude')
    ax1.set_xlabel('cycles / degree')
    
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_left()
    ax2.axis([(sf[0] - 0.05) * deg2um, (sf[-1] + 1) * deg2um, ymin, ymax])
    ax2.set_xlabel('cycles / $\mu$m')
    ax2.set_xscale('log')

    plt.show()

if __name__ == '__main__':
    plot_stack()
