from __future__ import division
import numpy as np
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D

from base import plot as pf
from base import data as dat

import analysis as an


def nat_image_analysis(d, model, mosaic_file, cell_type, block_plots):
    '''
    '''

    celldat = np.genfromtxt('results/txt_files/' + model + '/nn_results.txt')

    # get correlation matrix
    corrmat = an.compute_corr_matrix(d, cell_type)

    # compute the classical multi-dimensional scaling
    config_mat, eigen = dat.cmdscale(corrmat)

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    ax[0].imshow(corrmat)

    ax, fig = pf.get_axes(1, 2, nticks=[3, 3], return_fig=True)
    ax[0].plot(config_mat[:, 0], config_mat[:, 1], 'ko', markersize=8,
               alpha=0.8)
    ax[1].plot(config_mat[:, 0], config_mat[:, 2], 'ko', markersize=8,
               alpha=0.8)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(config_mat[:, 0], config_mat[:, 1], config_mat[:, 2],
               'ko')

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax[0].plot(eigen, 'ko')
    

    plt.show()

