from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf

from util import get_cell_list
import analysis as an


def cone_inputs(d, cell_type='bp'):
    '''
    '''
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')

    fig = plt.figure(figsize=(6,6))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)

    # build diamon plot
    pf.AxisFormat(markersize=8, fontsize=20)
    pf.centerAxes(ax)
    ax.spines['left'].set_smart_bounds(False)
    ax.spines['bottom'].set_smart_bounds(False)
    ax.axis('equal')

    # Add in diamond boarders
    ax.plot([-1, 0], [0, 1], 'k')
    ax.plot([0, 1], [1, 0], 'k')
    ax.plot([1, 0], [0, -1], 'k')
    ax.plot([0, -1], [-1, 0], 'k')

    # get results
    celllist = get_cell_list(d)
    r = an.response(d, cell_type, 'cone_inputs')
    for c in r: # for each cell type in results
        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
            type = round(celldat[ind, 1])
            sym = find_shape_color(type, c)
            ax.plot(r[c][cone, 2], r[c][cone, 1], sym)

    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    plt.show()


def find_shape_color(type, c):
    if type == 0.0:
        color = 'b'
    elif type == 1.0:
        color = 'g'
    else:
        color = 'r'
    onoff = c.split('_')
    if 'off' in onoff:
        sym = 's'
    else:
        sym = 'o'
    return sym + color

