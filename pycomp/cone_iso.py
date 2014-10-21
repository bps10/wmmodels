from __future__ import division
import numpy as np
import sys

from base import spectsens as ss


def cone_iso(spect='stockman', print_conv_M=False, 
	     print_S=False, print_M=False, print_L=False,
	     print_bkgd=False, print_var_link=False, 
	     max_contrast=True):
	'''Implement a % cone contrast specification.
	'''
	if spect == 'stockman':
		tmp = ss.stockmanfund(minLambda=390, maxLambda=750)
		sens = {}
		sens['l'] = tmp[:, 0]
		sens['m'] = tmp[:, 1]
		sens['s'] = tmp[:, 2]
		
	elif spect == 'neitz':
		sens = ss.load_spect(speak=420, mpeak=530, lpeak=559,
				     lambdamin=390, lambdamax=750, 
				     OD=[0.3, 0.4, 0.4],
				     add_filters=True, LOG=False)

	spectrum = np.arange(390, 751, 1)

	lights = {
		0: {'l': 650, 'ind': 0, 'spec': np.zeros(len(spectrum)), },
		1: {'l': 530, 'ind': 0, 'spec': np.zeros(len(spectrum)), },
		2: {'l': 420, 'ind': 0, 'spec': np.zeros(len(spectrum)), },
		}
	for light in lights:
		
		lights[light]['ind'] = np.where(
			spectrum == lights[light]['l'])[0]
		# should make this a gaussian for better accuracy
		lights[light]['spec'][lights[light]['ind']] = 1

	# generate system matrix: [LMS].T = [M][RGB].T
	M = np.array([
			[np.sum(sens['l'] * lights[0]['spec']),
			 np.sum(sens['l'] * lights[1]['spec']),
			 np.sum(sens['l'] * lights[2]['spec'])],
			
			[np.sum(sens['m'] * lights[0]['spec']),
			 np.sum(sens['m'] * lights[1]['spec']),
			 np.sum(sens['m'] * lights[2]['spec'])],

			[np.sum(sens['s'] * lights[0]['spec']),
			 np.sum(sens['s'] * lights[1]['spec']),
			 np.sum(sens['s'] * lights[2]['spec'])],
			])

	if print_conv_M:
		print M
	
	# generate inversion matrix for later
	inv_M = np.linalg.inv(M)
	
	# set background - assume 1/2 max light val for now
	bkgd = np.array([[0.5], [0.5], [0.5]])

	# compute relative photo isomerizations for background
	bkgd_photo = np.dot(M, bkgd)

	if print_bkgd:
		for i in range(len(bkgd_photo)):
			print bkgd_photo[i][0]

	# Find maximum we can move from background
	if max_contrast:
		if print_L is True: 
			i = 0
		if print_M is True: 
			i = 1
		if print_S is True: 
			i = 2
		scale = bkgd_photo[np.abs(bkgd - bkgd_photo[i]).argmax()]
	else:
		scale = bkgd_photo[np.abs(bkgd - bkgd_photo).argmax()]
	
	# LMS cone iso vectors
	s_iso = np.array([[0], [0], [1]])
	m_iso = np.array([[0], [1], [0]])
	l_iso = np.array([[1], [0], [0]])

	# S cone computation
	s_iso_rgb = np.dot(inv_M, s_iso)
	
	s_delta = s_iso_rgb / np.abs(s_iso_rgb).max() * scale
	s_plus = bkgd + s_delta
	s_minus = bkgd - s_delta
	
	# M cone computation
	m_iso_rgb = np.dot(inv_M, m_iso)

	m_delta = m_iso_rgb / np.abs(m_iso_rgb).max() * scale
	m_plus = bkgd + m_delta
	m_minus = bkgd - m_delta

	# L cone computation
	l_iso_rgb = np.dot(inv_M, l_iso)

	l_delta = l_iso_rgb / np.abs(l_iso_rgb).max() * scale
	l_plus = bkgd + l_delta
	l_minus = bkgd - l_delta

	# print outputs
	c = ['r', 'g', 'b']

	if print_S:
		for i in range(len(s_plus)):
			print 'color0_' + c[i] + ' ' + str(s_plus[i][0])
		for i in range(len(s_minus)):
			print 'color1_' + c[i] + ' ' + str(s_minus[i][0])
		cc = cone_contrast(M, bkgd_photo, s_plus)
		print '# cone contrast:'
		for i in range(len(s_minus)):
			print '# ' + str(cc[i][0])

	if print_M:
		for i in range(len(m_plus)):
			print 'color0_' + c[i] + ' ' + str(m_plus[i][0])
		for i in range(len(m_minus)):
			print 'color1_' + c[i] + ' ' + str(m_minus[i][0])
		cc = cone_contrast(M, bkgd_photo, m_plus)
		print '# cone contrast:'
		for i in range(len(s_minus)):
			print '# ' + str(cc[i][0])

	if print_L:
		for i in range(len(l_plus)):
			print 'color0_' + c[i] + ' ' + str(l_plus[i][0])
		for i in range(len(l_minus)):
			print 'color1_' + c[i] + ' ' + str(l_minus[i][0])
		cc = cone_contrast(M, bkgd_photo, l_plus)
		print '# cone contrast:'
		for i in range(len(s_minus)):
			print '# ' + str(cc[i][0])

	if print_var_link:
		print ' '
		print 'cone 0'
		print ' ' 
		print 'VARLINK_cone 1 2 3'
		for i in range(len(l_plus)):
			print ('VARLINK_color0_' + c[i] + ' ' + 
			       str(s_plus[i][0]) + ' ' + 
			       str(m_plus[i][0]) + ' ' + 
			       str(l_plus[i][0]))
		for i in range(len(l_minus)):
			print ('VARLINK_color1_' + c[i] + ' ' + 
			       str(s_minus[i][0]) + ' ' + 
			       str(m_minus[i][0]) + ' ' + 
			       str(l_minus[i][0]))


def cone_contrast(M, bkgd, rgb1):
	a = bkgd
	b = np.dot(M, rgb1)
	diff = (np.abs(b - a) / a)
	return  diff

if __name__ == '__main__':

	if sys.argv[1] == 'siso':
		cone_iso('stockman', print_S=True)

	if sys.argv[1] == 'miso':
		cone_iso('stockman', print_M=True)

	if sys.argv[1] == 'liso':
		cone_iso('stockman', print_L=True)

	if sys.argv[1] == 'coneiso':
		cone_iso('stockman', print_var_link=True)

	if sys.argv[1] == 'bkgd':
		cone_iso('stockman', print_bkdg=True)
