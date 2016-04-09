from __future__ import division
import numpy as np
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D

from base import plot as pf
from base import data as dat

import analysis as an
import util

# change the name of this function
def nat_image_analysis(d, model_name, mosaic_file, cell_type, 
                       randomized, block_plots=True, color_cats=True,
                       purity_thresh=0.0, nseeds=1):
    '''
    '''
    # --- params --- #
    rg_metric = False
    background = 'white'

    # MDScaling options
    dims = [0, 1, 2]
    test_size = 0.1
    param_grid = {'C': [1e2, 1e3, 5e3, 1e4, 5e4, 1e5, 1e6, 1e7],
                  'gamma': [0.001, 0.01, 0.05], }
    # -------------- #

    human_subjects = ['wt', 'bps']
    celldat = np.genfromtxt('results/txt_files/' + model_name + '/nn_results.txt')
    celllist = util.get_cell_list(d)
    ncells = len(celllist)
    
    # put responses into a matrix for easy processing
    data_matrix = an.get_data_matrix(d, cell_type)

    # get correlation matrix
    corrmat = an.compute_corr_matrix(data_matrix)

    # compute the classical multi-dimensional scaling
    config_mat, eigen = dat.cmdscale(corrmat)

    # get the location and cone type of each cone
    xy_lms = an.get_cone_xy_lms(d, celldat, celllist)

    # threshold rg that separates red, white, green
    if color_cats:
        # get response
        cone_contrast=[48.768, 22.265, 18.576]
        r = an.response(d, cell_type, 'cone_inputs',
                        cone_contrast=cone_contrast)
        output = an.associate_cone_color_resp(r, celldat, celllist, model_name, 
                                              bkgd=background, randomized=randomized)
        stim_cone_ids = output[:, -1]
        stim_cone_inds = np.zeros((1, len(stim_cone_ids)), dtype='int')
        for cone in range(len(stim_cone_ids)):
            stim_cone_inds[0, cone] = np.where(celldat[:, 0] == stim_cone_ids[cone])[0]

        if rg_metric:
            # break rg into three categories: red, green, white
            rg, high_purity = an.get_rg_from_naming(output[:, 5:10], purity_thresh)
            rg_thresh = 0.5
            red = rg < -rg_thresh
            green = rg > rg_thresh
        else: # use dom response category
            max_cat = np.argmax(output[:, 5:10], axis=1)
            red = max_cat == 1
            green = max_cat == 2
            blue = max_cat == 3
            yellow = max_cat == 4

        color_categories = (yellow * 4 + blue * 3 + red * 2 + green).T
        class_cats = color_categories.copy()
        config_mat = config_mat[stim_cone_inds, :][0]
        data_matrix = data_matrix[stim_cone_inds, :][0]
        ncells = len(class_cats)
    else:
        class_cats = xy_lms[:, 2]

    # MD Scaling
    target_names, class_cats = get_target_names_categories(color_cats, class_cats)
    an.classic_mdscaling(data_matrix, class_cats, param_grid, target_names,
                         dims=dims, display_verbose=False, rand_seed=23453, 
                         Nseeds=nseeds, test_size=test_size)
    # --------------------------------------------------- #

    # plot correlation matrix
    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    ax[0].imshow(corrmat)

    # plot MDS configuration matrix in 2 and 3dim
    ax, fig = pf.get_axes(1, 2, nticks=[3, 3], return_fig=True)
    fig3d = plt.figure()
    ax3d = fig3d.add_subplot(111, projection='3d')
    for cone in range(ncells):
        if class_cats[cone] == 0 and color_cats is False or class_cats[cone] == 3:
            color = [0, 0, 1]
        elif class_cats[cone] == 0 and color_cats is True:  
            color = [0.7, 0.7, 0.7]
        elif class_cats[cone] == 1:
            color = [0, 1, 0]
        elif class_cats[cone] == 2:
            color = [1, 0, 0]
        elif class_cats[cone] == 4:
            color = [0.8, 0.8, 0] # yellow
        else:
            raise TypeError('category type must be int [0, 4]')

        ax[0].plot(config_mat[cone, 0], config_mat[cone, 1], 'o', markersize=8,
                   alpha=0.8, color=color, markeredgecolor='k')
        ax[1].plot(config_mat[cone, 0], config_mat[cone, 2], 'o', markersize=8,
                   alpha=0.8, color=color, markeredgecolor='k')
        ax3d.scatter(config_mat[cone, 0], config_mat[cone, 1], config_mat[cone, 2],
                     'o', c=color)

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax[0].plot(eigen, 'ko')
    

    plt.show()


def get_target_names_categories(color_cats, categories):
    if color_cats:
        target_names = ['white']
        if np.sum(categories == 1) > 1:
            target_names.append('green')
        if np.sum(categories == 2) > 1:
            target_names.append('red')
        if np.sum(categories == 3) > 1:
            target_names.append('blue')
        if np.sum(categories == 4) > 1:
            target_names.append('yellow')

            # in the case of white, red, blue responses, shift blue down to 
            # 2 for SVM purposes
            unique_resp = np.unique(categories)
            if len(unique_resp) == 3 and categories.max() == 3:
                categories[categories > 0] -= 1
    else:
        target_names = ['S', 'M', 'L']

    return target_names, categories
