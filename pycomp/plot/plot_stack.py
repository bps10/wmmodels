from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
import analysis as an
import util as u


def stack(d):
    '''
    TO DO:
    * Add rgc option
    '''

    ylim = [[0, 0], [0, 0], [0, 0]]
    figs = {}
    for t in range(d['ntrial']):
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

        time = u.get_time(d)
        # Subtract 10 points in so that zero offset
        for i in ax:
            ax[i].set_color_cycle(['r', 'g', 'b', 'c', 'm', 'y', 'k'])

        keys = u.get_cell_data(d['tr'][t], 'cone')
        for r in keys:
            dat = d['tr'][t]['r'][r]['x']
            y = dat - dat[10]
            ax[0].plot(time, y)
            ylim = check_lims(y, ylim, 0)

        keys = u.get_cell_data(d['tr'][t], 'h1')
        for r in keys:
            dat = d['tr'][t]['r'][r]['x']
            y = dat - dat[10] + 0.2
            ax[1].plot(time, y)
            ylim = check_lims(y, ylim, 1)

        keys = u.get_cell_data(d['tr'][t], 'h2')
        for r in keys:
            dat = d['tr'][t]['r'][r]['x']
            y = dat - dat[10] + 0.1
            ax[1].plot(time, y)
            ylim = check_lims(y, ylim, 1)

        keys = u.get_cell_data(d['tr'][t], 'bp')
        for r in keys:
            dat = d['tr'][t]['r'][r]['x']
            y = dat - dat[10]
            ax[2].plot(time, y)
            ylim = check_lims(y, ylim, 2)

        ax[2].set_xlabel('time (ms)')        
        figs[t]['ax'] = ax
    
    for t in figs:
        for i in ax:
            figs[t]['ax'][i].set_ylim(ylim[i])
    
        for i in ax:
            #pf.invert(ax[i], fig, bk_color='k')
            figs[t]['f'].savefig('results/img/stack_t' + str(t) + '.svg',
                                 edgecolor='none')

    plt.show()


def horiz_time_const(d):
    '''
    TO DO:
    '''

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    pf.AxisFormat()
    pf.TufteAxis(ax, ['bottom', 'left'], [3, 3])

    time = u.get_time(d)
    for t in range(d['ntrial']):
        h1 = u.get_cell_data(d['tr'][t], 'h1')
        h2 = u.get_cell_data(d['tr'][t], 'h2')

        h1dat = d['tr'][t]['r'][h1[0]]['x']
        h2dat = d['tr'][t]['r'][h2[0]]['x']

        ax.plot(time, h1dat) # only use 1st response
        ax.plot(time, h2dat) # only use 1st response
    
    #ax[1].set_ylabel('response')
    ax.set_xlabel('time (ms)')
    
    #pf.invert(ax[i], fig, bk_color='k')

    fig.savefig('results/img/h_time_const' + str(t) + '.svg', 
                #facecolor=fig.get_facecolor(), 
                edgecolor='none')

    plt.show()


def tuning_curve(d, cell_type='h1', tuning_type='sf'):
    '''
    '''
    deg2um = 0.00534 # macaque conversion (cpd to micron)

    fig = plt.figure(figsize=(7,7))
    fig.set_tight_layout(True)
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twiny()
    pf.AxisFormat()
    pf.TufteAxis(ax1, ['bottom', 'left', ], [4, 4])
    pf.TufteAxis(ax2, ['top', ], [4, 4])

    # get the data
    r = an.response(d, cell_type, tuning_type)

    colors = ['k', 'gray', 'r', 'b', 'g', 'c', 'm' ]
    cells = u.get_cell_type(cell_type)
    # set some smart axes for second axis
    ymax = -100 # start small
    ymin = 1000 # start large
    if tuning_type == 'sf':
        x = u.num(d['const']['VAR_sf']['val']) # spatial freq (cpd)
    elif tuning_type == 'tf':
        x = u.num(d['const']['VAR_tf']['val']) # temp freq

    for i, c in enumerate(cells):
        ax1.loglog(x, r[c][i, :], 'ko-', color=colors[i])
        vec = np.reshape(r[c], -1)
        max = np.max(vec)
        min = np.min(vec)
        if max > ymax:
            ymax = max
        if min < ymin:
            ymin = min

    ymax += 0.1
    ymin -= 0.1

    ax1.axis([x[0] - 0.05, x[-1] + 1, ymin, ymax])
    ax1.set_ylabel('amplitude')
    ax1.set_xlabel('cycles / degree')
    
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_left()
    ax2.axis([(x[0] - 0.05) * deg2um, (x[-1] + 1) * deg2um, ymin, ymax])
    ax2.set_xlabel('cycles / $\mu$m')
    ax2.set_xscale('log')

    plt.show()


def check_lims(dat, lim, ind):
    if dat.min() < lim[ind][0]:
        lim[ind][0] = dat.min()
    if dat.max() > lim[ind][1]:
        lim[ind][1] = dat.max()
    return lim


if __name__ == '__main__':
    plot_stack()
