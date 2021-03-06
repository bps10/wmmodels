from __future__ import division
import numpy as np
import scipy.spatial as spat
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV

from base import data as dat

import util
from util import nearest_neighbor as nn
import plot as pl

def response(d, params):
    '''
    '''
    # Get cell list from data keys
    celllist = util.get_cell_list(d)

    # Load params from meta data
    N = util.num(d['const']['MOO_tn']['val']) # time steps

    time = util.get_time(d)
    ncells = len(celllist)
    time_bin = 15

    normalize = False
    # analysis specific parameters
    if params['analysis_type'] == 'cone_inputs':
        normalize = True
        tf = util.num(d['const']['tf']['val']) # temporal frequency (Hz)
    elif params['analysis_type'] == 'tf':
        sf = util.num(d['const']['sf']['val']) # spatial freq (cpd)
        tf = util.num(d['const']['VAR_tf']['val']) # temporal frequency (Hz)
    elif params['analysis_type'] == 'sf':
        sf = util.num(d['const']['VAR_sf']['val']) # spatial freq (cpd)
        tf = util.num(d['const']['tf']['val']) # temporal frequency (Hz)
    else:
        raise InputError('analysis type not supported (cone_input, sf, tf)')
    
    cells = util.get_cell_type(params['cell_type'])
    if params['cell_type'] == 'rgc':
        resp_ind = 'p'
    else:
        resp_ind = 'x'

    resp = {}
    for c in cells: # for each cell type
        resp[c] = np.zeros((ncells * len(cells), int(d['ntrial'])))

        keys = util.get_cell_data(d, c) 
        
        for t in range(d['ntrial']): # for each trial
            for i, r in enumerate(keys['tr'][t]['r']): # for each cell

                # handle case where TF is changing
                if params['analysis_type'] == 'tf':
                    _tf = int(tf[t])
                else:
                    _tf = int(tf)

                cell = d['tr'][t]['r'][r][resp_ind]

                if params['cell_type'] == 'rgc':
                    cell = compute_psth(cell, time.max(), delta_t=10)

                fft =  np.fft.fft(cell)
                                
                if params['analysis_type'] == 'cone_inputs':
                    amp  = np.real(fft[_tf]) * 2 / N
                    resp[c][i, t] = amp / params['cone_contrast'][t]
                else: 
                    amp  = np.abs(fft[_tf]) * 2 / N
                    resp[c][i, t] = amp

        if normalize:
            resp[c] = (resp[c].T / np.abs(resp[c]).sum(1)).T

    return resp


def svm_classify(data_matrix, categories, param_grid, target_names, cmdscaling,
                      dims=[0, 1, 2], display_verbose=False, rand_seed=23453, 
                      Nseeds=100, test_size=0.1, kernel='linear'):
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

    if cmdscaling:
        # compute distance matrix
        corrmat = compute_corr_matrix(data_matrix)
        # compute the classical multi-dimensional scaling
        config_mat, eigen = dat.cmdscale(corrmat)
    else:
        pca = PCA(n_components=len(dims)).fit(data_matrix)
        config_mat = pca.transform(data_matrix)

    # set up data containers for results
    total_y_true = np.array([])
    total_y_pred = np.array([])
    ncells = len(data_matrix[:, 0])
    for seed in rand_seeds:
        # Split into a training set and a test set using a stratified k fold
        X_train, X_test, y_train, y_test = train_test_split(
            np.arange(ncells), categories, test_size=test_size,
            random_state=int(seed[0]))

        X_train = config_mat[X_train, :][:, dims]
        X_test = config_mat[X_test, :][:, dims]

        # Classify with SVM
        if kernel == 'linear':
            clf = SVC(C=param_grid['C'][0], kernel='linear',
                      class_weight={0: 0.1, 1: 0.45, 2: 0.45})#,
            # change class_weight = balanced so less arbitrary? No
            #class_weight='balanced')
        else:
            clf = GridSearchCV(SVC(kernel=kernel, class_weight='balanced'),
                               param_grid)

        clf = clf.fit(X_train, y_train)

        # predict test data with fit model
        y_pred = clf.predict(X_test)

        if display_verbose and kernel != 'linear':
            print("Best estimator found by grid search:")
            print(clf.best_estimator_)    
            
        # Quantitative evaluation of the model quality on the test set
        total_y_true = np.append(total_y_true, y_test)
        total_y_pred = np.append(total_y_pred, y_pred)


    n_classes = len(target_names)
    report = classification_report(total_y_true, total_y_pred,
                                target_names=target_names)
    confusion_mat = confusion_matrix(total_y_true, total_y_pred, 
                                     labels=range(n_classes))

    # print the summary results
    print_output = 'Classification report\n======================\n'
    print_output += 'N simulations: ' + str(Nseeds) + '\n' 
    for key in param_grid.keys():
        print_output += key + ':\t'
        print_output += ''.join('%10.3f' % x for x in param_grid[key]) + '\n'
        #print_output += ''.join(map(str, param_grid[key])) + '\n'
    print_output += '\n' + report + '\n'
    print_output += np.array_str(confusion_mat)

    return clf, print_output


