#!/bin/bash

function check_arg {
    local val=$1
    local default=$2
    if [ $val == ${args[$i]} ]
    then
	i=$(($i+1))
	echo ${args[$i]}
    else
	echo $default
    fi
}


function check_gui_flag {

    GUI=0 # do not run gui unless flag is thrown
    if [ $(exists_in gui "${OPTS[*]}") == true ]
    then
	GUI=1
    fi
} 


function check_block_plots_flag {
    BLOCK_PLOTS=block
    if [ $(exists_in noblock "${args[*]}") == true ]
    then
	BLOCK_PLOTS=noblock
    fi
}


function exists_in {
    local var=$1
    local arr=($2)
    out=false
    for i in "${arr[@]}"; do
	if [ $var == $i ]
	then
	    out=true
	fi
    done
    echo $out
}


function change_parameters {
    N_CONES=200 # number of cones used in cone_inputs
    REGULAR_S=4
    # Deal with model specific parameters
    # put these into default param files for each model
    if [ $MODEL == "macaque" ]
    then
	MOSAIC_FILE=nonrandom_model.mosaic
	DUMP_CID=3240 
	SCONE=3690 # (non-random mosaic)

	if [ $RANDOM_S == "true" ] 
	then
	    SCONE=3839 # (random mosaic)
	    MOSAIC_FILE=random_model.mosaic
	    REGULAR_S=0
	fi
    elif [ $MODEL == "human" ]
    then
	DUMP_CID=2203
	SCONE=2204
	MOSAIC_FILE=nonrandom_human_model.mosaic

    elif [ $MODEL == "WT" ]
    then
	DUMP_CID=3039 # L cone to left of center S cone
	SCONE=3049
	if [[ $RANDOM_CONE == true ]]; then
	    MOSAIC_FILE=WT_randomized.mosaic
	    MOSAIC_TXT_FILE=WT_mosaic_randomized.txt
	else
	    MOSAIC_FILE=WT.mosaic
	    MOSAIC_TXT_FILE=WT_mosaic.txt
	fi
	N_CONES=600 # number of cones used in cone_inputs

    elif [ $MODEL == "BPS" ]
    then
	#DUMP_CID=3153 # L cone to left of bottom left 5 S cone patch
	DUMP_CID=3990 # L cone to upper right of dark cone
	SCONE=2914 # the dark cone
	if [[ $RANDOM_CONE == true ]]; then
	    MOSAIC_FILE=BPS_randomized.mosaic
	    MOSAIC_TXT_FILE=BPS_mosaic_randomized.txt
	else
	    MOSAIC_FILE=BPS.mosaic
	    MOSAIC_TXT_FILE=BPS_mosaic.txt
	fi
	N_CONES=600 # number of cones used in cone_inputs
    fi

    # Default settings
    MESH_DUMP_TYPE=null
    MESH_DUMP_CID=${DUMP_CID}
    STIM_OVERRIDE=0
    STIM_FILE=test_gray
    STIM_OVERRIDE_BINARY=${DUMP_CID}
    STIM_OVERRIDE=0
    MOO_FILE=Ret_Mesh_H2
    OUT_FILE=zz.nd
    RESP_FILE=retina
    HVAR=h2
    MESH_DUMP_FILE=h1.dist.pl

    # handle analysis options
    if [ $OPTS == "h1" ]
    then
	STIM_OVERRIDE=1
	MESH_DUMP_TYPE=h_v_dist

    elif  [ $OPTS == "h2" ]
    then
	HVAR=h1 # flip around so changing h2 in moo file
	MESH_DUMP_FILE=h2.dist.pl
	STIM_OVERRIDE=1
	MESH_DUMP_TYPE=h_v_dist

    elif [ $OPTS == "h_time" ]
    then
	STIM_OVERRIDE_BINARY=all
	STIM_OVERRIDE=1

    elif [[ $(exists_in ${OPTS} "${iso_cond[*]}") == true ]] 
    then
	stim_gen ${OPTS} ${SHAPE}
	STIM_FILE=cone_iso_step
	RESP_FILE=retina_line_${MODEL}

    elif [[ $(exists_in ${OPTS[0]} "${knn_cond[*]}") == true || \
	$(exists_in ${OPTS[1]} "${knn_cond[*]}") == true ]]
    then
	# has to be bp cells so that looks at output of h1, h2 vs cone
	knn_resp ${SCONE} $N_CONES bp
	mkdir -p results/txt_files/$MODEL
	mv results/txt_files/nn_results.txt \
	    results/txt_files/$MODEL/nn_results.txt

	RESP_FILE=knn_resp
	# decide which response file to use
	if [[ $OPTS == "vanhat" ]]
	then
	    STIM_FILE=img_vanhat
	else
            # sine wave would require change to analysis.py?
	    stim_gen coneiso ${SHAPE} #full_field
	    STIM_FILE=cone_iso_step
	fi
	
    elif [[ $OPTS == "knn" || $OPTS == "s_dist" ]]
    then
	knn_resp ${SCONE}
	stim_gen siso ${SHAPE}
	STIM_FILE=cone_iso_step
	RESP_FILE=knn_resp

    elif [[ $OPTS == "step" ]]
    then
	STIM_FILE=test_flash
	RESP_FILE=retina_line

    elif [[ $OPTS == "h_sf" || $OPTS == "bp_sf" || $OPTS == "rgc_sf" ]]
    then
	STIM_FILE=sine_sf
	RESP_FILE=retina_line

    elif [[ $OPTS == "h_tf" || $OPTS == "bp_tf" || $OPTS == "rgc_tf" ]]
    then
	STIM_FILE=sine_tf
	RESP_FILE=retina_line

    elif [ $OPTS == "gui" ]
    then

	stim_gen siso ${SHAPE}
	STIM_FILE=img_vanhat
	#STIM_FILE=cone_iso_step
    fi
}


