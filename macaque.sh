#!/bin/bash

# Params
H1GP=0.1
H1GH=0.8
H1W=0.7
H2GP=1.0
H2GH=0.8
H2W=0.4

#---- sub routines ----#
function run_model {
    local analysis=$1
    local secondopt=$2 # often doesn't exist

    ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W noblock $analysis $secondopt
}
# -------------------- #

### make dir for macaue if it doesn't exist
mkdir -p results/macaque/

### save parameters to directory
echo ./retina.sh params > results/macaque/start_params

### start with H1 & H2 space and time plots
mkdir -p results/macaque/horiz/

run_model h1
cp results/pl_files/h1.dist.pl results/macaque/horiz/h1.dist.pl

run_model h2
cp results/pl_files/h1.dist.pl results/macaque/horiz/h1.dist.pl

run_model h_time
cp results/nd_files/zz.nd results/macaque/horiz/h_time.nd

run_model plot verbose
cp results/img/h_time_const0.svg results/macaque/horiz/h_time_const0.svg
cp results/img/h_space_const.svg results/macaque/horiz/h_space_const.svg

### coneiso plots
mkdir -p results/macaque/coneiso/

run_model coneiso
cp results/nd_files/zz.nd results/macaque/coneiso/coneiso.nd
cp results/img/stack_t0.svg results/macaque/coneiso/siso.svg
cp results/img/stack_t1.svg results/macaque/coneiso/miso.svg
cp results/img/stack_t2.svg results/macaque/coneiso/liso.svg

### sf tuning plots
mkdir -p results/macaque/sf_tuning/

run_model h_sf
cp results/nd_files/zz.nd results/macaque/sf_tuning/sf_tuning.nd
cp results/img/h_sf_tuning.svg results/macaque/sf_tuning/h_sf_tuning.svg

run_model plot bp_sf
cp results/img/bp_sf_tuning.svg results/macaque/sf_tuning/bp_sf_tuning.svg

run_model plot rgc_sf
cp results/img/rgc_sf_tuning.svg results/macaque/sf_tuning/rgc_sf_tuning.svg

### tf tuning plots

### s_dist plots
mkdir -p results/macaque/s_dist/

# random and non-random dirs
mkdir -p results/macaque/s_dist/random/
mkdir -p results/macaque/s_dist/nonrandom/