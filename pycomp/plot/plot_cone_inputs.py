from __future__ import division

import numpy as np
import matplotlib.pylab as plt
import scipy.spatial as spat

import statsmodels.api as sm
from sklearn import cross_validation
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.svm import SVC
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import train_test_split

from base import plot as pf
from base import files as f
from base import data as dat

from util import get_cell_list
from plot.plot_mosaic import mosaic
import analysis as an


# need to add make color naming an option, not default. Won't work for models
def cone_inputs(d, mod_name, mosaic_file, cell_type='bp', block_plots=True,
                cone_contrast=[48.768, 22.265, 18.576]):
    '''
    '''
    # some options; should go into function options
    args = ['cmdscaling']
    purity_thresh = 0.0

    celldat = np.genfromtxt('results/txt_files/' + mod_name + '/nn_results.txt')

    # get results
    celllist = get_cell_list(d)

    # get response
    r = an.response(d, cell_type, 'cone_inputs',
                    cone_contrast=cone_contrast)

    if 'cone_weights' in args:
        plot_cone_weights(r, celldat, celllist, mod_name, mosaic_file)

    # -------------------------------------------------
    # if model is a human subject make additional plots
    # -------------------------------------------------
    if mod_name.lower() in ['wt', 'bps']:
        # first get data
        cnaming = np.genfromtxt('mosaics/' + mod_name + '_white_bkgd.csv', 
                                delimiter=',', skip_header=1)
        newold = np.genfromtxt('mosaics/' + mod_name + '_old_new.csv')
        mosaiclist = np.genfromtxt('mosaics/' + mod_name + '_mosaic.txt')

        # get the nearest neighbors to the specified cone
        to_newold = spat.KDTree(newold[:, 2:])
        to_cnaming = spat.KDTree(cnaming[:, :2])
        to_simmos = spat.KDTree(mosaiclist[:, :2])
        count = 0

        for c in r: # for each cell type in results
            output = np.zeros((len(r[c][:, 0]), 37))
            for cone in range(0, len(r[c][:, 0])):
                ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
                loc = celldat[ind, 2:4][0]

                # compute s weight for mosaic plot
                s_weight = r[c][cone, 0] #compute_s_weight(r, c, cone)

                # compute cone weights (re-order to L, M, S)
                cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]

                # match up color names and modeled output
                output, count = an.get_color_names(output, count,
                                                to_newold, to_simmos, to_cnaming,
                                                mosaiclist, newold, cnaming, loc,
                                                cone_weights, celldat, r, c)

        # cleanup output and remove zeros
        output = output[~np.all(output == 0, axis=1)]
        print 'N cells: ', count 
                
        # save output
        np.savetxt('results/txt_files/' + mod_name + '/cone_analysis.csv', 
                   output)

        # compute rg metric and find high purity indices
        if args is not []:
            rg, high_purity = an.get_rg_from_naming(output[:, 5:10], purity_thresh)

        # plot color names
        if 'color_names' in args:
            plot_color_names(rg, high_purity, output, mod_name)

        # linear model
        if 'linear_model' in args:
            fit_linear_model(rg, output, mod_name, opponent=True)

        # S-cone distance analysis and plot
        if 's_cone_dist' in args:
            s_cone_dist_analysis(rg, output, mod_name)

        # multidemensional scaling
        if 'cmdscaling' in args:
            classic_mdscaling(output, mod_name, rg, high_purity)

        # support vector machine
        if 'svm' in args:
            svm_classify(output, mod_name, rg, high_purity)

    plt.show(block=block_plots)


def plot_cone_weights(r, celldat, celllist, mod_name, mosaic_file,
                      block_plots=True):
    '''
    '''
    fig = plt.figure(figsize=(6,6))
    fig.set_tight_layout(True)
    ax = fig.add_subplot(111)

    # build diamond plot
    pf.AxisFormat(markersize=8, fontsize=9, tickdirection='inout')
    pf.centerAxes(ax)
    ax.spines['left'].set_smart_bounds(False)
    ax.spines['bottom'].set_smart_bounds(False)
    ax.axis('equal')

    # Add in diamond boarders
    ax.plot([-1, 0], [0, 1], 'k')
    ax.plot([0, 1], [1, 0], 'k')
    ax.plot([1, 0], [0, -1], 'k')
    ax.plot([0, -1], [-1, 0], 'k')

    # set come fig params
    ax.set_xlim([-1.1, 1.1])
    ax.set_ylim([-1.1, 1.1])

    # get mosaic plot
    mos, mos_fig = mosaic(mod_name, FILE=mosaic_file, return_ax=True)
    mos2, mos_fig2 = mosaic(mod_name, FILE=mosaic_file, return_ax=True)

    for c in r: # for each cell type in results
        output = np.zeros((len(r[c][:, 0]), 37))
        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
            type = round(celldat[ind, 1])
            sym = find_shape_color(type, c)
            loc = celldat[ind, 2:4][0]

            # add data to diamond plot
            ax.plot(r[c][cone, 2], r[c][cone, 1], sym)
            ax.plot(-r[c][cone, 2], -r[c][cone, 1], sym, mec='k', mew=2,
                     alpha=0.5)

            # compute s weight for mosaic plot
            s_weight = r[c][cone, 0] #compute_s_weight(r, c, cone)

            # compute cone weights
            cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]

            if s_weight > 0.1:
                mos.plot(loc[0], loc[1], 'ko', fillstyle='none', mew=2)

            mos2.plot(loc[0], loc[1], 'o', markersize=14, fillstyle='full',
                      color=np.abs(cone_weights))

    mos.set_xlim([35, 90])
    mos.set_ylim([35, 90])

    mos2.set_xlim([35, 90])
    mos2.set_ylim([35, 90])

    # save figs
    f.make_dir('results/img/' + mod_name)
    fig.savefig('results/img/' + mod_name + '/cone_inputs.svg', edgecolor='none')
    mos_fig.savefig('results/img/' + mod_name + '/cone_inputs_mosaic.svg', 
                    edgecolor='none')
    mos_fig2.savefig('results/img/' + mod_name + '/cone_inputs_mosaic2.svg', 
                     edgecolor='none')


