from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf
from base import files as f


def mosaic(model, FILE='mosaics/model.mosaic', block_plot=True, invert=False, 
           return_ax=False):

    mosaic = np.genfromtxt(FILE)
    fig = plt.figure(figsize=(9, 9))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)
    
    pf.AxisFormat()
    pf.TufteAxis(ax, [''], [5, 5])
    
    s_cones = mosaic[np.where(mosaic[:, 1] == 0)[0]]
    m_cones = mosaic[np.where(mosaic[:, 1] == 1)[0]]
    l_cones = mosaic[np.where(mosaic[:, 1] == 2)[0]]
    
    ax.plot(s_cones[:, 2], s_cones[:, 3], 'bo', markersize=6)
    ax.plot(m_cones[:, 2], m_cones[:, 3], 'go', markersize=6)
    ax.plot(l_cones[:, 2], l_cones[:, 3], 'ro', markersize=6)
    
    ax.set_xlim([-1, 128])
    ax.set_ylim([-1, 128])

    if invert:
        pf.invert(ax, fig, bk_color='k')

    if not return_ax:
        f.make_dir('results/img/' + model)
        fig.savefig('results/img/' + model + '/mosaic.svg', edgecolor='none')
        plt.show(block=block_plot)

    else:
        return ax, fig

if __name__ == '__main__':
    plot_mosaic()
