from __future__ import division
import numpy as np
import sys

from base import spectsens as ss


def cone_iso(spect='stockman', print_sys_M=False, print_cone=[],
             print_bkgd=False, print_var_link=False, filters=True):
    '''Outputs cone iso stimuli.
    TO DO
    =====
    * Cone contrast. Background white vs equal cones.
    '''

    if spect == 'stockman':
        if filters:
            tmp = ss.stockmanfund(minLambda=390, maxLambda=750)
        else:
            tmp = ss.stockman(minLambda=390, maxLambda=750)
        sens = {}
        sens['l'] = tmp[:, 0]
        sens['m'] = tmp[:, 1]
        sens['s'] = tmp[:, 2]

    elif spect == 'neitz':

        sens = ss.load_spect(speak=420, mpeak=530, lpeak=559,
                             lambdamin=390, lambdamax=750,
                             OD=[0.3, 0.35, 0.35],
                             add_filters=filters, LOG=False)
        for cone in sens:
            sens[cone] /= sens[cone].max()
    else:
        raise ValueError('Error: spec must be stockman or neitz')

    spectrum = np.arange(390, 751, 1)

    lights = {
            0: {'l': 625, 'spec': np.zeros(len(spectrum)), },
            1: {'l': 525, 'spec': np.zeros(len(spectrum)), },
            2: {'l': 445, 'spec': np.zeros(len(spectrum)), },
            }
    for light in lights:
        lights[light]['ind'] = np.where(
                spectrum == lights[light]['l'])[0]
        # should make this a gaussian for better accuracy
        lights[light]['spec'][lights[light]['ind']] = 1

    # generate system matrix: [LMS].T = [M][RGB].T
    M = np.zeros((3, 3))
    for i, cone in enumerate(['l', 'm', 's']):
        for l in [0, 1, 2]:
            M[i, l] = np.sum(sens[cone] * lights[l]['spec'])

    # generate inversion matrix for later
    inv_M = np.linalg.inv(M)

    # set background - assume 1/2 for each cone
    bkgd_photo = np.array([[0.5], [0.5], [0.5]])

    # compute relative intensities to create equal adaptation
    bkgd = np.dot(inv_M, bkgd_photo)

    # Find maximum we can move from background
    scale = {'l': 0, 'm': 0, 's': 0}
    for k in scale:
        scale[k] = bkgd[np.abs(bkgd - bkgd_photo).argmax()]
        if scale[k] > 0.5:
            scale[k] = 1 - scale[k]

    # Create data structure
    d = {'scale': scale, }

    # LMS cone iso vectors
    d['iso'] = {}
    d['iso']['s'] = np.array([[0], [0], [1]])
    d['iso']['m'] = np.array([[0], [1], [0]])
    d['iso']['l'] = np.array([[1], [0], [0]])

    # Cone computation
    d['rgb'] = {}
    d['delta'] = {}
    d['plus'] = {}
    d['minus'] = {}
    for c in ['s', 'm', 'l']:
        d['rgb'][c] = np.dot(inv_M, d['iso'][c])
        d['delta'][c] = (d['rgb'][c] / np.abs(d['rgb'][c]).max() *
                                              d['scale'][c])
        d['plus'][c] = bkgd + d['delta'][c]
        d['minus'][c] = bkgd - d['delta'][c]

    # print outputs
    if print_bkgd:

        # set background - assume 1/2 for each cone
        _bkgd_photo = np.array([[0.2], [0.2], [0.2]])

        # compute relative intensities to create equal adaptation
        _bkgd = np.dot(inv_M, _bkgd_photo)
        for i in range(len(_bkgd)):
            print _bkgd[i][0], _bkgd[i][0] * 4.9

    if print_sys_M:
        m = ['L', 'M', 'S']
        line = ''
        for i in range(3):
            line  += m[i] + '_rgb '
            for j in range(3):
                line += str(round(M[i, j], 6)) + ' '
            line += '\n'
        print line

    c = ['r', 'g', 'b']
    for key in  print_cone:
        if len(print_cone) == 1:
            for i in range(3):
                print 'color0_' + c[i] + ' ' + str(d['plus'][key][i][0])
            for i in range(3):
                print 'color1_' + c[i] + ' ' + str(d['minus'][key][i][0])
        cc = cone_contrast(M, bkgd_photo, d['plus'][key])

        print '# ' + key.upper() + ' cone contrast:'
        for i in range(3):
            print '# ' + str(cc[i][0])

    if print_var_link:
        print ' '
        print 'cone 0'
        print ' '
        print 'VARLINK_cone 1 2 3'
        for i in range(3):
            print ('VARLINK_color0_' + c[i] + ' ' +
                   str(d['plus']['s'][i][0]) + ' ' +
                   str(d['plus']['m'][i][0]) + ' ' +
                   str(d['plus']['l'][i][0]))
        for i in range(3):
            print ('VARLINK_color1_' + c[i] + ' ' +
                   str(d['minus']['s'][i][0]) + ' ' +
                   str(d['minus']['m'][i][0]) + ' ' +
                   str(d['minus']['l'][i][0]))


def cone_contrast(M, bkgd, rgb1):
    lms = np.dot(M, rgb1)
    return  (lms - bkgd) / bkgd


def michelson_contrast(M, rgb1, rgb2):
    lms1 = np.dot(M, rgb1)
    lms2 = np.dot(M, rgb2)
    return (lms2 - lms1) / (lms2 + lms1)



if __name__ == '__main__':

    fund = 'stockman'
    f = True

    if len(sys.argv)  > 2:
        fund = sys.argv[2]

    if len(sys.argv) > 3:
        f = [False, True][sys.argv[3].lower()[0] == 't']

    if sys.argv[1] == 'sys':
        cone_iso(fund, print_sys_M=True, filters=f)

    if sys.argv[1] == 'siso':
        cone_iso(fund, print_cone=['s'], filters=f)

    if sys.argv[1] == 'miso':
        cone_iso(fund, print_cone['m'], filters=f)

    if sys.argv[1] == 'liso':
        cone_iso(fund, print_cone['l'], filters=f)

    if sys.argv[1] == 'coneiso':
        cone_iso(fund, print_var_link=True, filters=f,
                 print_cone=['s', 'm', 'l'])

    if sys.argv[1] == 'bkgd':
        cone_iso(fund, print_bkgd=True, filters=f)