def plot_color_names(rg, purity_thresh, output, mod_name):
    '''
    '''
    # --- plot color names on a diamond plot --- #
    fig1 = plt.figure(figsize=(6,6))
    fig1.set_tight_layout(True)
    ax = fig1.add_subplot(111)

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

    for i in range(len(rg)):
        maxind = output[i, 5:10].argmax()
        symbol = 'o'
        # check if cone has a purity greater threshold
        if purity_thresh is not None and purity_thresh < 1:
            symbol = '^' # means low purity

        if rg[i] < 0:
            color = [0, np.abs(rg[i]), 0]
        else:
            color = [np.abs(rg[i]), 0, 0]

        ax.plot(output[i, 3], output[i, 2], symbol, color=color,
                 markeredgewidth=2, markeredgecolor='k', alpha=0.5)

    fig1.savefig('results/img/' + mod_name + '/cone_inputs_w_naming.svg',
                edgecolor='none')


def classic_mdscaling(output, mod_name, rg, high_purity=None):
    '''
    '''
    # ----- params ----- #
    # Don't use if Nseeds > 1
    display_verbose = False
    # used in train_test_split
    rand_seed = 23456 
    # number of times to resample data set
    Nseeds = 100
    # proportion of data set to leave for test
    test_size = 0.1
    # dimensions to use from MDS in SVD (list)
    dims = [0, 1, 2]
    # threshold rg that separates red, white, green
    rg_thresh = 0.5
    # search grid params in svm
    param_grid = {'C': [1e2, 1e3, 5e3, 1e4, 5e4, 1e5, 1e6, 1e7],
                  'gamma': [0.001, 0.01, 0.05], }
    # cols 2, 3, 4 = stimulated cones; 10:27 = neighbors
    cols = [2, 3, 4, 10, 11, 12, 13, 14, 15]#, 16, 17, 18, 19, 20]

    metric = 'correlation'
    # ------------------- #

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

    # set up random numbers
    np.random.seed(rand_seed)
    rand_seeds = np.round(np.random.rand(Nseeds, 1) * 10000)
    
    # set up data containers for results
    total_y_true = []
    total_y_pred = []

    for seed in rand_seeds:
        # Split into a training set and a test set using a stratified k fold
        X_train, X_test, y_train, y_test = train_test_split(
            predictors, color_categories, test_size=test_size,
            random_state=int(seed[0]))

        # first thing need to transform output into distance matrix
        # many to choose from including: euclidean, correlation, cosine, 
        # cityblock, minkowski, hamming, etc
        dist_train = spat.distance.pdist(X_train, metric)
        dist_test = spat.distance.pdist(X_test, metric)

        # convert distance (output in vector form) into square form
        dist_train = spat.distance.squareform(dist_train)
        dist_test = spat.distance.squareform(dist_test)

        # compute the classical multi-dimensional scaling
        config_mat, eigen = dat.cmdscale(dist_train)
        config_mat_test, eigen = dat.cmdscale(dist_test)

        # Classify with SVM
        clf = GridSearchCV(SVC(kernel='rbf', class_weight='balanced'), 
                           param_grid)
        clf = clf.fit(config_mat[:, dims], y_train)

        # predict test data with fit model
        y_pred = clf.predict(config_mat_test[:, dims])

        if display_verbose:
            print("Best estimator found by grid search:")
            print(clf.best_estimator_)    
            # Quantitative evaluation of the model quality on the test set
            print("Predicting color names on the test set")

        # save output
        total_y_true.append(y_test)
        total_y_pred.append(y_pred)

    # print the summary results
    total_y_true = np.asarray(total_y_true).flatten()
    total_y_pred = np.asarray(total_y_pred).flatten()
    target_names = ['white', 'red', 'green']

    print 'N simulations: ', Nseeds
    print 'Dimensions used: ', dims 
    print 'rg thresh: ', rg_thresh
    print param_grid
    print 'cols used: ', cols

    n_classes = 3
    print classification_report(total_y_true, total_y_pred,
                                target_names=target_names)
    print confusion_matrix(total_y_true, total_y_pred, labels=range(n_classes))

    # ---------- Plot some results --------- #
    # first sort predictors for plotting purposes
    rg = rg.T[0]
    sort_inds = np.argsort(rg)
    predictors = predictors[sort_inds, :]
    rg = rg[sort_inds]

    # compute dissimilarity matrix
    plot_dist_train = spat.distance.pdist(predictors, metric)
    plot_dist_train = spat.distance.squareform(plot_dist_train)

    # plot dissimilarity matrix for whole data set    
    imax, imgfig = pf.get_axes(1, 1, nticks=[4, 4], return_fig=True)
    imax[0].imshow(plot_dist_train, interpolation=None,
                   cmap=plt.cm.viridis, 
                   extent=[rg.min(), rg.max(), rg.max(), rg.min()])
    ticks = [rg.min(), find_nearest(rg, -0.5), find_nearest(rg, 0),
             find_nearest(rg, 0.5), rg.max()]
    imax[0].set_xticks(ticks)
    imax[0].set_yticks(ticks)

    # plot projection of training data in mds space
    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    for i in range(0, len(y_train)):
        if y_train[i] == 1:
            color = [1, 0, 0]
        elif y_train[i] == 2:
            color = [0, 1, 0]
        else:
            color = [0, 0, 0]
        
        ax[0].plot(config_mat[i, dims[0]], config_mat[i, dims[1]], 'o',
                   color=color)

    ax[0].set_xlabel('dimension 1')
    ax[0].set_ylabel('dimension 2')
    
    # save functions
    fig.savefig('results/img/' + mod_name + '/mdscaling.svg',
                edgecolor='none')    
    imgfig.savefig('results/img/' + mod_name + '/mds_dissimilarity.svg',
                edgecolor='none')    


