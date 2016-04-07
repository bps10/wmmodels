from __future__ import division
import numpy as np
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D

from base import plot as pf
from base import data as dat

import analysis as an
import util

def nat_image_analysis(d, model_name, mosaic_file, cell_type, block_plots, 
                       purity_thresh=0.0):
    '''
    '''
    color_cats = True

    celldat = np.genfromtxt('results/txt_files/' + model_name + '/nn_results.txt')
    celllist = util.get_cell_list(d)
    ncells = len(celllist)
    
    # get correlation matrix
    corrmat = an.compute_corr_matrix(d, cell_type)

    # compute the classical multi-dimensional scaling
    config_mat, eigen = dat.cmdscale(corrmat)

    # get the location and cone type of each cone
    xy_lms = an.get_cone_xy_lms(d, celldat, celllist)

    # get response
    cone_contrast=[48.768, 22.265, 18.576]
    r = an.response(d, cell_type, 'cone_inputs',
                    cone_contrast=cone_contrast)
    output = an.associate_cone_color_resp(r, celldat, celllist, model_name, 
                                       bkgd='white', randomize=False)
    stim_cone_ids = output[:, -1]
    stim_cone_inds = np.zeros((1, len(stim_cone_ids)), dtype='int')
    for cone in range(len(stim_cone_ids)):
        stim_cone_inds[0, cone] = np.where(celldat[:, 0] == stim_cone_ids[cone])[0]

    # break rg into three categories: red, green, white
    rg, high_purity = an.get_rg_from_naming(output[:, 5:10], purity_thresh)
    # threshold rg that separates red, white, green
    rg_thresh = 0.5 
    red = rg < -rg_thresh
    green = rg > rg_thresh
    color_categories = red * 2 + green
    color_categories = color_categories.T[0]

    # plot correlation matrix
    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    ax[0].imshow(corrmat)

    # plot MDS configuration matrix in 2 and 3dim
    ax, fig = pf.get_axes(1, 2, nticks=[3, 3], return_fig=True)
    fig3d = plt.figure()
    ax3d = fig3d.add_subplot(111, projection='3d')

    if color_cats:
        class_cats = color_categories
        config_mat = config_mat[stim_cone_inds, :][0]
        ncells = len(color_categories)
    else:
        class_cats = xy_lms[:, 2]
    for cone in range(ncells):
        if class_cats[cone] == 0 and color_cats is False:
            color = [0, 0, 1]
        elif class_cats[cone] == 0 and color_cats is True:  
            color = [0.7, 0.7, 0.7]
        elif class_cats[cone] == 1:
            color = [0, 1, 0]
        elif class_cats[cone] == 2:
            color = [1, 0, 0]
        else:
            raise TypeError('lms type must be 0, 1, 2')

        ax[0].plot(config_mat[cone, 0], config_mat[cone, 1], 'o', markersize=8,
                   alpha=0.8, color=color, markeredgecolor='k')
        ax[1].plot(config_mat[cone, 0], config_mat[cone, 2], 'o', markersize=8,
                   alpha=0.8, color=color, markeredgecolor='k')
        ax3d.scatter(config_mat[cone, 0], config_mat[cone, 1], config_mat[cone, 2],
                     'o', c=color)

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax[0].plot(eigen, 'ko')
    

    plt.show()


'''
    # threshold rg that separates red, white, green
    rg_thresh = 0.5
    # dimensions to use from MDS in SVD (list)
    dims = [0, 1, 2]
    # cols 2, 3, 4 = stimulated cones; 10:27 = neighbors
    cols = [2, 3, 4, 10, 11, 12, 13, 14, 15]#, 16, 17, 18, 19, 20]
    param_grid = {'C': [1e2, 1e3, 5e3, 1e4, 5e4, 1e5, 1e6, 1e7],
                  'gamma': [0.001, 0.01, 0.05], }

    # keep only high purity cones if a vector is passed
    if high_purity is not None:
        output = output[high_purity, :]
        rg = rg[high_purity]
    
    # break rg into three categories: red, green, white
    red = rg < -rg_thresh
    green = rg > rg_thresh
    color_categories = red + green * 2
    color_categories = color_categories.T[0]

    # select out the predictors
    predictors = output[:, cols]
'''
