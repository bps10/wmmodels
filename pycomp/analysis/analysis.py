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


def classic_mdscaling(dist_mat, categories, display_verbose=False,
                      rand_seed=23453, Nseeds=100, test_size=0.1):
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
    # search grid params in svm
    param_grid = 
    # ------------------- #

    '''
    # set up random numbers
    np.random.seed(rand_seed)
    rand_seeds = np.round(np.random.rand(Nseeds, 1) * 10000)
    
    # set up data containers for results
    total_y_true = []
    total_y_pred = []

    for seed in rand_seeds:
        # Split into a training set and a test set using a stratified k fold
        X_train, X_test, y_train, y_test = train_test_split(
            predictors, categories, test_size=test_size,
            random_state=int(seed[0]))

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
    ncells = len(celllist)

    # Load params from meta data
    nsteps = num(d['const']['MOO_tn']['val']) # time steps
    ntrials = num(d['ntrial'])

    normalize = False    
    #cells = get_cell_type(cell_type)
    if cell_type == 'rgc':
        resp_ind = 'p'
    else:
        resp_ind = 'x'

    cellkey = get_cell_data(d, cell_type) 
        
    data_mat = np.zeros((ncells, nsteps * ntrials))
    for t in range(ntrials):
        for i, r in enumerate(cellkey['tr'][t]['r']):
            data_mat[i, t * nsteps:(t + 1) * nsteps] = d['tr'][t]['r'][r][resp_ind]
    corrmat = 1 - np.corrcoef(data_mat)

    return corrmat


def compute_cone_weights():
    for c in r: # for each cell type in results
        output = np.zeros((len(r[c][:, 0]), 37))
        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
            loc = celldat[ind, 2:4][0]
            
            # compute s weight for mosaic plot
            s_weight = r[c][cone, 0] #compute_s_weight(r, c, cone)
            
            # compute cone weights (re-order to L, M, S)
            cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]


def get_cone_xy_lms(d, celldat, celllist):
    '''Find the xy position and cone type (lms) of a population of cones.
    '''    
    ncells = len(celllist)
    
    xylms = np.zeros((ncells, 3))
    t = 0 # only need to look at first trial
    for cone in range(ncells): # for each cell
        ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
        loc = celldat[ind, 2:4][0]
        lms = celldat[ind, 1]
        xylms[cone, :] = np.concatenate([loc, lms])
    return xylms


def associate_cone_color_resp(r, celldat, celllist, mod_name, bkgd='white',
                              randomize=False, cell_type='bp'):
    '''
    '''
    # first get data
    cnaming = np.genfromtxt('mosaics/' + mod_name + '_' + bkgd + '_bkgd.csv', 
                            delimiter=',', skip_header=1)
    newold = np.genfromtxt('mosaics/' + mod_name + '_old_new.csv')
    mosaiclist = np.genfromtxt('mosaics/' + mod_name + '_mosaic.txt')
    
    # get the nearest neighbors to the specified cone
    to_newold = spat.KDTree(newold[:, 2:])
    to_cnaming = spat.KDTree(cnaming[:, :2])
    to_simmos = spat.KDTree(mosaiclist[:, :2])

    count = 0
    c = cell_type
    output = np.zeros((len(r[c][:, 0]), 39))
    for cone in range(0, len(r[c][:, 0])):
        ind = np.where(celldat[:, 0] == float(celllist[cone]))[0]
        loc = celldat[ind, 2:4][0]

        # compute s weight for mosaic plot
        s_weight = r[c][cone, 0] #compute_s_weight(r, c, cone)

        # compute cone weights (re-order to L, M, S)
        cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]

        # --- match up color names and modeled output --- #
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
                    output[count, 37] = cone_type
                    output[count, 38] = celldat[ind, 0]
                    output[count, 5:10] = cnames[6:] # / total
                
                    # now need to associate mosaiclist w cone inputs
                    j = 10
                    for i in range(1, 9): # 10 nearest neighbors
                        if randomize:
                            ind1 = np.random.randint(0, 400, 1)
                        else:
                            ind1 = np.where(celldat[:, 0] == moscoord[1][i])[0]
                            
                        neighbor = r[c][ind1]
                        output[count, j:j + 3] = neighbor
                        j += 3
                    count += 1
    # cleanup output and remove zeros
    output = output[~np.all(output == 0, axis=1)]

    return output


def get_rg_from_naming(naming, purity_thresh=None):
    '''
    purity_thresh: find cones that have purities higher than this threshold.
    '''
    if purity_thresh is None:
        purity_thresh = 0

    high_purity = []
    rg = np.zeros((len(naming[:, 1]), 1))
    for i in range(len(naming[:, 1])):
        maxind = naming[i, :].argmax()

        # check if cone has a purity greater than purity_threshold
        if naming[i, maxind] / naming[i, :].sum() > purity_thresh:
            high_purity.append(i)
        
        # green - red / total
        rg[i] = (naming[i, 2] - naming[i, 1]) / naming[i, :].sum()

    return rg, high_purity


def compute_s_weight(r, c, cone):
    # not currently being used
    return 1 - (np.abs(r[c][cone, 2]) + np.abs(r[c][cone, 1]))


def compute_psth(spike_times, time_ms, delta_t=16):
    ''' delta_t = 16 # ms (size of bins for spike rate)
    '''
    bins = np.arange(0, time_ms, delta_t)
    count, bins = np.histogram(spike_times, bins=bins)
    Hz = count / (delta_t / 1000)
    return Hz