def s_cone_dist_analysis(rg, output, mod_name):

    # checkout proximity to s cone and rg metric
    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax = ax[0]
    inds = output[:, 4] < 0.4 # eliminate S-cone center cells
    ax.plot(output[inds, 4], np.abs(rg[inds]), 'ko')
    
    ax.set_xlabel('S-cone weight')
    ax.set_ylabel('absolute value rg response')

    # See if there is a relationship between color names and distance to S-cone
    X = sm.add_constant(output[inds, 4], prepend=True)
    OLSmodel = sm.OLS(rg[inds], X)
    res = OLSmodel.fit()
    print '\n\n\n'
    print res.rsquared

    fig.savefig('results/img/' + mod_name + '/s_cone_distance.svg',
                edgecolor='none')    


def fit_linear_model(rg, output, mod_name, opponent=True):
    # Switch depending upon opponent option
    if not opponent:
        predictors = output[:, [2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 
                                19, 20, 21, 22, 23, 24, 25, 26, 27]] 
    else:
        # organize in opponent fashion
        N = 2 # center cone and nearest x
        predictors = np.zeros((len(output[:, 0]), N + 1))
        _inds = [2, 10, 13, 16, 19, 22, 25, 28, 31]
        for i in range(N + 1):
            predictors[:, i] = ((output[:, _inds[i]] +
                                 output[:, _inds[i] + 2])
                                - output[:, _inds[i] + 1])
    # cone weights in L, M, S order
    inds = [2, 10, 13]
    X = sm.add_constant(predictors, prepend=True)
    OLSmodel = sm.OLS(rg, X) #GLM(rg, X)
    res = OLSmodel.fit()
    #print res.rsquared
    print '\n\n\n'
    print (res.summary())

    linear_reg = True
    ridge_reg = False

    ## Linear regression on training data
    clfs = []
    if linear_reg:
        clfs.append(LinearRegression())
    if ridge_reg:
        clfs.append(Ridge())

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax = ax[0]
    Ntrials = 100
    mae = np.zeros((Ntrials, 1))
    for i in range(Ntrials):
        x_train, x_test, y_train, y_test = cross_validation.train_test_split(
            predictors, rg, test_size=0.15)

        for clf in clfs:

            clf.fit(x_train, y_train) 
            mae[i] = mean_absolute_error(y_test, clf.predict(x_test))    

            ax.plot(y_test, clf.predict(x_test), 'ko', alpha=0.5)

    print '\n\n'
    print mae.mean(), mae.std()

    ax.set_xlabel('observed')
    ax.set_ylabel('predicted')
    ax.set_aspect('equal')

    if y_train.min() < 0:
        ax.plot([-1, 1], [-1, 1], 'k-')
        ax.set_ylim([-1, 1])
        ax.set_xlim([-1, 1])
    else:
        ax.plot([0, 1], [0, 1], 'k-')
    fig.savefig('results/img/' + mod_name + '/cone_inputs_model_error.svg',
                edgecolor='none')


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


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

