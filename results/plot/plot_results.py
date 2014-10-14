from __future__ import division
import numpy as np
import matplotlib.pylab as plt

from base import plot as pf


# 0. Conversion factors
pix_per_deg = 0.02
mm_per_deg = 0.19

plot_mosaic = False

# 1. load data files
s_iso_curr = np.genfromtxt('s_cone_3690_siso.txt', skip_header=1)
m_iso_curr = np.genfromtxt('m_cone_3689_siso.txt', skip_header=1)
l_iso_curr = np.genfromtxt('l_cone_3691_siso.txt', skip_header=1)
mosaic = np.genfromtxt('zz.mosaic')
space_const_h1 = np.genfromtxt('h1.dist.pl', skip_header=2)
space_const_h2 = np.genfromtxt('h2_0.6.dist.pl', skip_header=2)
time_const_h1 = np.genfromtxt('h1_time_const.txt', skip_header=2)
time_const_h2 = np.genfromtxt('h2_time_const.txt', skip_header=2)
h1_s_iso = np.genfromtxt('h1_3690_siso.txt', skip_header=2)
h1_m_iso = np.genfromtxt('h1_3690_miso.txt', skip_header=2)
h1_l_iso = np.genfromtxt('h1_3690_liso.txt', skip_header=2)
h2_s_iso = np.genfromtxt('h2_3690_siso.txt', skip_header=2)
h2_m_iso = np.genfromtxt('h2_3690_miso.txt', skip_header=2)
h2_l_iso = np.genfromtxt('h2_3690_liso.txt', skip_header=2)

m_cone_flash = np.genfromtxt('m_cone_flash.txt', skip_header=2)
h1_flash = np.genfromtxt('h1_flash.txt', skip_header=2)
h2_flash = np.genfromtxt('h2_flash.txt', skip_header=2)
bp_flash = np.genfromtxt('bp_flash.txt', skip_header=2)
on_gang_flash = np.genfromtxt('on_gang_flash.txt', skip_header=2)
off_gang_flash = np.genfromtxt('off_gang_flash.txt', skip_header=2)

m_cone_s_input = np.genfromtxt('m_cone_s_input.txt', skip_header=2)
h1_s_input_2 = np.genfromtxt('h1_s_input_0.2.txt', skip_header=2)
h2_s_input_2 = np.genfromtxt('h2_s_input_0.2.txt', skip_header=2)
bp_s_input_2 = np.genfromtxt('bp_s_input_0.2.txt', skip_header=2)
onG_s_input_2 = np.genfromtxt('onG_s_input_0.2.txt', skip_header=2)
offG_s_input_2 = np.genfromtxt('offG_s_input_0.2.txt', skip_header=2)

h1_s_input_4 = np.genfromtxt('h1_s_input_0.4.txt', skip_header=2)
h2_s_input_4 = np.genfromtxt('h2_s_input_0.4.txt', skip_header=2)
bp_s_input_4 = np.genfromtxt('bp_s_input_0.4.txt', skip_header=2)
onG_s_input_4 = np.genfromtxt('onG_s_input_0.4.txt', skip_header=2)
offG_s_input_4 = np.genfromtxt('offG_s_input_0.4.txt', skip_header=2)

h1_s_input_6 = np.genfromtxt('h1_s_input_0.6.txt', skip_header=2)
h2_s_input_6 = np.genfromtxt('h2_s_input_0.6.txt', skip_header=2)
bp_s_input_6 = np.genfromtxt('bp_s_input_0.6.txt', skip_header=2)
onG_s_input_6 = np.genfromtxt('onG_s_input_0.6.txt', skip_header=2)
offG_s_input_6 = np.genfromtxt('offG_s_input_0.6.txt', skip_header=2)

bp_s_input_8 = np.genfromtxt('bp_s_input_0.8.txt', skip_header=2)

