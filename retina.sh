#!/bin/bash

MODEL=human
H1GP=0.1
H2GP=0.6
H2GH=1.8
H2S=0.7
H2M=0.15
H2L=0.15
H2W=0.3
OPTS=h1

while getopts d:p:g:h:s:m:l:w:o: opt; do
  case $opt in
    d)
      MODEL=$OPTARG
      ;;
    p)
      H1GP=$OPTARG
      ;;
    g)
      H2GP=$OPTARG
      ;;
    h)
      H2GH=$OPTARG
      ;;
    s)
      H2S=$OPTARG
      ;;
    m)
      H2M=$OPTARG
      ;;
    l)
      H2L=$OPTARG
      ;;
    w)
      H2W=$OPTARG
      ;;
    o)
      OPTS=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

shift $((OPTIND - 1))

echo "h1 gp is set to: $H1GP"
echo "h2 gp is set to: $H2GP"
echo "h2 gh is set to: $H2GH"
echo "model is set to: $MODEL"
echo "h2 l weight is set to: $H2L"
echo "h2 m weight is set to: $H2M"
echo "h2 s weight is set to: $H2S"
echo "h2 lm bioplar is et to: $H2W"
echo "analysis option: $OPTS"
echo " "

if [[ $OPTS == "h1" || $OPTS == "verbose" ]]
	then
		if [ -e "results/pl_files/h1.dist.pl" ] 
			then
				rm results/pl_files/h1.dist.pl
				echo "rm results/pl_files/rm h1.dist.pl"
		fi	
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/test_gray.stm \
		response/retina.rsp  tn 512 \
		retina0/h_mesh.h1/gp ${H1GP} \
		retina0/h_mesh.h2/gp ${H2GP} \
		retina0/h_mesh.h2/gh ${H2GH} \
		retina0/h_mesh.h2/w_s ${H2S} \
		retina0/h_mesh.h2/w_m ${H2M} \
		retina0/h_mesh.h2/w_l ${H2L} \
		retina0/bipolar_lm_wh2 ${H2W} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		if [ $OPTS != "verbose" ]
			then
				python results ${OPTS} ${MODEL}
		fi

fi

if [[ $OPTS == "h2" || $OPTS == "verbose" ]]
	then
		if [ -e "results/pl_files/h2.dist.pl" ] 
			then
				rm results/pl_files/h2.dist.pl
				echo "rm results/pl_files/rm h2.dist.pl"
		fi	
		# Everything is reversed here!
		wm mod ${MODEL}/Ret_Mesh_H2_H1_reverse.moo stim/test_gray.stm \
		response/retina.rsp  tn 512 \
		retina0/h_mesh.h2/gp ${H1GP} \
		retina0/h_mesh.h1/gp ${H2GP} \
		retina0/h_mesh.h1/gh ${H2GH} \
		retina0/h_mesh.h2/w_s ${H2S} \
		retina0/h_mesh.h2/w_m ${H2M} \
		retina0/h_mesh.h2/w_l ${H2L} \
		retina0/bipolar_lm_wh2 ${H2W} \
		retina0/stim_override 1 \
		retina0/mesh_dump_type h_v_dist

		python results ${OPTS} ${MODEL}
fi

if [[ $OPTS == "h1_spat" || $OPTS == "verbose" ]]
	then
		if [ -e "results/nd_files/zz.nd" ]
			then
				rm results/nd_files/zz.nd
		fi
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/test_gray.stm \
		    response/retina.rsp  tn 512 \
			retina0/h_mesh.h1/gp ${H1GP} \
			retina0/h_mesh.h2/gp ${H2GP} \
			retina0/h_mesh.h2/gh ${H2GH} \
		        retina0/h_mesh.h2/w_s ${H2S} \
		        retina0/h_mesh.h2/w_m ${H2M} \
       		        retina0/h_mesh.h2/w_l ${H2L} \
		        retina0/bipolar_lm_wh2 ${H2W} \
			retina0/stim_override 1 \
			retina0/stim_override_binary all

		java -jar ~/Projects/wmbuild/nd.jar results/nd_files/zz.nd
fi

if [ $OPTS == "coneiso" ]
	then
		if [ -e "results/nd_files/zz.nd" ]
			then
				rm results/nd_files/zz.nd
		fi
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/cone_iso_step.stm \
		    response/retina_line.rsp tn 512 \
		    retina0/h_mesh.h1/gp ${H1GP} \
		    retina0/h_mesh.h2/gp ${H2GP} \
		    retina0/h_mesh.h2/gh ${H2GP} \
		    retina0/h_mesh.h2/w_s ${H2S} \
		    retina0/h_mesh.h2/w_m ${H2M} \
		    retina0/h_mesh.h2/w_l ${H2L} \
		    retina0/bipolar_lm_wh2 ${H2W} 

		java -jar ~/Projects/wmbuild/nd.jar results/nd_files/zz.nd
fi


if [ $OPTS == "Siso" ]
	then
		if [ -e "results/nd_files/zz.nd" ]
			then
				rm results/nd_files/zz.nd
		fi
		wm mod ${MODEL}/Ret_Mesh_H2.moo stim/s_iso_step.stm \
		    response/retina_line.rsp tn 512 \
		    retina0/h_mesh.h1/gp ${H1GP} \
		    retina0/h_mesh.h2/gp ${H2GP} \
		    retina0/h_mesh.h2/gh ${H2GP} \
		    retina0/h_mesh.h2/w_s ${H2S} \
		    retina0/h_mesh.h2/w_m ${H2M} \
		    retina0/h_mesh.h2/w_l ${H2L} \
		    retina0/bipolar_lm_wh2 ${H2W}

		java -jar ~/Projects/wmbuild/nd.jar results/nd_files/zz.nd
fi

echo "end script"
echo "--------------"
echo " "