from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf

from util import get_cell_list
from plot.plot_mosaic import mosaic
import analysis as an


def cone_inputs(d, mosaic_file, cell_type='bp', block_plots=True,
                cone_contrast=[48.768, 22.265, 18.576]):
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
    # get response -- find way to pass cone contrast properly
    r = an.response(d, cell_type, 'cone_inputs', 
                    cone_contrast=cone_contrast)

    # get mosaic plot
    mos, mos_fig = mosaic(FILE=mosaic_file, return_ax=True)
    mos2, mos_fig2 = mosaic(FILE=mosaic_file, return_ax=True)

    for c in r: # for each cell type in results
        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
            type = round(celldat[ind, 1])
            sym = find_shape_color(type, c)
            loc = celldat[ind, 2:4][0]

            ax.plot(r[c][cone, 2], r[c][cone, 1], sym)
            ax.plot(-r[c][cone, 2], -r[c][cone, 1], sym, mec='k', mew=2,
                     alpha=0.5)

            s_weight = 1 - (abs(r[c][cone, 2]) + abs(r[c][cone, 1]))
            if s_weight > 0.1:
                mos.plot(loc[0], loc[1], 'ko', fillstyle='none', mew=2)

            mos2.plot(loc[0], loc[1], 'o', markersize=14, fillstyle='full',
                      color=[abs(r[c][cone, 1]), abs(r[c][cone, 2]), s_weight])
            #mos2.plot(loc[0], loc[1], sym, mew=0, markersize=6)


    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    mos.set_xlim([35, 90])
    mos.set_ylim([35, 90])

    mos2.set_xlim([35, 90])
    mos2.set_ylim([35, 90])

    fig.savefig('results/img/cone_inputs.svg', edgecolor='none')
    mos_fig.savefig('results/img/cone_inputs_mosaic.svg', edgecolor='none')
    mos_fig2.savefig('results/img/cone_inputs_mosaic2.svg', edgecolor='none')

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