function stim_gen {
    echo 'generating stimulus file'

    # Decide which file to start with
    local fname=iso_step # uniform full field case
    if [ $2 == spot ]
    then
        fname=step_spot_${MODEL}
    elif [ $2 == grating ]
    then
	fname=iso_sine
    elif [ $2 == sine_tf ]
    then
	fname=sine_tf
    elif [ $2 == sine_spot ]
    then
	fname=sine_spot
    else
	if [ $2 != full_field ]
	then
	# let the use know that the shape is not supported.
	    echo Shape $2 not understood. Going with full_field.
	fi
    fi

    # Paste the first part of the stimulus file
    cat stim/${fname}.stm > stim/cone_iso_step.stm

    # Paste the second part of the stimulus file
    if [[ $1 == siso || $1 == miso || $1 == liso ]]
    then
	python pycomp/cone_iso.py $1 stockman  ${FUND} >> \
	    stim/cone_iso_step.stm
    elif [ $1 == coneiso ] 
    then
	python pycomp/cone_iso.py siso stockman ${FUND} >> \
	    stim/cone_iso_step.stm
	python pycomp/cone_iso.py coneiso stockman ${FUND} >> \
	    stim/cone_iso_step.stm
    fi
}


function knn_resp {
    if [ -z "$1" ]; then
	local coneID=${DUMP_CID}
    else
	local coneID=$1
    fi
    if [ -z "$2" ]; then
	local Ncones=100
    else
	local Ncones=$2
    fi
    local cell_type=horiz
    if [ ! -z "$3" ]; then
	cell_type=$3
    fi

    # Paste the first part of the stimulus file
    cat response/header.rsp > response/knn_resp.rsp

    # Paste the second part of the stimulus file
    echo "creating rsp file and computing nearest neighbors"
    echo "mosaic file: $MOSAIC_FILE"
    echo "N cones: $Ncones"
    python pycomp/util/nearest_neighbor.py ${coneID} ${Ncones} ${cell_type} \
	${MOSAIC_FILE} >> response/knn_resp.rsp 

}


