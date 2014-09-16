#! /usr/bin/env python
import sys, os
import numpy as np

from plot_dist import plot_dist

def main():
	'''
	'''	
	if 'ret4' in sys.argv:
		SPECIES = 'human'
	elif 'ret3' in sys.argv:
		SPECIES = 'macaque'

	data = {}
	
	if 'h1' in sys.argv or 'verbose' in sys.argv:
		data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl', skip_header=2)

	if 'h2' in sys.argv or 'verbose' in sys.argv:
		data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', skip_header=2)

	plot_dist(data, SPECIES)


if __name__ == '__main__':

	main()