# 2. Plot cone iso stimuli
fig = plt.figure()
fig.set_tight_layout(True)
ax = fig.add_subplot(111)

pf.AxisFormat()
pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

time = s_iso_curr[:, 0]
ax.plot(time, s_iso_curr[:, 1] - s_iso_curr[10, 1], 'b')
ax.plot(time, m_iso_curr[:, 1] - m_iso_curr[10, 1], 'g')
ax.plot(time, l_iso_curr[:, 1] - l_iso_curr[10, 1], 'r')

ax.set_ylabel('response')
ax.set_xlabel('time (ms)')

pf.invert(ax, fig, bk_color='k')

plt.show()

# 3. Plot cone mosaic
if plot_mosaic:
	fig = plt.figure(figsize=(9, 9))
	fig.set_tight_layout(True)
	ax = fig.add_subplot(111)

	pf.AxisFormat()
	pf.TufteAxis(ax, [''], [5, 5])

	s_cones = mosaic[np.where(mosaic[:, 1] == 0)[0]]
	m_cones = mosaic[np.where(mosaic[:, 1] == 1)[0]]
	l_cones = mosaic[np.where(mosaic[:, 1] == 2)[0]]

	ax.plot(s_cones[:, 2], s_cones[:, 3], 'bo', markersize=6)
	ax.plot(m_cones[:, 2], m_cones[:, 3], 'go', markersize=6)
	ax.plot(l_cones[:, 2], l_cones[:, 3], 'ro', markersize=6)

	ax.set_xlim([-1, 128])
	ax.set_ylim([-1, 128])

	pf.invert(ax, fig, bk_color='k')

	plt.show()

# 4. Plot spatial receptive fields of horizontal cells
fig = plt.figure(figsize=(5, 6))
fig.set_tight_layout(True)
ax = fig.add_subplot(111)

pf.AxisFormat()
pf.TufteAxis(ax, ['bottom', ], [5, 5])

x_val_h1 = space_const_h1[:, 0] * pix_per_deg * mm_per_deg * 1000
x_val_h2 = space_const_h2[:, 0] * pix_per_deg * mm_per_deg * 1000

x_val_h1 = np.concatenate((-1 * x_val_h1[::-1], x_val_h1))
h1_space = np.concatenate((space_const_h1[::-1, 1], space_const_h1[:, 1]))

x_val_h2 = np.concatenate((-1 * x_val_h2[::-1], x_val_h2))
h2_space = np.concatenate((space_const_h2[::-1, 1], space_const_h2[:, 1]))

#norm = np.max([h1_space, h2_space])
ax.plot(x_val_h1, h1_space / h1_space.max(), 'y')
ax.plot(x_val_h2, h2_space / h2_space.max(), 'b')

ax.set_xlabel('distance ($\mu$m)')
ax.set_xlim([-200, 200])
ax.set_xticks([-200, -100, 0, 100, 200])

pf.invert(ax, fig, bk_color='k')

plt.show()

# 5. Plot time constant of horizontal cells
fig = plt.figure()
fig.set_tight_layout(True)
ax = fig.add_subplot(111)

pf.AxisFormat()
pf.TufteAxis(ax, ['bottom', 'left'], [5, 5])

# convert x axis into um
x_val_h1 = time_const_h1[:, 0] #* pix_per_deg * mm_per_deg * 1000
h1_time = time_const_h1[:, 1]
x_val_h2 = time_const_h1[:, 0] #* pix_per_deg * mm_per_deg * 1000
h2_time = time_const_h2[:, 1]

#norm = np.max([h1_space, h2_space])
ax.plot(x_val_h1, h1_time, 'y')# / h1_space.max(), 'y')
ax.plot(x_val_h2, h2_time, 'b')# / h2_space.max(), 'b')

ax.set_ylabel('response')
ax.set_xlabel('time (ms)')

pf.invert(ax, fig, bk_color='k')

plt.show()

# 6. Plot cone isolating stimuli

