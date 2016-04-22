from __future__ import division
import numpy as np
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

from base import plot as pf
from base import data as dat

import analysis as an
import util


def classify_analysis(d, model_name, mosaic_file, cell_type, 
                      params, block_plots=True, color_cats=True,
                      purity_thresh=0.0, nseeds=10):
    '''
    '''
    # --- params --- #
    rg_metric = False
    background = 'white'
    cmdscaling = True
    # kernel options=linear, rbf, poly
    kernel = 'linear'

    # MDScaling options
    dims = [0, 1]
    test_size = 0.15
    # if kernel is set to linear only first entry of 'C' is used, gamma ignored
    param_grid = {'C': [1e9],
                  'gamma': [0.0001, 0.001], }
    # -------------- #
    human_subjects = ['wt', 'bps']
    if model_name.lower() not in human_subjects:
        raise('Model must be a human subject with psychopysics data')

    # no need to run a bunch of times since lms is easy to classify    
    if not color_cats:
        nseeds = 1 

    # get some info about the cones
    nn_dat = util.get_nn_dat(model_name)
    celllist = util.get_cell_list(d)
    ncells = len(celllist)
    
    # put responses into a matrix for easy processing
    data_matrix = an.get_data_matrix(d, cell_type)

    # compute distance matrix
    corrmat = an.compute_corr_matrix(data_matrix)

    if cmdscaling:
        # compute the classical multi-dimensional scaling
        config_mat, eigen = dat.cmdscale(corrmat)
    else:
        pca = PCA(n_components=len(dims)).fit(data_matrix)
        config_mat = pca.transform(data_matrix)

    # get the location and cone type of each cone
    xy_lms = an.get_cone_xy_lms(d, nn_dat, celllist)

    # threshold rg that separates red, white, green
    if color_cats:
        # get response
        cone_contrast=[48.768, 22.265, 18.576]
        r = an.response(d, cell_type, 'cone_inputs',
                        cone_contrast=cone_contrast)
        output = an.associate_cone_color_resp(r, nn_dat, celllist, model_name, 
                                              bkgd=background, 
                                              randomized=params['Random_Cones'])
        stim_cone_ids = output[:, -1]
        stim_cone_inds = np.zeros((1, len(stim_cone_ids)), dtype='int')
        for cone in range(len(stim_cone_ids)):
            stim_cone_inds[0, cone] = np.where(nn_dat[:, 0] == 
                                               stim_cone_ids[cone])[0]

        if rg_metric:
            # break rg into three categories: red, green, white
            rg, by, high_purity = an.get_rgby_from_naming(output[:, 5:10], 
                                                          purity_thresh)
            rgby_thresh = 0.5
            red = rg < -rgby_thresh
            green = rg > rgby_thresh
            blue = by < -rgby_thresh
            yellow = by > rgby_thresh
            color_categories = (yellow * 4 + blue * 3 + red * 2 + green).T[0]

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

    # SVM Classify
    print 'running SVM'
    print '\tCMDScaling=' + str(cmdscaling)
    print '\tkernel=' + str(kernel)
    print '\tRGmetric=' + str(rg_metric)
    print '\tbackground=' + background

    target_names, class_cats = get_target_names_categories(color_cats, class_cats)
    clf = an.svm_classify(data_matrix, class_cats, param_grid, target_names, 
                          cmdscaling, dims=dims, display_verbose=True, 
                          rand_seed=2264235, Nseeds=nseeds, test_size=test_size,
                          kernel=kernel)
    # --------------------------------------------------- #
    print 'plotting results from SVM'

    # undo category shift of plotting 
    if background == 'blue' and color_cats:
        class_cats[class_cats > 0] += 1

    # need to order corrmat based on color category
    sort_inds = np.argsort(class_cats)
    sort_data_matrix = data_matrix[sort_inds, :]
    sort_corrmat = an.compute_corr_matrix(sort_data_matrix)
    # plot correlation matrix
    ax, fig1 = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    ax[0].imshow(sort_corrmat)
    # change axes to indicate location of category boundaries

    # plot MDS configuration matrix in 2 and 3dim
    ax, fig2 = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    # add decision function
    xx, yy = np.meshgrid(np.linspace(-1.5, 1.5, 200), np.linspace(-1.5, 1.5, 200))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax[0].contourf(xx, yy, -Z, cmap=plt.cm.Paired, alpha=0.8)
                         
    '''fig3 = plt.figure()
    ax3d = fig3.add_subplot(111, projection='3d')'''
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
        '''ax[1].plot(config_mat[cone, 0], config_mat[cone, 2], 'o', markersize=8,
                   alpha=0.8, color=color, markeredgecolor='k')
        ax3d.scatter(config_mat[cone, 0], config_mat[cone, 1], config_mat[cone, 2],
                     'o', c=color)'''

    # save figs
    savedir = util.get_save_dirname(params, model_name)
    if params['Random_Cones']:
        savedir += 'randomized_'
    #fig1.savefig(savename + '_corr_matrix.eps', edgecolor='none')
    fig2.savefig(savedir + 'low_dim_rep.eps', edgecolor='none')
    #fig3.savefig(savename + '_3dplot.eps', edgecolor='none')

    if cmdscaling:
        ax, fig4 = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
        ax[0].plot(eigen, 'ko')
        fig4.savefig(savedir + 'eigenvals.eps', edgecolor='none')

    plt.show(block=block_plots)


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
