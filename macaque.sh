#!/bin/bash

# Params
H1GP=0.1
H1GH=0.8
H1W=0.7
H2GP=1.0
H2GH=0.8
H2W=0.4
RAN_S=false

#---- sub routines ----#
function run_model {
    local analysis=$1
    if [ "$2" == "foo" ]
    then
	local secondopt=
    else
	local secondopt=$2 # often doesn't exist
    fi
    if [ -z $3 ]
    then 
	local shape=uniform
    else 
	local shape=$3
    fi

    # print out what we are doing
    echo ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape \
	noblock $analysis $secondopt

    # now run the model
    ./retina.sh -model macaque -P $H1GP -H $H1GH -W $H1W \
	-p $H2GP -h $H2GH -w $H2W -ran_s $RAN_S -shape $shape \
	noblock $analysis $secondopt
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
cp results/pl_files/h2.dist.pl results/macaque/horiz/h2.dist.pl

run_model h_time
cp results/nd_files/zz.nd results/macaque/horiz/h_time.nd

run_model plot verbose
cp results/img/h_time_const0.svg results/macaque/horiz/h_time_const0.svg
cp results/img/h_space_const.svg results/macaque/horiz/h_space_const.svg

### step function
mkdir -p results/macaque/step/

run_model step
cp results/nd_files/zz.nd results/macaque/step/step_func_response.nd
cp results/img/stack_t0.svg results/macaque/step/step_func.svg

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
mkdir -p results/macaque/tf_tuning/

run_model h_tf
cp results/nd_files/zz.nd results/macaque/tf_tuning/tf_tuning.nd
cp results/img/h_tf_tuning.svg results/macaque/tf_tuning/h_tf_tuning.svg

run_model plot bp_tf
cp results/img/bp_tf_tuning.svg results/macaque/tf_tuning/bp_tf_tuning.svg

run_model plot rgc_tf
cp results/img/rgc_tf_tuning.svg results/macaque/tf_tuning/rgc_tf_tuning.svg

### s_dist plots
mkdir -p results/macaque/s_dist/

for i in `seq 1 2`; do
   
    if [ $i -eq 1 ]
    then
	RAN_S=true # change param to random
	DIR=random
    else
	RAN_S=false
	DIR=nonrandom
    fi
    mkdir -p results/macaque/s_dist/$DIR/


# save mosaic files
    run_model mosaic
    cp mosaics/model.mosaic results/macaque/s_dist/$DIR/$DIR.mosaic
    cp results/img/mosaic.svg results/macaque/s_dist/$DIR/mosaic.svg

# Uniform
    run_model s_dist foo uniform
    cp results/nd_files/s_dist/2658.nd results/macaque/s_dist/$DIR/uniform.nd
    
    cp results/img/s_dist_scatter.svg \
    results/macaque/s_dist/$DIR/uniform_scatter.svg

    cp results/img/s_dist_hist.svg \
    results/macaque/s_dist/$DIR/uniform_hist.svg

# 5 cpd grating
    run_model s_dist foo grating
    cp results/nd_files/s_dist/2658.nd results/macaque/s_dist/$DIR/grating.nd

    cp results/img/s_dist_scatter.svg \
	results/macaque/s_dist/$DIR/grating_scatter.svg

    cp results/img/s_dist_hist.svg \
	results/macaque/s_dist/$DIR/grating_hist.svg

# Small spot
## also need to change cone here for the random case, otherwise not centered
    run_model s_dist foo spot
    cp results/nd_files/s_dist/2658.nd results/macaque/s_dist/$DIR/spot.nd

    cp results/img/s_dist_scatter.svg \
	results/macaque/s_dist/$DIR/spot_scatter.svg

    cp results/img/s_dist_hist.svg \
	results/macaque/s_dist/$DIR/spot_hist.svg
done