## H1's
fig = plt.figure(figsize=(6, 8))
fig.set_tight_layout(True)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

pf.AxisFormat()
pf.TufteAxis(ax1, ['', ], [5, 5])
pf.TufteAxis(ax2, ['', ], [5, 5])
pf.TufteAxis(ax3, ['', ], [5, 5])


ax1.plot(h1_l_iso[:, 0], h1_l_iso[:, 1], 'r')
ax2.plot(h1_m_iso[:, 0], h1_m_iso[:, 1], 'g')
ax3.plot(h1_s_iso[:, 0], h1_s_iso[:, 1], 'b')
ax3.plot(np.arange(100, 350), np.ones(250) * 0.23, 'w')


ax1.set_ylim([0.22, 0.47])
ax2.set_ylim([0.22, 0.47])
ax3.set_ylim([0.22, 0.47])
ax1.set_xlim([0, 1000])
ax2.set_xlim([0, 1000])
ax3.set_xlim([0, 1000])

pf.invert(ax1, fig, bk_color='k')
pf.invert(ax2, fig, bk_color='k')
pf.invert(ax3, fig, bk_color='k')

plt.show()

## H2's
fig = plt.figure(figsize=(6, 8))
fig.set_tight_layout(True)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

pf.AxisFormat()
pf.TufteAxis(ax1, ['', ], [5, 5])
pf.TufteAxis(ax2, ['', ], [5, 5])
pf.TufteAxis(ax3, ['', ], [5, 5])


ax1.plot(h2_l_iso[:, 0], h2_l_iso[:, 1], 'r')
ax2.plot(h2_m_iso[:, 0], h2_m_iso[:, 1], 'g')
ax3.plot(h2_s_iso[:, 0], h2_s_iso[:, 1], 'b')
ax3.plot(np.arange(100, 350), np.ones(250) * 0.23, 'w')


ax1.set_ylim([0.22, 0.47])
ax2.set_ylim([0.22, 0.47])
ax3.set_ylim([0.22, 0.47])
ax1.set_xlim([0, 1000])
ax2.set_xlim([0, 1000])
ax3.set_xlim([0, 1000])

pf.invert(ax1, fig, bk_color='k')
pf.invert(ax2, fig, bk_color='k')
pf.invert(ax3, fig, bk_color='k')

plt.show()

# 7. Plot response to pulse of light

fig = plt.figure(figsize=(5.5, 9))
fig.set_tight_layout(True)
ax1 = fig.add_subplot(411)
ax2 = fig.add_subplot(412)
ax3 = fig.add_subplot(413)
ax4 = fig.add_subplot(414)

pf.AxisFormat()
pf.TufteAxis(ax1, ['', ], [5, 5])
pf.TufteAxis(ax2, ['', ], [5, 5])
pf.TufteAxis(ax3, ['', ], [5, 5])
pf.TufteAxis(ax4, ['', ], [5, 5])

ax1.plot(m_cone_flash[:, 0], m_cone_flash[:, 1] - m_cone_flash[10, 1], 'w')
ax2.plot(h1_flash[:, 0], h1_flash[:, 1] - h1_flash[10, 1], 'w-')
ax2.plot(h2_flash[:, 0], h2_flash[:, 1] - h2_flash[10, 1] - 0.1, 'w--')
ax3.plot(bp_flash[:, 0], bp_flash[:, 1] - bp_flash[10, 1], 'w')
ax4.plot(on_gang_flash[:, 0], on_gang_flash[:, 1], 'w-')
ax4.plot(off_gang_flash[:, 0], off_gang_flash[:, 1], 'w--')
ax4.plot(np.arange(700, 950), np.ones(250) * 10, 'w')
ax4.plot(np.ones(2) * 20, np.array([0, 50]), 'w')

ax1.set_ylim([-0.26, 0.35])
ax2.set_ylim([-0.26, 0.35])
ax3.set_ylim([-0.26, 0.35])

