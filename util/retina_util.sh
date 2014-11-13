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
    echo "$out"
}

function stim_gen {
    
    # Decide which file to start with
    local fname=iso_step
    if [ $2 == spot ]
    then
        fname=step_spot
    fi

    # Paste the first part of the stimulus file
    cat stim/${fname}.stm > stim/cone_iso_step.stm

    # Paste the second part of the stimulus file
    if [[ $1 == siso || $1 == miso || $1 == liso ]]
    then
	python pycomp/cone_iso.py $1 stockman  ${FUND} >> stim/cone_iso_step.stm
    elif [ $1 == coneiso ] 
    then
	python pycomp/cone_iso.py siso stockman ${FUND} >> stim/cone_iso_step.stm
	python pycomp/cone_iso.py coneiso stockman ${FUND} >> \
	    stim/cone_iso_step.stm
    fi
}

function knn_resp {
    
    # Paste the first part of the stimulus file
    cat response/header.rsp > response/knn_resp.rsp

    # Paste the second part of the stimulus file
    python pycomp/nearest_neighbor.py 3690 50 >> response/knn_resp.rsp

}

function save_defaults {
    # remove file with old values
    rm util/default_vars.sh

    # create new file with current values
    echo "#! /bin/bash" >> util/default_vars.sh
    echo " " >> util/default_vars.sh
    echo "MODEL=$MODEL" >> util/default_vars.sh
    echo "FUND=$FUND" >> util/default_vars.sh
    echo "SHAPE=$SHAPE" >> util/default_vars.sh
    echo "H1GP=$H1GP" >> util/default_vars.sh
    echo "H1GH=$H1GH" >> util/default_vars.sh
    echo "H1P0=$H1P0" >> util/default_vars.sh
    echo "H1ES=$H1ES" >> util/default_vars.sh
    echo "H2GP=$H2GP" >> util/default_vars.sh
    echo "H2GH=$H2GH" >> util/default_vars.sh
    echo "H2GH=$H2GH" >> util/default_vars.sh
    echo "H2P0=$H2P0" >> util/default_vars.sh
    echo "H2S=$H2S" >> util/default_vars.sh
    echo "H2M=$H2M" >> util/default_vars.sh
    echo "H2L=$H2L" >> util/default_vars.sh
    echo "H2W=$H2W" >> util/default_vars.sh
    echo "TN=$TN" >> util/default_vars.sh
}


function dump_results {
    if [[ $(exists_in ${OPTS} "${dump[*]}") == true  || $1 == -f ]]
    then
	~/Projects/wmbuild/bin/ndutil nd2text \
	    results/nd_files/zz.nd \
	    results/txt_files/zz.txt 
    fi
}


function change_parameters {
    DUMP_CID=3689 # macaque
    if [ $MODEL == "human" ]
    then
	DUMP_CID=2079
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
    
    if [ $OPTS == "h1" ]
    then
	OUT_FILE=h1.dist.pl
	STIM_OVERRIDE=1
	MESH_DUMP_TYPE=h_v_dist

    elif  [ $OPTS == "h2" ]
    then
	HVAR=h1 # flip around so changing h2 in moo file
	MOO_FILE=Ret_Mesh_H2_H1_reverse
	OUT_FILE=h2.dist.pl
	STIM_OVERRIDE=1
	MESH_DUMP_TYPE=h_v_dist

    elif [ $OPTS == "h_time" ]
    then
	STIM_OVERRIDE_BINARY=all
	STIM_OVERRIDE=1

    elif [ $(exists_in $OPTS $iso_cond) == true ]
    then
	STIM_FILE=cone_iso_step
	RESP_FILE=retina_line
	
    elif [[ $OPTS == "knn" || $OPTS == "s_dist" ]]
    then
	knn_resp
	stim_gen siso ${SHAPE}
	STIM_FILE=cone_iso_step
	RESP_FILE=knn_resp

    elif [ $OPTS == "h_sf" ]
    then
	STIM_FILE=sine_sf
	RESP_FILE=retina_line

    fi

}


function change_sys_matrix() {
    sys=$(python pycomp/cone_iso.py sys stockman ${FUND})
    perl -p -e "s/rgb_here/$sys/g" ${MODEL}/${MOO_FILE}.moo > ${MODEL}/run.moo
}


function print_info {
    if [ ${#OPTS[@]} -eq 0 ]; then

	echo -e "\nretina.sh\n"
	echo -e "Options:"
	echo -e "========================"
	echo -e "-model\t MODEL"
	echo -e "-fund\t FUND"
	echo -e "-shape\t SHAPE"
	echo -e "-P\t H1GP"
	echo -e "-H\t H1GH"
	echo -e "-T\t H1P0 (percent0)"
	echo -e "-E\t H1ES (e_seed)"
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
	echo "h1 gp is set to: $H1GP"
	echo "h1 gh is set to: $H1GH"
	echo "h1 percent0 is set to: $H1P0"
	echo "h1 e_seed is set to: $H1ES"
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

function delete_old_file {
    if [ -e "results/pl_files/$OUT_FILE" ] 
    then
	rm results/pl_files/${OUT_FILE}
	echo "rm results/pl_files/rm $OUT_FILE"
    fi	
}


function run_s_dist_analysis {

    # make dir for data if doesn't exist already
    if [ ! -d "results/txt_files/s_dist" ]
    then
	mkdir "results/txt_files/s_dist"
    fi

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
	
	# dump the results to a text file
	dump_results -f

	# rename dumped data, move into dir (make if doesn't exist)
	mv "results/txt_files/zz.txt" "results/txt_files/s_dist/$H2ES.txt"

	# increase count
	count=$(($count+1))

    done

    # save parameters
    print_info > "results/txt_files/s_dist/params.txt"

}

function run_wm {
    # if stimulus condition is an iso_cond then gen stim file
    if [[ $(exists_in ${OPTS} ${iso_cond}) == true ]] 
    then
	stim_gen ${OPTS} ${SHAPE} 
    fi

    wm mod $1/run.moo \
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
	retina0/bipolar_lm_wh2 ${H2W} \
	retina0/stim_override ${STIM_OVERRIDE}\
        retina0/mesh_dump_type ${MESH_DUMP_TYPE} \
	retina0/mesh_dump_cid ${MESH_DUMP_CID} \
	retina0/stim_override_binary ${STIM_OVERRIDE_BINARY}
}


function run_mosaic {
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/test_flash.stm \
	response/retina.rsp  tN ${TN}  gui_flag 1 \
	retina0/mesh_dump_type mosaic_coord \
	retina0/mesh_dump_file zz.mosaic
    
    python pycomp mosaic

}


function run_gui {
    wm mod ${MODEL}/run.moo stim/test_gray.stm \
	response/retina.rsp  tn ${TN}  \
	gui_flag 1
}