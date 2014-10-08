from __future__ import division
import os, sys
import numpy as np


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
                dat = np.asarray(dat, dtype='|S8')
                dat = dat.astype(np.float)
                data[name] = {}
                data[name]['vals'] = dat
                data[name]['rtype'] = rtype
                if rtype == 0:
                    try:
                        while data_list[i + 1].split(' ')[0] != 'RTYPE':
                            i += 1
                            dat = data_list[i].split(' ')
                            if dat[0] != '':
                                dat = np.asarray(dat, dtype='|S8')
                                dat = dat.astype(np.float)
                                dat = np.concatenate((data[name]['vals'], dat))
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
    data = parse()   
    print 'This function parses nd files'
    try:
        print data['meta'].keys()
        print data.keys()
    except:
        print 'cannot locate zz.nd'
        pass


