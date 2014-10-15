from __future__ import division
import os, sys
import numpy as np


def clean_data(d):
    '''
    '''
    data = {}
    for t in range(d['meta']['NTRIALS']):
        _d = d[t]

        data[t] = {}
        data[t]['cone'] = []
        data[t]['h1'] = []
        data[t]['h2'] = []
        data[t]['bp'] = []
        data[t]['rgc'] = []

        for key in _d.keys():
            if key[2:6] == 'cone':
                data[t]['cone'].append(_d[key]['vals'])
            elif key[:2] == 'h1':
                data[t]['h1'].append(_d[key]['vals'])
            elif key[:2] == 'h2':
                data[t]['h2'].append(_d[key]['vals'])
            elif key[:2] == 'bp':
                data[t]['bp'].append(_d[key]['vals'])
            elif key[:3] == 'rgc':
                data[t]['rgc'].append(_d[key]['vals'])

    data['time'] = np.linspace(0, float(d['meta']['stim_samp']),
                               float(d['meta']['MOO_tn']))

    return data


def parse_txt(fname='results/txt_files/zz.txt'):
    '''Not yet dealing with var link data.
    
    Need to keep track of trials. Not currently doing this.
    As a result var link data does not work.
    '''
    data = {'meta': {}, }
    i = 0 # index of file
    t = 0 # trial
    with open(fname) as f:
        d = f.read()
        data_list = d.split('\n')
        while i < len(data_list):
            line = data_list[i].split(' ')
                      
            if line[0] == 'RTYPE':
                rtype = float(line[1])
                name = line[4]
                data_line = True

                i += 1
                dat = data_list[i].split(' ') 
                try:
                    dat.remove('')
                except ValueError:
                    pass
                try:
                    dat = np.asarray(dat, dtype='|S8')
                    dat = dat.astype(np.float)
                except ValueError: # handle empty arrays
                    dat = np.array([])
  
                # increment trial if cell already exists
                if name in data[t].keys():
                    t += 1
                data[t][name] = {}
                data[t][name]['vals'] = dat
                data[t][name]['rtype'] = rtype
                if rtype == 0:
                    try:
                        while data_list[i + 1].split(' ')[0] != 'RTYPE':
                            i += 1
                            dat = data_list[i].split(' ')
                            if dat[0] != '':
                                try: # handle empty arrays
                                    dat = np.asarray(dat, dtype='|S8')
                                    dat = dat.astype(np.float)
                                    dat = np.concatenate(
                                        (data[t][name]['vals'], dat))
                                except ValueError:
                                    pass
                    except IndexError:
                        pass
            else:
                try:
                    line.remove('')
                except ValueError:
                    pass
                if line != []:
                    if line[0] == '':
                        j = 2
                    else:
                        j = 0  
                    try:
                        data['meta'][line[j]] = line[j+1]
                    except IndexError:
                        data['meta'][line[j]] = []
                # if RTYPE is ntrials use data to setup data dict
                if line[0] == 'NTRIALS':
                    data['meta']['NTRIALS'] = int(line[j+1])
                    for trial in range(0, int(line[1])):
                        data[trial] = {}

            i += 1
    return data


if __name__ == '__main__':
    data = parse_txt()   
    print 'This function parses nd files'
    try:
        print data['meta'].keys()
        print data.keys()
    except:
        print 'cannot locate zz.nd'
        pass


