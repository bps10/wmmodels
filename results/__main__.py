#! /usr/bin/env python
import sys, os
import numpy as np

import plot as plot
from parse_txt import parse_txt


def main():
    '''	
    '''	
    if 'human' in sys.argv:
        SPECIES = 'human'
    elif 'macaque' in sys.argv:
        SPECIES = 'macaque'

    if 'mosaic' in sys.argv:
        plot.mosaic()
	
    plots = []
    data = {}
    h1 = ['h1', 'verbose']
    h2 = ['h2', 'verbose']
    h_time = ['h_time', 'verbose']
    stack = ['siso', 'cone', 'stack', 'coneiso']
    
    for arg in sys.argv:
        if arg in h1:
            data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl',             
				       skip_header=2)
            if 'horiz' not in plots:
                plots.append('horiz')
        if arg in h2:
            data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', 
				       skip_header=2)            
            if 'horiz' not in plots:
                plots.append('horiz')
    
        if arg in stack:
            if 'stack' not in plots:
                plots.append('stack')
        if arg in h_time:
            if 'h_time' not in plots:
                plots.append('h_time')

    if 'stack' in plots or 'h_time' in plots:
        d = parse_txt()

    if 'stack' in plots:
        plot.stack(d)

    if 'h_time' in plots:
        plot.horiz_time_const(d)

    if 'horiz' in plots:
        if data is not {}:
            plot.dist(data, SPECIES)


if __name__ == '__main__':

    main()
