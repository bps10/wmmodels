#
#  Ret_Mesh_H2.moo
#

mod_type pop

sscale        0.015   # degr/pix (this is different from stim)
tscale        0.002  # sec/frame
xn          64      # x size
yn          64      # y size
tn         1024      # t size

<area>
  name   v1          # Area name
  x0    58.0         # Origin wrt stim grid
  y0    58.0         #
  xn    12           # width
  yn    12           # height
  umx   64.0 (um)    # microns per Area grid unit (for now, Area = Stim grid)
</area>

<area>
  name  stim         # Area name
  x0     0.0         # Origin wrt stim grid
  y0     0.0         #
  xn   64           # width
  yn   64           # height
  umx    1.0 (um)    # microns per Area grid unit (for now, Area = Stim grid)
</area>

<map>
  name    orimap       # ID for reference
  type    ori          # Type of map
  area    v1           # Area associated with this map
  ncol_x    1.5        # Number of ori columns in X-direction
  phase_x  45.0 (deg)  # Phase of pinwheel centers along x-axis, 0-360
  phase_y  45.0 (deg)  # Phase of pinwheel centers along y-axis, 0-360
  phase_p 315.0 (deg)  # Phase of color around pinwheel center, 0-360
</map>

model_noise_seed 231965       # Controls trial seed

mod_trial_reset  1  # reset state between stimuli, default 1

#--------------------------------------.--------------------------------------#
#                                                                             #
#                                     RGC                                     #
#                                                                             #
#-----------------------------------------------------------------------------#
<pop>
  name rgc
  type retina0_gc0      # Layer type
  area stim
  <icon>
    shape circle
    r 0.7
    g 0.7
    b 0.7
  </icon>

  <geometry>
    type     irregular   # Locations will be irregular
    source   retina0     # Locations to be received from retina mosaic

    # xn,yn are inherited from stim grid
    zn    2             # Two sheets, 0-off, 1-on
  </geometry>

  binocular       0     # 0-monocular, 1-binocular

  sig1 0.1   # For Display Only - no effect on mesh model
  sig2 0.2   # For Display Only - no effect on mesh model
  amp1 1     # For Display Only - no effect on mesh model
  amp2 0.2   # For Display Only - no effect on mesh model

  <input>
    ### This is needed to build the BP to RGC synapses
    name         bp
    type         mesh_bp_to_rgc
    receptor     ex
    pop_origin   bipolar
  </input>

  sum_bp_distrib 0     # 0-Gaussian, 1-uniform

  #### Can we not just set this to 0.0 to get the same effect?
  sum_bp_dist    0.10  # Distance (stim pix) for summing BP signals
                       # Instead of the above, can use 'sum_bp_dist_deg'
  sum_bp_minw    0.10  # Minimum weight (rel to 1) to include in sum
  sum_bp_normw   0.3   # Total weight of all BP inputs
  sum_bp_ccode 111     # Cone code:  111-SML, 010-M only, 011-L+M, ...

  spike_dump_xi  -1    # RGC index, set to -1 to avoid dump
  spike_dump_zi   1    # 0-OFF, 1-ON

  <spike_gen>
    type        poisson      # Spike generation algorithm
    offset0     0.0          # Added *before* scaling [0.0]
    scale       4.0          # Multiplying factor [1.0]
    offset      0.0          # Added *after* scaling [0.0]
    toffset     0.020    (s) # Time offset (delay) added to spikes [0.0]
  </spike_gen>
</pop>
#--------------------------------------.--------------------------------------#
#                                                                             #
#                                   BIPOLAR                                   #
#                                                                             #
#-----------------------------------------------------------------------------#
<pop>
  name bipolar
  type virtual           # This is not a layer for computation
  run_flag 0             # Do not simulate this pop, inherit from mesh model

  area stim              # Coordinate reference is stimulus grid

  <icon>
    shape circle
    r 1.0
    g 1.0
    b 0.0
  </icon>

  <geometry>
    type     irregular   # Locations will be irregular
    source   retina0     # Locations to be received from retina mosaic

    # xn,yn are inherited from stim grid
    zn    2             # Two sheets, 0-off, 1-on
  </geometry>

  <response>
    data_id  photo      # Identifier for .rsp file
    source   retina0    # Source of data within model
    sampling  500.0     # (samples/s)
  </response>

  <response>
    data_id  horiz      # Identifier for .rsp file
    source   retina0    # Source of data within model
    sampling  500.0     # (samples/s)
  </response>

  <response>
    data_id  h2         # Identifier for .rsp file
    source   retina0    # Source of data within model
    sampling  500.0     # (samples/s)
  </response>

  <response>
    data_id  diff       # Identifier for .rsp file
    source   retina0    # Source of data within model
    sampling  500.0     # (samples/s)
  </response>

