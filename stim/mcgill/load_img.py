from __future__ import division

from PIL import Image
import numpy as np
import matplotlib.pylab as plt

img_name = 'merry_italy0125'
ending = '.tif'
filename = 'stim/mcgill/' + img_name

img = Image.open(filename + ending)
imarray = np.array(img, dtype='uint8')

print imarray.shape

plt.figure()
plt.imshow(imarray)

arr = np.zeros((imarray.shape[0] * imarray.shape[1], 1))
i = 0
for x in range(imarray.shape[0]):
    for y in range(imarray.shape[1]):
        byte = int(imarray[x, y, 0])
        byte = byte << 8
        byte = byte | int(imarray[x, y, 1])
        byte = byte << 8
        byte = byte | int(imarray[x, y, 2])

        b = byte >> 0
        g = byte >> 8
        r = byte >> 16
        print imarray[i, 0, :]
        print r, g, b

        arr[i] = byte
        i += 1
print arr[:100]
        
#imd = np.zeros((imarray.shape[0], imarray.shape[1]))
#for i in range(2):#len(arr)):


'''
flatarray = imarray.flatten()

f = open(filename + '.bin', 'wb')
f.write(flatarray)
f.close()

f = open(filename + '.bin', 'rb')
im = np.fromfile(f, dtype=np.uint8)
f.close()

im = im.reshape(768, 576, 3)

plt.figure()
plt.imshow(im)
plt.show()'''