def associate_cone_color_resp(r, nn_dat, celllist, mod_name, bkgd='white',
                              randomized=False, cell_type='bp'):
    '''
    '''
    # first get data
    cnaming = np.genfromtxt('mosaics/' + mod_name + '_' + bkgd + '_bkgd.csv', 
                            delimiter=',', skip_header=1)
    # old_new refers to the coordinates of the classified cones in the old 
    # (AO defined)
    # coord space and those same cones in the WM defined space. These files are 
    # generated in mosaic/gen_mosaic.py and do not include LMS cone types
    newold = np.genfromtxt('mosaics/' + mod_name + '_old_new.csv')
    if randomized:
        mod_name += '_mosaic_randomized'
    else:
        mod_name += '_mosaic'
    mosaiclist = np.genfromtxt('mosaics/' + mod_name + '.txt')
    
    # get the nearest neighbors to the specified cone
    to_newold = spat.KDTree(newold[:, 2:])
    to_cnaming = spat.KDTree(cnaming[:, :2])
    to_simmos = spat.KDTree(mosaiclist[:, :2])

    count = 0
    c = cell_type
    output = np.zeros((len(r[c][:, 0]), 36))
    for cone in range(0, len(r[c][:, 0])):
        ind = np.where(nn_dat[:, 0] == float(celllist[cone]))[0]
        loc = nn_dat[ind, 2:4][0]

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
                    output[count, 2:5] = cone_weights
                    output[count, 34] = cone_type
                    output[count, 35] = nn_dat[ind, 0]
                    output[count, 5:10] = cnames[6:] # / total
                
                    # now need to associate mosaiclist w cone inputs
                    j = 10
                    for i in range(1, 9): # 10 nearest neighbors
                        #if randomized: # this randomized neighbors
                        #    ind1 = np.random.randint(0, 400, 1)
                        #else:
                        ind1 = np.where(nn_dat[:, 0] == moscoord[1][i])[0]
                            
                        neighbor = r[c][ind1]
                        output[count, j:j + 3] = neighbor
                        j += 3
                    count += 1

    # cleanup output and remove zeros
    output = output[~np.all(output == 0, axis=1)]

    return output


def get_rgby_from_naming(naming, purity_thresh=None):
    '''
    purity_thresh: find cones that have purities higher than this threshold.
    '''
    if purity_thresh is None:
        purity_thresh = 0

    high_purity = []
    rg = np.zeros((len(naming[:, 1]), 1))
    by = np.zeros((len(naming[:, 1]), 1))
    for i in range(len(naming[:, 1])):
        maxind = naming[i, :].argmax()

        # check if cone has a purity greater than purity_threshold
        if naming[i, maxind] / naming[i, :].sum() > purity_thresh:
            high_purity.append(i)
        
        # green - red / total
        rg[i] = (naming[i, 2] - naming[i, 1]) / naming[i, :].sum()

        # yellow - blue / total
        by[i] = (naming[i, 4] - naming[i, 3]) / naming[i, :].sum()

    return rg, by, high_purity


