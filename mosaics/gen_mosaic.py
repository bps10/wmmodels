from __future__ import division
import matplotlib.pylab as plt
import numpy as np
from scipy.spatial import ConvexHull, KDTree


def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def gen_mosaic(mosaic_file='model.mosaic', subj_file='10001_WT.csv',
               scale_factor=4.6, offset_factor=40):
    model = np.genfromtxt(mosaic_file)
    
    subj = np.genfromtxt(subj_file, delimiter=',')
    tmp = np.zeros((len(subj[:, 2]), 4))
    tmp[:, :2] = subj[:, :2]
    subj[:, :2] = subj[:, :2] / scale_factor # scale it to be same size
    subj[:, :2] = subj[:, :2] + offset_factor # offset to be in center
    tmp[:, 2:] = subj[:, :2]
    np.savetxt('old_new.csv', tmp)
    del tmp

    hull = ConvexHull(subj[:, :2])
    outline = zip(subj[hull.vertices, 0], subj[hull.vertices, 1])

    inside = np.zeros((len(model[:, 2]), 1))
    for i in range(len(model[:, 2])):
        x = model[i, 2]
        y = model[i, 3]
        
        inside[i] = point_in_poly(x, y, outline)
        
    print 'added {0} nodes'.format(str(len(subj[:, 0])))
    print 'deleted {0} nodes'.format(str(sum(inside)))

    outside = np.array([not i for i in inside])

    # plot
    plt.figure()

    S = subj[:, 2] == 1
    M = subj[:, 2] == 2
    L = subj[:, 2] == 3
    plt.plot(subj[L, 0], subj[L, 1], 'ro')
    plt.plot(subj[M, 0], subj[M, 1], 'go')
    plt.plot(subj[S, 0], subj[S, 1], 'bo')

    S = model[outside, 1] == 0
    M = model[outside, 1] == 1
    L = model[outside, 1] == 2
    x = model[outside, 2]
    y = model[outside, 3]
    plt.plot(x[L], y[L], 'ro', alpha=0.4)
    plt.plot(x[M], y[M], 'go', alpha=0.4)
    plt.plot(x[S], y[S], 'bo', alpha=0.4)

    # kill nodes that are too close
    # ------------------------------
    d = np.vstack([subj[:, :2], model[outside, 2:]])
    data = np.zeros((d.shape[0], d.shape[1] + 2))

    # append cone type
    d_type = subj[:, 2] - 1
    m_type = model[outside, 1]
    types = np.concatenate([d_type, m_type])

    data[:, 0] = types

    # keep track of model vs data nodes
    d_nodes = np.zeros((len(subj[:, 2])))
    m_nodes = np.ones((len(model[outside, 2])))
    nodes = np.concatenate([d_nodes, m_nodes])
    data[:, 3] = nodes

    # construct kd tree
    tree = KDTree(d, 2)
    data[:, 1:3] = tree.data
    nn = tree.query(subj[:, :2], 2)

    too_close = nn[0][:, 1] < 0.8
    indexes = nn[1][too_close, 1]
    kill_ind = indexes[indexes > len(subj[:, 2])]

    keep = []
    for i in range(len(data[:, 3])):
        if i not in kill_ind:
            keep.append(i)
    data = data[keep, :]

    print 'deleted {0} additional nodes'.format(str(len(kill_ind)))

    # add new nodes in holes
    delta = 1.95
    nodes = tree.data
    windows = []
    for x in np.arange(30.5, 90, delta):
        for y in np.arange(30.4, 90, delta):
            go_on = True
            i = 0
            maxi = len(nodes) - 1
            while go_on:
                node = nodes[i]
                if (node[0] > x and node[0] < x + delta and
                    node[1] > y and node[1] < y + delta):

                    # remove node
                    nodes = np.delete(nodes, i, 0)
                    go_on = False
                
                # move onto next window
                elif i >= maxi:
                    windows.append((x, y))
                    go_on = False

                else: # keep going and increment counter
                    i += 1

    np.random.seed(2568) # make sure rand generator in known state
    for window in windows:
        newcone = np.zeros((4))
        newcone[0] = np.random.randint(1, 3, 1) # cone type (M or L)
        newcone[1] = window[0] + (delta / 2)
        newcone[2] = window[1] + (delta / 2)
        newcone[3] = 2 # is a new cone
        
        # add the new cone to data
        data = np.vstack([data, newcone])

    print 'added {0} additional nodes'.format(str(len(windows)))

    # plot final mosaic
    plt.figure()

    S = data[:, 0] == 0
    M = data[:, 0] == 1
    L = data[:, 0] == 2
    x = data[:, 1]
    y = data[:, 2]

    plt.plot(x[L], y[L], 'ro', alpha=0.4)
    plt.plot(x[M], y[M], 'go', alpha=0.4)
    plt.plot(x[S], y[S], 'bo', alpha=0.4)

    # find new nodes
    new = data[:, 3] == 2
    # index on new nodes
    Sn = data[new, 0] == 0
    Mn = data[new, 0] == 1
    Ln = data[new, 0] == 2
    xn = data[new, 1]
    yn = data[new, 2]

    plt.plot(xn[Ln], yn[Ln], 'ro')
    plt.plot(xn[Mn], yn[Mn], 'go')
    plt.plot(xn[Sn], yn[Sn], 'bo')

    plt.show()

    # rearrange data for saving in proper format
    d = np.zeros((len(data[:, 0]), 3))                                      
    d[:, 2] = data[:, 0]
    d[:, :2] = data[:, 1:3]
    #d = d[d[:, 1].argsort()]

    # now have to do a hacky thing to get this list sorted
    # there is an easier way to do this. Need to understand structured
    # arrays better.
    np.savetxt('subj_mosaic.txt', d, delimiter='  ', fmt="%f %f %d")
    d = np.genfromtxt('subj_mosaic.txt', names=['a', 'b', 'c'])

    # sort the structured array
    d = np.sort(d, order=['b', 'a'])

    # save the file in an ordered manner.
    np.savetxt('subj_mosaic.txt', d, delimiter='  ', fmt="%f %f %d")

