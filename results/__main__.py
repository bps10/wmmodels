#! /usr/bin/env python
import sys, os
import numpy as np

from plot_dist import plot_dist
from plot_mosaic import plot_mosaic
from plot_cones import plot_cones
from parse_txt import parse_txt


def main():
    '''	
    '''	
    if 'human' in sys.argv:
        SPECIES = 'human'
    elif 'macaque' in sys.argv:
        SPECIES = 'macaque'

    if 'mosaic' in sys.argv:
        plot_mosaic()
	
    plots = []
    data = {}
    if 'h1' in sys.argv or 'verbose' in sys.argv:
        data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl', 
				       skip_header=2)
	plots.append('horiz')

    if 'h2' in sys.argv or 'verbose' in sys.argv:
        data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', 
				       skip_header=2)
	if 'horiz' not in plots:
            plots.append('horiz')
    
    if 'cone' in sys.argv:
        d = parse_txt()
        data['cone'] = []
	for key in d.keys():
            if key[2:6] == 'cone':
                data['cone'].append(d[key]['vals'])

        time = np.arange(len(d[key]['vals']))
        plot_cones(time, data['cone'])

    if data is not {}:
        if 'horiz' in plots:
            plot_dist(data, SPECIES)


if __name__ == '__main__':

    main()
