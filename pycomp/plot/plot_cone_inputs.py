from __future__ import division

import numpy as np
import matplotlib.pylab as plt
import scipy.spatial as spat

import statsmodels.api as sm
from sklearn import cross_validation
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.cross_validation import train_test_split

from base import plot as pf
from base import data as dat

import util
from plot.plot_mosaic import mosaic
import analysis as an


# need to add make color naming an option, not default. Won't work for models
def cone_inputs(d, params, cell_type='bp', 
                cone_contrast=[48.768, 22.265, 18.576]):
    '''
    '''
    # some options; should go into function options
    args = ['cone_weights', 's_cone_weights']
    purity_thresh = 0.0

    celldat = np.genfromtxt('results/txt_files/' + params['model_name'] + 
                            '/nn_results.txt')

    # get some info about the cones
    nn_dat = util.get_nn_dat(params['model_name'])
    celllist = util.get_cell_list(d)

    # get response
    r = an.response(d, cell_type, 'cone_inputs',
                    cone_contrast=cone_contrast)

    if 'cone_weights' in args:
        plot_cone_weights(r, celldat, celllist, params)


    if 's_cone_weights' in args:
        s_cone_weights(d, cone_contrast, celllist, celldat, params)

    # -------------------------------------------------
    # if model is a human subject make additional plots
    #  * these routines have been largely superseded by 
    #  * plot_classify
    # -------------------------------------------------
    if params['model_name'].lower() in ['wt', 'bps'] and ('linear_model' in args or
                                                's_cone_dist' in args or
                                                'color_names' in args):

        # match up color names and modeled results
        results = an.associate_cone_color_resp(r, nn_dat, celllist, 
                                              params['model_name'], bkgd='white',
                                              randomized=False,
                                              cell_type='bp')

        # cleanup results and remove zeros
        results = results[~np.all(results == 0, axis=1)]
        print 'N cells: ', len(results[:, 0])
                
        # save results
        np.savetxt('results/txt_files/' + params['model_name'] + '/cone_analysis.csv', 
                   results)

        # compute rg metric and find high purity indices
        if args is not []:
            # break rg into three categories: red, green, white
            rg, by, high_purity = an.get_rgby_from_naming(results[:, 5:10], 
                                                          purity_thresh)

        # plot color names
        if 'color_names' in args:
            plot_color_names(rg, high_purity, results, params)

        # linear model
        if 'linear_model' in args:
            fit_linear_model(rg, results, params, opponent=True)

        # S-cone distance analysis and plot
        if 's_cone_dist' in args:
            s_cone_dist_analysis(rg, results, params)

    plt.show(block=params['block_plots'])


def plot_cone_weights(r, celldat, celllist, params):
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
    mos, mos_fig = mosaic(params['model_name'], FILE=params['mosaic_file'], 
                          return_ax=True)

    for c in r: # for each cell type in results
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
            
            s_rgb = 1 - np.abs(s_weight)
            mos.plot(loc[0], loc[1], 'o', fillstyle='none', mew=4,
                     mec=[s_rgb, s_rgb, s_rgb])

    mos.set_xlim([35, 90])
    mos.set_ylim([35, 90])

    # save figs
    savedir = util.get_save_dirname(params, check_randomized=True)
    fig.savefig(savedir + 'cone_inputs.svg', edgecolor='none')
    mos_fig.savefig(savedir + 'cone_inputs_mosaic.eps', edgecolor='none')


def s_cone_weights(d, cone_contrast, celllist, celldat, params):
    '''
    '''

    lm_midgets = an.compute_s_dist_cone_weight(d, celldat, celllist, 
                                               params['mosaic_file'], 
                                               cone_contrast,
                                               species='human')
    # plotting routines    
    ax, fig1 = pf.get_axes(1, 1, nticks=[4, 5], return_fig=True)
    ax[0].plot(lm_midgets[:, 0], lm_midgets[:, 1], 'ko')

    ax[0].set_xlabel('distance from S-cone (arcmin)')
    ax[0].set_ylabel('S / (L+M+S)')

    # histogram of same data
    ax2, fig2 = pf.get_axes(1, 1, nticks=[4, 5], return_fig=True)
    ax2[0].spines['bottom'].set_smart_bounds(False)

    count, bins = np.histogram(lm_midgets[:, 1], bins=15)
    count = count / count.sum() * 100
    bins, count = pf.histOutline(count, bins)
    ax2[0].plot(bins, count, 'k-')

    ax2[0].set_xlim([0, 1])
    ax2[0].set_ylabel('% of cells')
    ax2[0].set_xlabel('S / (L+M+S)')

    # Save plots
    savedir = util.get_save_dirname(params, check_randomized=True)
    fig1.savefig(savedir + 's_weight_scatter.eps', edgecolor='none')
    fig2.savefig(savedir + 's_weight_hist.eps', edgecolor='none')


def s_cone_dist_analysis(rg, results, model_name):
    '''
    '''
    # checkout proximity to s cone and rg metric
    ax, fig = pf.get_axes(1, 1, nticks=[3, 3], return_fig=True)
    ax = ax[0]
    inds = results[:, 4] < 0.4 # eliminate S-cone center cells
    ax.plot(results[inds, 4], np.abs(rg[inds]), 'ko')
    
    ax.set_xlabel('S-cone weight')
    ax.set_ylabel('absolute value rg response')

    # See if there is a relationship between color names and distance to S-cone
    X = sm.add_constant(results[inds, 4], prepend=True)
    OLSmodel = sm.OLS(rg[inds], X)
    res = OLSmodel.fit()
    print '\n\n\n'
    print res.rsquared

    savedir = util.get_save_dirname(params, check_randomized=True)
    fig.savefig(savedir + 's_cone_distance.svg', edgecolor='none')    


def plot_color_names(rg, purity_thresh, results, params):
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
        maxind = results[i, 5:10].argmax()
        symbol = 'o'
        # check if cone has a purity greater threshold
        if purity_thresh is not None and purity_thresh < 1:
            symbol = '^' # means low purity

        if rg[i] < 0:
            color = [0, np.abs(rg[i]), 0]
        else:
            color = [np.abs(rg[i]), 0, 0]

        ax.plot(results[i, 3], results[i, 2], symbol, color=color,
                 markeredgewidth=2, markeredgecolor='k', alpha=0.5)

    savedir = util.get_save_dirname(params, check_randomized=True)
    fig1.savefig(savedir + 'cone_inputs_w_naming.svg',
                edgecolor='none')


def fit_linear_model(rg, results, params, opponent=True):
    # Switch depending upon opponent option
    if not opponent:
        predictors = results[:, [2, 3, 4, 10, 11, 12, 13, 14, 15, 16, 17, 18, 
                                19, 20, 21, 22, 23, 24, 25, 26, 27]] 
    else:
        # organize in opponent fashion
        N = 2 # center cone and nearest x
        predictors = np.zeros((len(results[:, 0]), N + 1))
        _inds = [2, 10, 13, 16, 19, 22, 25, 28, 31]
        for i in range(N + 1):
            predictors[:, i] = ((results[:, _inds[i]] +
                                 results[:, _inds[i] + 2])
                                - results[:, _inds[i] + 1])
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
    savedir = util.get_save_dirname(params, check_randomized=True)
    fig.savefig(params + 'cone_inputs_model_error.svg',
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

