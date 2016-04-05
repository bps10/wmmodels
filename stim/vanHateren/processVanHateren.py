from __future__ import division
import array
import numpy as np
import scipy.misc as m
import matplotlib.pylab as plt

img_name = 'imk00001'
ending = '.iml'
filename = 'stim/vanHateren/' + img_name + ending
with open(filename, 'rb') as handle:
   s = handle.read()
arr = array.array('H', s)
arr.byteswap()
img = np.array(arr, dtype='uint16').reshape(1024, 1536)

plt.figure()
plt.imshow(img, cmap='gray')

plt.show()

m.imsave(img_name + '.jpg', img)
