from __future__ import division
import os, sys
import numpy as np


def clean_data(d):
    data = {}
    data['cone'] = []
    data['h1'] = []
    data['h2'] = []
    data['bp'] = []
    data['rgc'] = []
    for key in d.keys():
        if key[2:6] == 'cone':
            data['cone'].append(d[key]['vals'])
        elif key[:2] == 'h1':
            data['h1'].append(d[key]['vals'])
        elif key[:2] == 'h2':
            data['h2'].append(d[key]['vals'])
        elif key[:2] == 'bp':
            data['bp'].append(d[key]['vals'])
        elif key[:3] == 'rgc':
            data['rgc'].append(d[key]['vals'])
    data['time'] = np.arange(len(d[key]['vals']))
    return data

def parse_txt(fname='results/txt_files/zz.txt'):

    data = {'meta': {}, }
    i = 0
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
                data[name] = {}
                data[name]['vals'] = dat
                data[name]['rtype'] = rtype
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
                                        (data[name]['vals'], dat))
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
            
                    data['meta'][line[j]] = line[j+1]
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