def find_hc():
    '''
    '''
    # get the data from the stitched together mosaic
    data = np.genfromtxt('subj_mosaic.txt', delimiter=' ')

    # create a KD tree structure
    tree = KDTree(data[:, :2], 7)
    
    # get the nearest neighbors (0 = cone itself)
    nn = tree.query(data[:, :2], 7)
    
    # paste together distances (n[0]) and ids (n[1])
    out = np.hstack([nn[0][:, 1:], nn[1][:, 1:]])

    # save nearest neighbor data
    np.savetxt('neighbors.txt', out, delimiter=' ',
               fmt="%f %f %f %f %f %f %d %d %d %d %d %d")


def gen_randomized_mosaic(mosaic_file):
    '''Take a mosaic and shuffle the cone identities, but keep the 
    x,y locations the same
    '''
    data = np.genfromtxt(mosaic_file, delimiter=' ')

    cone_types = data[:, 2].astype('int')
    np.random.shuffle(cone_types)
    data[:, 2] = cone_types

    # save the file in an ordered manner.
    savename = mosaic_file[:-4] + '_randomized.txt'
    np.savetxt(savename, data, delimiter='  ', fmt="%f %f %d")


if __name__ == '__main__':

    gen_mosaic(mosaic_file='model.mosaic', # model mosaic file
               subj_file='20076_BPS.csv', # subj mosaic file
               scale_factor=4.6, # scale subj mosaic to fit density WT=4.6
               offset_factor=40 # offset subj mosaic to be centered WT=40
               )
    find_hc()

    gen_randomized_mosaic('mosaics/BPS_mosaic.txt')
