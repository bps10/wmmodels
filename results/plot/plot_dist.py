from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf

from conversion import conversion_factors


def dist(data, species, invert=True, normalize=True):
	'''
	'''
	pix_per_deg, mm_per_deg = conversion_factors(species)

	fig = plt.figure()
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)

	pf.AxisFormat(markersize=8)
	pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

	for d in data:
		dat = data[d]
		x_val_h1 = dat[:, 0] * pix_per_deg * mm_per_deg * 1000
		if normalize:
			dat[:, 1] /= dat[:, 1].max()

		ax.plot(x_val_h1, dat[:, 1], 'o')

	ax.set_xlabel('distance ($\mu$m)')

	if invert:
		pf.invert(ax, fig, bk_color='k')

	fig.savefig('results/img/h_space_const.svg', 
		    facecolor=fig.get_facecolor(), edgecolor='none')

	plt.show()

if __name__ == '__main__':

	## LOAD DATA BASED ON INPUT ARG ALLOW FOR 2 PLOTS
	data = {}
	try:
		data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl', skip_header=2)
	except:
		pass
	try:
		data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', skip_header=2)
	except:
		pass

	dist(data)

