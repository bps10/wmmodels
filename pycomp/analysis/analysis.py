from __future__ import division
import numpy as np
import scipy.spatial as spat
from util import get_time, get_cell_data, get_cell_list, get_cell_type, num


def response(d, cell_type, analysis_type,
             cone_contrast=[49, 22, 19]):
    '''
    '''
    # Get cell list from data keys
    celllist = get_cell_list(d)

    # Load params from meta data
    N = num(d['const']['MOO_tn']['val']) # time steps

    time = get_time(d)
    ncells = len(celllist)
    time_bin = 15

    normalize = False
    # analysis specific parameters
    if analysis_type == 'cone_inputs':
        normalize = True
        tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
    elif analysis_type == 'tf':
        sf = num(d['const']['sf']['val']) # spatial freq (cpd)
        tf = num(d['const']['VAR_tf']['val']) # temporal frequency (Hz)
    elif analysis_type == 'sf':
        sf = num(d['const']['VAR_sf']['val']) # spatial freq (cpd)
        tf = num(d['const']['tf']['val']) # temporal frequency (Hz)
    else:
        raise InputError('analysis type not supported (cone_input, sf, tf)')
    
    cells = get_cell_type(cell_type)
    if cell_type == 'rgc':
        resp_ind = 'p'
    else:
        resp_ind = 'x'

    resp = {}
    for c in cells: # for each cell type
        resp[c] = np.zeros((ncells * len(cells), int(d['ntrial'])))

        keys = get_cell_data(d, c) 
        
        for t in range(d['ntrial']): # for each trial
            for i, r in enumerate(keys['tr'][t]['r']): # for each cell

                # handle case where TF is changing
                if analysis_type == 'tf':
                    _tf = int(tf[t])
                else:
                    _tf = int(tf)

                cell = d['tr'][t]['r'][r][resp_ind]

                if cell_type == 'rgc':
                    cell = compute_psth(cell, time.max(), delta_t=10)

                fft =  np.fft.fft(cell)
                                
                if analysis_type == 'cone_inputs':
                    amp  = np.real(fft[_tf]) * 2 / N
                    resp[c][i, t] = amp / cone_contrast[t]
                else: 
                    amp  = np.abs(fft[_tf]) * 2 / N
                    resp[c][i, t] = amp

        if normalize:
            resp[c] = (resp[c].T / np.abs(resp[c]).sum(1)).T

    return resp


def classic_mdscaling(output, mod_name, rg):
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
        metric = 'correlation'
        dist_train = spat.distance.pdist(X_train, metric)
        dist_test = spat.distance.pdist(X_test, metric)

        # convert distance (output in vector form) into square form
        dist_train = spat.distance.squareform(dist_train)
        dist_test = spat.distance.squareform(dist_test)

        # compute the classical multi-dimensional scaling
        config_mat, eigen = d.cmdscale(dist_train)
        config_mat_test, eigen = d.cmdscale(dist_test)

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



def compute_corr_matrix(d, cell_type):
    '''
    '''
    # Get cell list from data keys
    celllist = get_cell_list(d)

    # Load params from meta data
    N = num(d['const']['MOO_tn']['val']) # time steps

    time = get_time(d)
    ncells = len(celllist)
    time_bin = 15

    normalize = False    
    cells = get_cell_type(cell_type)
    if cell_type == 'rgc':
        resp_ind = 'p'
    else:
        resp_ind = 'x'

    cellkey = get_cell_data(d, 'bp') 
        
    t = 0 # trial 0
    r1 = cellkey['tr'][t]['r'][0]
    data_mat = np.zeros((ncells, len(d['tr'][t]['r'][r1][resp_ind])))
    for i, r in enumerate(cellkey['tr'][t]['r']):
        data_mat[i, :] = d['tr'][t]['r'][r][resp_ind]
    corrmat = 1 - np.corrcoef(data_mat)

    '''metric = 'correlation'
    distances = spat.distance.pdist(data_mat, metric)
    corrmat = spat.distance.squareform(distances)'''

    return corrmat


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