def compute_corr_matrix(data_mat):
    '''
    '''
    return 1 - np.corrcoef(data_mat)


def get_data_matrix(d, cell_type):
    # Get cell list from data keys
    celllist = util.get_cell_list(d)
    ncells = len(celllist)

    # Load params from meta data
    nsteps = util.num(d['const']['MOO_tn']['val']) # time steps
    ntrials = util.num(d['ntrial'])

    normalize = False    
    #cells = util.get_cell_type(cell_type)
    if cell_type == 'rgc':
        resp_ind = 'p'
    else:
        resp_ind = 'x'

    cellkey = util.get_cell_data(d, cell_type) 
        
    data_mat = np.zeros((ncells, nsteps * ntrials))
    for t in range(ntrials):
        for i, r in enumerate(cellkey['tr'][t]['r']):
            data_mat[i, t * nsteps:(t + 1) * nsteps] = d['tr'][t]['r'][r][resp_ind]

    return data_mat


def compute_s_dist_cone_weight(d, celldat, celllist, params):
    '''
    '''
    deg_per_pix, mm_per_deg = util.conversion_factors(params['species'])

    cellIDs = celldat[:, 0]

    # convert pixels into arcmin
    dist2S =  nn.find_nearest_S(celldat[:, 2:4], params['mosaic_file'])[0]
    dist2S *= deg_per_pix * 60

    N = util.num(d['const']['MOO_tn']['val']) # time steps
    tf = util.num(d['const']['tf']['val']) # temporal frequency (Hz)

    lm_midgets = np.zeros((len(celllist), 2))
    keys = util.get_cell_data(d['tr'][0], 'bp')
    for i, r in enumerate(keys):
        # find distance to S
        cellID = int(celllist[i])
        ind = np.where(cellIDs == cellID)[0]
        distance = dist2S[ind]

        # Compute SML cone weights
        # Trials: 1. S iso; 2. M iso; 3. L iso
        sml_weights = np.zeros((3, 1))
        for t in [0, 1, 2]:             
            # find amplitude of signal
            cell = d['tr'][t]['r'][r]['x']
            fft = np.fft.fft(cell)
            amp  = np.abs(fft[int(tf)]) * 2 / N
            sml_weights[t] = amp / params['cone_contrast'][t] 

        # skip S cones
        if celldat[ind, 1] != 0:
            lm_midgets[i, 0] = distance
            sml = sml_weights / sml_weights.sum()
            lm_midgets[i, 1] = sml[0] # s-cone weight

    # remove zero rows (where S cones were)
    lm_midgets = lm_midgets[~np.all(lm_midgets == 0, axis=1)]

    return lm_midgets


def compute_cone_weights(r, nn_dat, celllist):
    for c in r: # for each cell type in results
        output = np.zeros((len(r[c][:, 0]), 37))
        for cone in range(0, len(r[c][:, 0])):
            ind = np.where(nn_dat[:, 0] == float(celllist[cone]))[0]
            loc = nn_dat[ind, 2:4][0]
            
            # compute s weight for mosaic plot
            s_weight = r[c][cone, 0] #compute_s_weight(r, c, cone)
            
            # compute cone weights (re-order to L, M, S)
            cone_weights = [r[c][cone, 1], r[c][cone, 2], s_weight]


def get_cone_xy_lms(d, nn_dat, celllist):
    '''Find the xy position and cone type (lms) of a population of cones.
    '''    
    ncells = len(celllist)
    
    xylms = np.zeros((ncells, 3))
    t = 0 # only need to look at first trial
    for cone in range(ncells): # for each cell
        ind = np.where(nn_dat[:, 0] == float(celllist[cone]))[0]
        loc = nn_dat[ind, 2:4][0]
        lms = nn_dat[ind, 1]
        xylms[cone, :] = np.concatenate([loc, lms])
    return xylms


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
