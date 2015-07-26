from __future__ import division
import numpy as np
import matplotlib.pylab as plt
import scipy.spatial as spat

from base import plot as pf
from base import files as f

from util import get_cell_list
from plot.plot_mosaic import mosaic
import analysis as an


def cone_inputs(d, model, mosaic_file, cell_type='bp', block_plots=True,
                cone_contrast=[48.768, 22.265, 18.576]):
    '''
    '''
    celldat = np.genfromtxt('results/txt_files/nn_results.txt')

    fig = plt.figure(figsize=(6,6))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)

    # build diamond plot
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

    # get response
    r = an.response(d, cell_type, 'cone_inputs', 
                    cone_contrast=cone_contrast)

    # get mosaic plot
    mos, mos_fig = mosaic(model, FILE=mosaic_file, return_ax=True)
    mos2, mos_fig2 = mosaic(model, FILE=mosaic_file, return_ax=True)

    cnaming = np.genfromtxt('mosaics/' + model + '_white_bkgd.csv', 
                            delimiter=',', skip_header=1)
    newold = np.genfromtxt('mosaics/' + model + '_old_new.csv')

    # get the nearest neighbors to the specified cone
    to_newold = spat.KDTree(newold[:, 2:])
    to_cnaming = spat.KDTree(cnaming[:, :2])
    count = 0

    for c in r: # for each cell type in results
        output = np.zeros((len(r[c][:, 0]), 10))
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
        
            cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]
            mos2.plot(loc[0], loc[1], 'o', markersize=14, fillstyle='full',
                      color=np.abs(cone_weights))

            oldcoord = to_newold.query(loc, 1)
            if oldcoord[0] < 0.1:
                newcoord = newold[oldcoord[1], :2]
                cname_ind = to_cnaming.query(newcoord, 1)
                if cname_ind[0] < 0.1:
                    cnames = cnaming[cname_ind[1], :]

                    output[count, :2] = loc
                    output[count, 2:5] = cone_weights
                    total = cnames[6:].sum()
                    if total > 8:
                        output[count, 5:] = cnames[6:] / total
                        count += 1

    # remove zeros
    output = output[~np.all(output == 0, axis=1)]
    print count 

    # save output
    np.savetxt('results/txt_files/cone_analysis.csv', output)

    # --- plot color names on a diamond plot --- #
    fig1 = plt.figure(figsize=(6,6))
    fig1.set_tight_layout(True)
    ax1 = fig1.add_subplot(111)

    # build diamond plot
    pf.AxisFormat(markersize=8, fontsize=20)
    pf.centerAxes(ax1)
    ax1.spines['left'].set_smart_bounds(False)
    ax1.spines['bottom'].set_smart_bounds(False)
    ax1.axis('equal')

    # Add in diamond boarders
    ax1.plot([-1, 0], [0, 1], 'k')
    ax1.plot([0, 1], [1, 0], 'k')
    ax1.plot([1, 0], [0, -1], 'k')
    ax1.plot([0, -1], [-1, 0], 'k')

    colors = ['w', 'r', 'g', 'b', 'y']
    for i in range(len(output[:, 1])):
        maxind = output[i, 5:].argmax()
        symbol = 'o'
        if output[i, 5 + maxind] < 0.65:
            symbol = '^'

        ax1.plot(output[i, 3], output[i, 2], symbol + colors[maxind],
                 markeredgewidth=2, markeredgecolor='k', alpha=0.5)

    # set come fig params
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    mos.set_xlim([35, 90])
    mos.set_ylim([35, 90])

    mos2.set_xlim([35, 90])
    mos2.set_ylim([35, 90])

    # save figs
    f.make_dir('results/img/' + model)
    fig.savefig('results/img/' + model + '/cone_inputs.svg', edgecolor='none')
    fig1.savefig('results/img/' + model + '/cone_inputs_w_naming.svg',
                edgecolor='none')
    mos_fig.savefig('results/img/' + model + '/cone_inputs_mosaic.svg', 
                    edgecolor='none')
    mos_fig2.savefig('results/img/' + model + '/cone_inputs_mosaic2.svg', 
                     edgecolor='none')

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

