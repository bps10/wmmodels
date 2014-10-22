#!/bin/bash

function check_arg {
    local val=$1
    local default=$2
    if [ $val ==  ${args[$i]} ]
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

    cat stim/iso_step.stm > stim/cone_iso_step.stm
    if [[ $1 == siso || $1 == miso || $1 == liso ]]
    then
	python pycomp/cone_iso.py $1 1 >> stim/cone_iso_step.stm
    elif [ $1 == coneiso ] 
    then
	python pycomp/cone_iso.py siso 1 >> stim/cone_iso_step.stm
	python pycomp/cone_iso.py coneiso 1 >> stim/cone_iso_step.stm
    fi
}

function save_defaults {
    # remove file with old values
    rm util/default_vars.sh

    # create new file with current values
    echo "#! /bin/bash" >> util/default_vars.sh
    echo " " >> util/default_vars.sh
    echo "MODEL=$MODEL" >> util/default_vars.sh
    echo "H1GP=$H1GP" >> util/default_vars.sh
    echo "H1GH=$H1GH" >> util/default_vars.sh
    echo "H2GP=$H2GP" >> util/default_vars.sh
    echo "H2GH=$H2GH" >> util/default_vars.sh
    echo "H2S=$H2S" >> util/default_vars.sh
    echo "H2M=$H2M" >> util/default_vars.sh
    echo "H2L=$H2L" >> util/default_vars.sh
    echo "H2W=$H2W" >> util/default_vars.sh
    echo "TN=$TN" >> util/default_vars.sh
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
	MOO_FILE=Ret_Mesh_H2_H1_reverse

    elif [ $OPTS == "h_time" ]
    then
	STIM_OVERRIDE_BINARY=all
	STIM_OVERRIDE=1

    elif [[ $(exists_in $OPTS $iso_cond) ]]
    then    
	STIM_FILE=cone_iso_step
	RESP_FILE=retina_line
    fi
}

function print_info {
    if [ ${#OPTS[@]} -eq 0 ]; then

	echo -e "\nretina.sh\n"
	echo -e "Options:"
	echo -e "========================"
	echo -e "-model\t MODEL"
	echo -e "-P\t H1GP"
	echo -e "-H\t H1GH"
	echo -e "-p\t H2GP"
	echo -e "-h\t H2GH"
	echo -e "-s\t H2S"
	echo -e "-m\t H2M"
	echo -e "-l\t H2L"
	echo -e "-w\t H2W"
	echo -e "-t\t TN"

	exit 1

    else
	echo " "
	echo "h1 gp is set to: $H1GP"
	echo "h1 gh is set to: $H1GH"
	echo "h2 gp is set to: $H2GP"
	echo "h2 gh is set to: $H2GH"
	echo "model is set to: $MODEL"
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

function run_wm {
    # if stimulus condition is an iso_cond then gen stim file
    if [[ $(exists_in ${OPTS} ${iso_cond}) ]] 
    then
	stim_gen ${OPTS}
    fi

    wm mod $1/$2.moo \
	stim/$3.stm \
	response/${RESP_FILE}.rsp  tn ${TN} \
	retina0/h_mesh.h1/gp ${H1GP} \
	retina0/h_mesh.h1/gh ${H1GH} \
	retina0/h_mesh.${HVAR}/gp ${H2GP} \
	retina0/h_mesh.${HVAR}/gh ${H2GH} \
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
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tN ${TN}  gui_flag 1 \
	retina0/mesh_dump_type mosaic_coord \
	retina0/mesh_dump_file zz.mosaic
    
    python pycomp mosaic

}


function run_gui {
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tn ${TN}  \
	gui_flag 1
}