#!/bin/bash

# make this a subroutine
function run {
    wm mod $1/$2.moo \
	stim/$3.stm \
	response/${RESP_FILE}.rsp  tn ${TN} \
	retina0/h_mesh.h1/gp ${H1GP} \
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

#-- Set default parameters
H1GP=0.1
H2GP=0.6
H2GH=1.8
H2S=0.7
H2M=0.15
H2L=0.15
H2W=0.2
TN=512

# Get analysis option
analysis=(siso coneiso h1 h2 h1_spat mosaic gui)

MODEL=macaque
OPTS=()
args=("$@")
i=0
while [ $i -lt $# ]; do

    if [[ ${args[$i]} == human ]]
    then
	MODEL=human
    fi
    if [[ ${args[$i]} =~ $analysis ]]
    then
	OPTS+=(${args[$i]})
    fi
    if [ ${args[$i]} == "-P" ]
    then
	i=$(($i+1))
	H1GP=${args[$i]}
    fi
    if [ ${args[$i]} == "-p" ]
    then
	i=$((i+1))
	H2GP=${args[$i]}
    fi
    if [ ${args[$i]} == "-h" ]
    then
	i=$((i+1))
	H2GH=${args[$i]}
    fi
    if [ ${args[$i]} == "-s" ]
    then
	i=$((i+1))
	H2S=${args[$i]}
    fi
    if [ ${args[$i]} == "-m" ]
    then
	i=$((i+1))
	H2M=${args[$i]}
    fi
    if [ ${args[$i]} == "-l" ]
    then
	i=$((i+1))
	H2L=${args[$i]}
    fi
    if [ ${args[$i]} == "-w" ]
    then
	i=$((i+1))
	H2W=${args[$i]}
    fi
    if [ ${args[$i]} == "-t" ]
    then
	i=$((i+1))
	TN=${args[$i]}
    fi
    i=$((i+1))
done

#-- Print some info about parameters
# print this to a records file?
echo "h1 gp is set to: $H1GP"
echo "h2 gp is set to: $H2GP"
echo "h2 gh is set to: $H2GH"
echo "model is set to: $MODEL"
echo "h2 l weight is set to: $H2L"
echo "h2 m weight is set to: $H2M"
echo "h2 s weight is set to: $H2S"
echo "h2 lm bioplar is set to: $H2W"
echo "analysis option: $OPTS"
echo " "

#-- Change the model behavior based on command line input
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

elif [ $OPTS == "h1_spat" ]
then
    STIM_OVERRIDE_BINARY=all
    STIM_OVERRIDE=1

elif [ $OPTS == "coneiso" ]
then    
    STIM_FILE=cone_iso_step
    RESP_FILE=retina_line

elif [ $OPTS == "siso" ]
then
    STIM_FILE=s_iso_step
    RESP_FILE=retina_line
fi

#else print some help info

###Handle verbose option

#-- Delete old output files
if [ -e "results/pl_files/$OUT_FILE" ] 
then
    rm results/pl_files/${OUT_FILE}
    echo "rm results/pl_files/rm $OUT_FILE"
fi	

#-- Perform the simulation(s)
if [ $OPTS == "mosaic" ]
then
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tN ${TN}  gui_flag 1 \
	retina0/mesh_dump_type mosaic_coord \
	retina0/mesh_dump_file zz.mosaic

elif [ $OPTS == "gui" ]
then
    wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
	response/retina.rsp  tn ${TN}  \
	gui_flag 1
else

# Can now loop
#for m in $MODELS; do
run ${MODEL} ${MOO_FILE} ${STIM_FILE}

fi

# dump results when necessary
~/Projects/wmbuild/bin/ndutil nd2text results/nd_files/zz.nd \
    results/txt_files/zz.txt 

#-- Plotting routines
# Handle more options. 
if [[ $OPTS == "h1" || $OPTS == "h2" ]]
then
    python results ${OPTS} ${MODEL}
fi

if [[ $OPTS == "h1_spat" || $OPTS == "siso" ]]
then
    java -jar ~/Projects/wmbuild/nd.jar results/nd_files/zz.nd
fi

echo "end script"
echo "--------------"
echo " "