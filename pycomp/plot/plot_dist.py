from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf

from util.conversion import conversion_factors


def dist(data, species, invert=False, normalize=True):
	'''
	'''
	deg_per_pix, mm_per_deg = conversion_factors(species)

	fig = plt.figure()
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)

	pf.AxisFormat(markersize=8, linewidth=3)
	pf.TufteAxis(ax, ['bottom', 'left'], [4, 5])

	for d in data:
		dat = data[d]
		dat = dat[dat[:, 0].argsort()]

		x_val_h = dat[:, 0] * deg_per_pix * mm_per_deg * 1000
		yval = dat[:, 1]

		xval = np.hstack([x_val_h[::-1][:-1] * -1, x_val_h])
		yval = np.hstack([yval[::-1][:-1], yval])
		if normalize:
			yval /= yval.max()

		ax.plot(xval, yval, '-', label=d.upper())

	ax.set_xlabel('distance ($\mu$m)')
	ax.set_xlim([-200, 200])
	ax.legend(fontsize=22)

	if invert:
		pf.invert(ax, fig, bk_color='k')

	fig.savefig('results/img/h_space_const.svg', 
		    #facecolor=fig.get_facecolor(), 
		    edgecolor='none')

	plt.show()

if __name__ == '__main__':

	## LOAD DATA BASED ON INPUT ARG ALLOW FOR 2 PLOTS
	data = {}
	try:
		data['h1'] = np.genfromtxt('results/pl_files/h1.dist.pl', 
					   skip_header=2)
	except:
		pass
	try:
		data['h2'] = np.genfromtxt('results/pl_files/h2.dist.pl', 
					   skip_header=2)
	except:
		pass

	dist(data)

