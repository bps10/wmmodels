from __future__ import division
import numpy as np
import matplotlib.pylab as plt
import scipy.spatial as spat

import statsmodels.api as sm
from sklearn import cross_validation
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge

from base import plot as pf
from base import files as f
from base import data as d

from util import get_cell_list
from plot.plot_mosaic import mosaic
import analysis as an


# need to add make color naming an option, not default. Won't work for models
def cone_inputs(d, mod_name, mosaic_file, cell_type='bp', block_plots=True,
                cone_contrast=[48.768, 22.265, 18.576]):
    '''
    '''
    # some options; should go into function options
    args = ['mdscaling']
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
                output, count = get_color_names(output, count,
                                                to_newold, to_simmos, to_cnaming, 
                                                mosaiclist, newold, cnaming, loc, 
                                                cone_weights, celldat, r, c)

        # cleanup output and remove zeros
        output = output[~np.all(output == 0, axis=1)]
        print count 
                
        # save output
        np.savetxt('results/txt_files/' + mod_name + '/cone_analysis.csv', output)

        # compute rg metric and find high purity indices
        rg, high_purity = get_rg_from_output(output, purity_thresh)

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
        if 'mdscaling' in args:
            mdscaling(output, mod_name, high_purity)

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
        if purity_thresh < 1:
            symbol = '^' # means low purity

        if rg[i] < 0:
            color = [0, np.abs(rg[i]), 0]
        else:
            color = [np.abs(rg[i]), 0, 0]

        ax.plot(output[i, 3], output[i, 2], symbol, color=color,
                 markeredgewidth=2, markeredgecolor='k', alpha=0.5)

    fig1.savefig('results/img/' + mod_name + '/cone_inputs_w_naming.svg',
                edgecolor='none')


def mdscaling(output, mod_name, high_purity=None):
    if high_purity is not None:
        output = output[high_purity, :]
    cols = [2, 3, 4] # 10:27 neighbors
    predictors = output[:, cols]

    # first thing need to transform output into distance matrix
    distance = spat.distance.pdist(predictors, 'euclidean')
    # convert distance (output in vector form) into square form
    distance = spat. distance.squareform(distance)
    # compute the classical multi-dimensional scaling
    config_mat, eigen = d.cmdscale(distance)
    # for classification, find dominant color
    max_color = np.argmax(output[:, 5:10], axis=1)

    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)    
    colors = ['k', 'r', 'g', 'b', 'y']
    for i in range(0, len(max_color)):
        #ax[0].plot(predictors[i, 0], predictors[i, 1], 's',
        #color=colors[max_color[i]])
        ax[0].plot(config_mat[i, 0], config_mat[i, 1], 'o',
                   color=colors[max_color[i]])

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


def get_rg_from_output(output, purity_thresh=0.6):
    '''
    purity_thresh: find cones that have purities higher than this threshold.
    '''
    high_purity = []
    rg = np.zeros((len(output[:, 1]), 1))
    for i in range(len(output[:, 1])):
        maxind = output[i, 5:10].argmax()

        # check if cone has a purity greater than purity_threshold
        if output[i, 5 + maxind] / output[i, 5:10].sum() > purity_thresh:
            high_purity.append(i)

        rg[i] = (output[i, 6] - output[i, 7]) / output[i, 5:10].sum()

    return rg, high_purity


def get_color_names(output, count, to_newold, to_simmos, to_cnaming, 
                    mosaiclist, newold, cnaming, loc, cone_weights, 
                    celldat, r, c):

    # associate cones in model and AO
    oldcoord = to_newold.query(loc, 1)
    moscoord = to_simmos.query(loc, 11)
    if oldcoord[0] < 0.01:
        cone_type = mosaiclist[oldcoord[1], 2]
        newcoord = newold[oldcoord[1], :2]
        cname_ind = to_cnaming.query(newcoord, 1)
        if cname_ind[0] < 0.01:
            cnames = cnaming[cname_ind[1], :]
            total = cnames[6:].sum()

            # make sure more than 8 seen trials and cone is not S
            if total > 8 and cone_type > 0: 
                output[count, :2] = loc
                output[count, 2:5] = cone_weights
                output[count, 5:10] = cnames[6:] # / total
                
                # now need to associate mosaiclist w cone inputs
                j = 10
                for i in range(1, 9): # 10 nearest neighbors
                    ind1 = np.where(celldat[:, 0] == moscoord[1][i])[0]
                    #ind1 = np.random.randint(0, 400, 1)
                    neighbor = r[c][ind1]
                    output[count, j:j + 3] = neighbor
                    j += 3
                count += 1
    return output, count


def compute_s_weight(r, c, cone):
    return 1 - (np.abs(r[c][cone, 2]) + np.abs(r[c][cone, 1]))


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