ax1.set_xlim([0, 1000])
ax2.set_xlim([0, 1000])
ax3.set_xlim([0, 1000])
ax4.set_xlim([0, 1000])

pf.invert(ax1, fig, bk_color='k')
pf.invert(ax2, fig, bk_color='k')
pf.invert(ax3, fig, bk_color='k')
pf.invert(ax4, fig, bk_color='k')

plt.show()

# 8. Plot response as a func of H2 feedback to LM cones

fig = plt.figure(figsize=(5.5, 9))
fig.set_tight_layout(True)
ax1 = fig.add_subplot(411)
ax2 = fig.add_subplot(412)
ax3 = fig.add_subplot(413)
ax4 = fig.add_subplot(414)

pf.AxisFormat()
pf.TufteAxis(ax1, ['', ], [5, 5])
pf.TufteAxis(ax2, ['', ], [5, 5])
pf.TufteAxis(ax3, ['', ], [5, 5])
pf.TufteAxis(ax4, ['bottom', 'left'], [5, 2])

ax1.plot(m_cone_s_input[:, 0], m_cone_s_input[:, 1] - m_cone_s_input[10, 1], 'w')

ax2.plot(h1_s_input_2[:, 0], h1_s_input_2[:, 1] - h1_s_input_2[10, 1], 'w-')
ax2.plot(h1_s_input_4[:, 0], h1_s_input_4[:, 1] - h1_s_input_4[10, 1], 'w-')
ax2.plot(h1_s_input_6[:, 0], h1_s_input_6[:, 1] - h1_s_input_6[10, 1], 'w-')

ax2.plot(h2_s_input_2[:, 0], h2_s_input_2[:, 1] - h2_s_input_2[10, 1], 'w--')
ax2.plot(h2_s_input_4[:, 0], h2_s_input_4[:, 1] - h2_s_input_4[10, 1], 'w--')
ax2.plot(h2_s_input_6[:, 0], h2_s_input_6[:, 1] - h2_s_input_6[10, 1], 'w--')

ax3.plot(bp_s_input_2[:, 0], bp_s_input_2[:, 1] - bp_s_input_2[10, 1], 'w-')
ax3.plot(bp_s_input_4[:, 0], bp_s_input_4[:, 1] - bp_s_input_4[10, 1], 'w-')
ax3.plot(bp_s_input_6[:, 0], bp_s_input_6[:, 1] - bp_s_input_6[10, 1], 'w-')
ax3.plot(bp_s_input_8[:, 0], bp_s_input_8[:, 1] - bp_s_input_8[10, 1], 'w-')
ax3.plot(np.arange(50, 300), np.ones(250) * 0.1, 'w')

x_val = np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
y_val = np.array([0., 1., 8., 11., 15., 21.])
ax4.plot(x_val, y_val / y_val.max(), 'w-o')

#ax4.plot(offG_s_input_2[:, 0], offG_s_input_2[:, 1], 'w-')
#ax4.plot(offG_s_input_4[:, 0], offG_s_input_4[:, 1], 'w-')
#ax4.plot(offG_s_input_6[:, 0], offG_s_input_6[:, 1], 'w-')



ax1.set_ylim([-0.1, 0.2])
ax2.set_ylim([-0.1, 0.2])
ax3.set_ylim([-0.1, 0.2])
ax4.set_ylim([-0.5, 1.5])

ax1.set_xlim([0, 1000])
ax2.set_xlim([0, 1000])
ax3.set_xlim([0, 1000])
ax4.set_xlim([-0.1, 1.1])
ax4.set_yticks([0, 1])

ax4.set_xlabel('H2 feedback')
ax4.set_ylabel('response')

pf.invert(ax1, fig, bk_color='k')
pf.invert(ax2, fig, bk_color='k')
pf.invert(ax3, fig, bk_color='k')
pf.invert(ax4, fig, bk_color='k')

plt.show()