</pop>
#--------------------------------------.--------------------------------------#
#                                                                             #
#                                   RETINA0                                   #
#                                                                             #
#-----------------------------------------------------------------------------#
<retina0>

  stim_auto_center_mi  -1   # Center stimulus on this mosaic index [-1 ignore]

  stim_override 0            # 0-no override, 1-stimulus ignored and replaced
  stim_override_binary 2079  # 0,L,M,S,all,none - set to 1, all others to 0
  stim_override_delay    1   # 0-full override, 1-override at tn/2, zero before
  stim_override_zero_ci -1   # Set this ci to zero always, -1 to deactivate

  # PHOTORECEPTORS
  photo_delta         0      # 1-Override photo filter with delta-function
  mod_mesh_photo_m1   0.020  # Maxwell kernel, 1/2wid = 1.5*m1 (s)
  mod_mesh_photo_m2   0.040  # Maxwell kernel, 1/2wid = 1.5*m2 (s)
  mod_mesh_photo_a2   0.70   # Maxwell kernel, amplitude of m2 relative to m1
  cone_mosaic_flag    1      # [0] Color mosaic (0-cartesian, 1-mosaic)

  <cone_mosaic>
   #file    mosaic01.txt  # Read from file
    arrangement RegJit    # "Spiral", "RegJit"
    custom_cid_file null  # Reset ConeID's from named file ("null" to ignore)
    gui          0        # Show GUI for cone mosaic [1]
    ecc          1.5      # (degr) Eccentricity, for density [-1.0 ignore]
    degpermm     3.3     # degrees per mm on retina
    ncone     11600        # number of cones to create (extra discarded)
    seed_loc  1777        # randomization of cone locations
    noise        0.3      # amplitude of spatial noise, 0..1
    seed_col   1977       # randomization of cone color (L,M,S) - Red Center

    lm_ratio     1.5   # L:M cone ratio
    prob_s       0.0   # S cone probability [Ignored if 'regular_s' > 0]
    regular_s    3     # Leave this many cones between S cones (1,2,3,...)

    rgb_here

    out_id   0               # mosaic index for dump (GUI shows indices)
  </cone_mosaic>

  # QUANTAL NOISE
  noise_factor        0.0    # Quantal noise scaling factor

  #
  # HORIZONTAL MESH
  #
  mesh_type           1      # Use a hexagonal mesh [0-cartesian]

  <h_mesh>
      name  h1
      # Note, gh, gp and dt are interpreted differently when mesh_type = 1
      gh     1.80    # Difference fraction per small time step
      gp     0.064   # Time from 1 to 1/e, if 'gh' is 0.0
      dt     0.02    # Time increment (time units); Must be <= 1.0
      w_s    0.0     # S-cone input weight to H1 mesh
      w_m    1.0     # M-cone input weight to H1 mesh
      w_l    1.0     # L-cone input weight to H1 mesh
  </h_mesh>

  <h_mesh>
      name  h2
      gh     1.80    # Difference fraction per small time step
      gp     0.064   # Time from 1 to 1/e, if 'gh' is 0.0
      dt     0.02    # Time increment (time units); Must be <= 1.0
      w_s    0.7     # S-cone input weight to H2 mesh
      w_m    0.15    # M-cone input weight to H2 mesh
      w_l    0.15    # L-cone input weight to H2 mesh
  </h_mesh>

  #
  # BIPOLAR DIFF
  #
  mesh_whc            1.0    # Weight of HC signal in diff. (1.0 is balanced)
  bipolar_s_wh1       0.0    # 0.0 - means that H1's do not influence S-bipolar
  bipolar_s_wh2       1.0    # Weight of H2 signal for S-bipolar

  bipolar_lm_wh1      1.0    # 0.0 - means that H1's do not influence lm-bipolar
  bipolar_lm_wh2      0.2    # Weight of H2 signal for lm-bipolar


  # GAIN CONTROL
  mesh_gain_hp_flag   0      # Apply the gain-controlled HP filtering (0)
  mesh_lp_tau         0.004  # (s) 1/alpha for LP-filter of 'diff' (0-none)
  mesh_gsig_mean      0.6    # gain1 value which maps to 0.5 * lp
  mesh_gsig_slope     10.0   # slope of sigmoid at gsig_mean
  mesh_gain_inhib_g2  0      # (0) 1-apply 'gain2' as 'gti' for IFC spike-gen
  mesh_lp2_tau        0.050  # (s) 1/alpha for LPfilter of 'gain2' (0-no LP)

  # ADAPTATION
  ad1_tau            20.0    # (s) Adaptation tau, Stim-Horiz difference [0.0]
  ad1_amp             1.0    # Adaptation ampl [0.0], set < 1 to weaken
  ad1_t0              0.020  # (s) Time to set ad1 reference

#   ad1_init_l    0.43
#   ad1_init_m    0.43
#   ad1_init_s    0.35

  # ON/OFF
  mesh_off_flag       0      # 0/1 = ON/OFF cell [0], negate before IFC

  # DUMPING OUTPUT
  mesh_3d_dump_file  null    # Flag to write 3D data, "null"
  mesh_display_type   hc     # "hc" default, also "diff"
  mesh_dump_all       0      # Write intermediate responses to dump file (0)
  mesh_dump_prep      0      # Write fixed traces to a dump file (0)
  mesh_dump_slice_t  -1.0    # Time for slice [-1 for none]
  mesh_dump_slice_x   0.0    # x-position for slice (deg)
  mesh_dump_hex       0      # Dump traces for hex mesh (should unify w/ above)

  #
  #  New way of dumping, should make the above conform to this.
  #
  mesh_dump_type    null      # 'h_v_dist', 'mosaic_coord'
  mesh_dump_file  results/pl_files/h1.dist.pl  # File name
  mesh_dump_cid     2079      # Reference cone ID for dump
  mesh_dump_tsec     -1.0     # Time reference (s), -1.0 for max time

</retina0>