function get_save_name {
    random_opt=
    if [[ $RANDOM_CONE == true ]]
    then
	random_opt="_randomized"
    fi
    if [ -z "$1" ]; then
	if [[ ${OPTS[0]} == plot ]]; then
	    name=${OPTS[1]}-H1W${H1W}_H2W${H2W}_H2t${H2P0}${random_opt}
	else
	    name=${OPTS[0]}-H1W${H1W}_H2W${H2W}_H2t${H2P0}${random_opt}
	fi	
    else 
	# use passed variable 1 to create savename
	echo $1-H1W${H1W}_H2W${H2W}_H2t${H2P0}${random_opt}
    fi
}


function save_defaults {
    # remove files with old values
    rm util/default_vars.sh
    rm models/${MODEL}/default_vars.sh

    # create new default util file with current values
    echo "#! /bin/bash" >> models/${MODEL}/default_vars.sh
    echo " " >> util/default_vars.sh
    echo "MODEL=$MODEL" >> util/default_vars.sh
    echo "FUND=$FUND" >> util/default_vars.sh
    echo "SHAPE=$SHAPE" >> util/default_vars.sh
    echo "RANDOM_S=$RANDOM_S" >> util/default_vars.sh
    echo "RANDOM_CONE=$RANDOM_CONE" >> util/default_vars.sh
    echo "TN=$TN" >> util/default_vars.sh
    echo "LM_RATIO=$LM_RATIO" >> util/default_vars.sh

    # create new default model specific file with current values
    echo "#! /bin/bash" >> models/${MODEL}/default_vars.sh
    echo " " >> models/${MODEL}/default_vars.sh
    echo "H1GP=$H1GP" >> models/${MODEL}/default_vars.sh
    echo "H1GH=$H1GH" >> models/${MODEL}/default_vars.sh
    echo "H1P0=$H1P0" >> models/${MODEL}/default_vars.sh
    echo "H1ES=$H1ES" >> models/${MODEL}/default_vars.sh
    echo "H1W=$H1W" >> models/${MODEL}/default_vars.sh
    echo "H2GP=$H2GP" >> models/${MODEL}/default_vars.sh
    echo "H2GH=$H2GH" >> models/${MODEL}/default_vars.sh
    echo "H2P0=$H2P0" >> models/${MODEL}/default_vars.sh
    echo "H2ES=$H2ES" >> models/${MODEL}/default_vars.sh
    echo "H2S=$H2S" >> models/${MODEL}/default_vars.sh
    echo "H2M=$H2M" >> models/${MODEL}/default_vars.sh
    echo "H2L=$H2L" >> models/${MODEL}/default_vars.sh
    echo "H2W=$H2W" >> models/${MODEL}/default_vars.sh
}


function change_sys_matrix() {
    sys=$(python pycomp/cone_iso.py sys stockman ${FUND})
    perl -p -e "s/rgb_here/$sys/g" models/${MODEL}/${MOO_FILE}.moo > \
	models/${MODEL}/run.moo
}


