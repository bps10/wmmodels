from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf


def plot_cones(time, data):

    fig = plt.figure()
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)

    pf.AxisFormat()
    pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])
    
    for dat in data:
        # Subtract 10 points in so that zero offset
        ax.plot(time, dat - dat[10])

    ax.set_ylabel('response')
    ax.set_xlabel('time (ms)')
    
    pf.invert(ax, fig, bk_color='k')

    plt.show()

if __name__ == '__main__':
    print 'Not yet implemented'
