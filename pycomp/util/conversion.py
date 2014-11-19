

def conversion_factors(species):
	if species == 'human':
		# 0. Conversion factors
		deg_per_pix = 0.015
		mm_per_deg = 0.3

	elif species == 'macaque':
		# 0. Conversion factors
		deg_per_pix = 0.02
		mm_per_deg = 0.19

	else:
		raise('ERROR: species must be human or macaque.')

	return deg_per_pix, mm_per_deg