function print_info {
    if [ ${#OPTS[@]} -eq 0 ]; then

	echo -e "\nretina.sh\n"
	echo -e "Options:"
	echo -e "========================"
	echo -e "-model\t MODEL"
	echo -e "-fund\t FUND"
	echo -e "-shape\t SHAPE"
	echo -e "-ran_s\t RANDOM_S"
	echo -e "-ran_cone\t RANDOM_CONE"
	echo -e "-lm_ratio\t LM_RATIO"
	echo -e "-P\t H1GP"
	echo -e "-H\t H1GH"
	echo -e "-T\t H1P0 (percent0)"
	echo -e "-E\t H1ES (e_seed)"
	echo -e "-W\t H1W"
	echo -e "-p\t H2GP"
	echo -e "-h\t H2GH"
	echo -e "-t\t H2P0 (percent0)"
	echo -e "-e\t H2ES (e_seed)"
	echo -e "-s\t H2S"
	echo -e "-m\t H2M"
	echo -e "-l\t H2L"
	echo -e "-w\t H2W"
	echo -e "-t\t TN"

	exit 1

    else
	echo " "
	echo "model is set to: $MODEL"
	echo "fundamentals set to: $FUND"
	echo "stim shape is set to: $SHAPE"
	echo "random S is set to: $RANDOM_S"
	echo "random cone is set to: $RANDOM_CONE"
	echo "LM ratio is set to: $LM_RATIO"
	echo "h1 gp is set to: $H1GP"
	echo "h1 gh is set to: $H1GH"
	echo "h1 percent0 is set to: $H1P0"
	echo "h1 e_seed is set to: $H1ES"
	echo "h1 lm bipolar is set to: $H1W"
	echo "h2 gp is set to: $H2GP"
	echo "h2 gh is set to: $H2GH"
	echo "h2 percent0 is set to: $H2P0"
	echo "h2 e_seed is set to: $H2ES"
	echo "h2 l weight is set to: $H2L"
	echo "h2 m weight is set to: $H2M"
	echo "h2 s weight is set to: $H2S"
	echo "h2 lm bioplar is set to: $H2W"
	echo "analysis option: $OPTS"
	echo " "
    fi
    
    if [ $OPTS == plot ]
    then
	echo ""
	echo "plotting most recent simulation"
	echo ""
    fi
}


function run_s_dist_analysis {

    # make dir for data if doesn't exist already
    if [ ! -d "results/nd_files/$MODEL/s_dist" ]
    then
	mkdir "results/nd_files/$MODEL/s_dist"
	echo "made dir results/nd_files/$MODEL/s_dist"
    fi
    
    # cp nn_results.txt into s_dist folder
    cp results/txt_files/nn_results.txt \
	results/nd_files/${MODEL}/s_dist/nn_results.txt
    
    # get random numbers
    rnums=$(python pycomp/util/gen_rand.py)

    # parse into list
    rnums=(`echo $rnums | tr ',' ' '`)

    if [[ $H2P0 == "0.0" || $H2P0 == "0" ]] 
    then # only need to run once
	rnums=(${rnums[0]})
    fi

    local count=0
    # iterate over all numbers in the list
    for i in ${rnums[*]}; do
	# set new H2 e_seed
	H2ES=$i

	# print out params to keep track of where we are
	echo "Trial: $count, H2ES: $H2ES"

	# run wm with new H2 e_seed
	run_wm ${MODEL} ${STIM_FILE}

	# rename dumped data, move into dir (make if doesn't exist)
	mv "results/nd_files/$MODEL/s_dist.nd" \
	    "results/nd_files/$MODEL/s_dist/$H2ES.nd"

	# increase count
	count=$(($count+1))

    done

    # save parameters
    print_info > "results/nd_files/$MODEL/s_dist/params.txt"

    # save defaults
    save_defaults
}


function run_h_space {
    
	echo -e "\nrunning H1 simulation\n"
	OPTS=h1
	change_parameters
	run_wm ${MODEL} ${STIM_FILE}

	echo -e "\nrunning H2 simulation\n"
	OPTS=h2
	change_parameters
	run_wm ${MODEL} ${STIM_FILE}
	
	# change $OPTS back to h_space for plotting
	OPTS=h_space
}


function run_verbose {
    run_h_space
    
    echo -e "\nrunning h_time simulation\n"
    OPTS=h_time
    change_parameters
    get_save_name
    run_wm ${MODEL} ${STIM_FILE}
    
    echo -e "\nrunning sf simulation\n"
    OPTS=h_sf
    change_parameters
    run_wm ${MODEL} ${STIM_FILE}
    
    echo -e "\nrunning iso (cone inputs) simulation\n"
    OPTS=iso_classify
    change_parameters
    run_wm ${MODEL} ${STIM_FILE}
    
    # Change $name and $OPTS back to verbose for plotting
    OPTS=verbose
    get_save_name
    BLOCK_PLOTS=noblock # don't block plots
}


function run_wm {

    wm mod models/$1/run.moo \
	stim/$2.stm \
	response/${RESP_FILE}.rsp  tn ${TN} \
	retina0/h_mesh.h1/gp ${H1GP} \
	retina0/h_mesh.h1/gh ${H1GH} \
	retina0/h_mesh.h1/percent0 ${H1P0} \
	retina0/h_mesh.h1/e_seed ${H1ES} \
	retina0/h_mesh.${HVAR}/gp ${H2GP} \
	retina0/h_mesh.${HVAR}/gh ${H2GH} \
	retina0/h_mesh.${HVAR}/percent0 ${H2P0} \
	retina0/h_mesh.${HVAR}/e_seed ${H2ES} \
	retina0/h_mesh.${HVAR}/w_s ${H2S} \
	retina0/h_mesh.${HVAR}/w_m ${H2M} \
	retina0/h_mesh.${HVAR}/w_l ${H2L} \
	retina0/bipolar_lm_wh1 ${H1W} \
	retina0/bipolar_lm_wh2 ${H2W} \
	retina0/cone_mosaic/lm_ratio ${LM_RATIO} \
	retina0/cone_mosaic/regular_s ${REGULAR_S} \
	retina0/cone_mosaic/file mosaics/${MOSAIC_TXT_FILE} \
	retina0/stim_override ${STIM_OVERRIDE}\
        retina0/mesh_dump_type ${MESH_DUMP_TYPE} \
	retina0/mesh_dump_cid ${MESH_DUMP_CID} \
	retina0/mesh_dump_file results/pl_files/${MESH_DUMP_FILE} \
	retina0/stim_override_binary ${STIM_OVERRIDE_BINARY} \
    	gui_flag ${GUI}

    if [ $GUI == 0 ]
    then
	echo "saving output files"
	if [[ $OPTS == "h2" || $OPTS == "h1" ]]
	then
	    mkdir -p results/pl_files/${MODEL}
	    savename=$(get_save_name ${OPTS})
	    mv results/pl_files/${OPTS}.dist.pl \
		results/pl_files/${MODEL}/${savename}.dist.pl
	elif [[ $OPTS == "h_sf" || $OPTS == "bp_sf" || $OPTS == "rgc_sf" ]]
	then
	    mkdir -p results/nd_files/${MODEL}
	    savename=$(get_save_name sf)
	    mv results/nd_files/zz.nd results/nd_files/${MODEL}/${savename}.nd
	elif [[ $OPTS == "h_tf" || $OPTS == "bp_tf" || $OPTS == "rgc_tf" ]]
	then
	    mkdir -p results/nd_files/${MODEL}
	    savename=$(get_save_name tf)
	    mv results/nd_files/zz.nd results/nd_files/${MODEL}/${savename}.nd
	elif [[ $OPTS == "iso_classify" || $OPTS == "cone_inputs" ]]
	then
	    mkdir -p results/nd_files/${MODEL}
	    savename=$(get_save_name sml_iso)
	    mv results/nd_files/zz.nd results/nd_files/${MODEL}/${savename}.nd
	else
	    mkdir -p results/nd_files/${MODEL}
	    savename=${name}
	    mv results/nd_files/zz.nd results/nd_files/${MODEL}/${savename}.nd
	fi
    fi

}


function run_mosaic {
    # remove old mosaic model
    rm mosaics/model.mosaic

    wm mod models/${MODEL}/run.moo stim/test_flash.stm \
	response/retina.rsp  tn ${TN}  gui_flag ${GUI} \
	retina0/cone_mosaic/lm_ratio ${LM_RATIO} \
	retina0/cone_mosaic/regular_s ${REGULAR_S} \
	retina0/mesh_dump_type mosaic_coord \
	retina0/mesh_dump_file mosaics/model.mosaic
    
    python pycomp ${MOSAIC_FILE} ${name} ${MODEL} ${BLOCK_PLOTS}

}

