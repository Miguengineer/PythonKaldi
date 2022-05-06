#!/bin/bash

# V1.0. Last edit: Miguel Duran (09/2021)
# Description: Creates alignment matrix. 
# Conf files:
# 1) conf_frame_size.txt found in /conf


database_path=../Databases/
# Database folders. TODO: Automatically fetch folder names
dataset_list=("Abril_2020"  "Mayo_2020_P1"  "Mayo_2020_P2"  "Mayo_2020_P3"  "Junio_2020"  "Julio_2020" "Agosto_2020" "Septiembre_2020" "Marzo_2021" "ship1" "ship2" "ship3" "ship4" "ship5" "ship6" "ship7" "ship8" "ship9" "ant_noise1" "ant_noise2" "ant_noise3" "ant_noise4" "ant_noise5")
matlab_src=matlab_src
echo "** WARNING: folders ALIPHO and dataset_units will be removed"
echo "Started creating alignment matrix" 
rm -rf ALIPHO
mkdir ALIPHO
rm -rf dataset_units
mkdir dataset_units
for data_name in ${dataset_list[*]}; do
	cp -r ${database_path}${data_name} ALIPHO/${data_name}
#	cp $matlab_src/prepare_data_v2.m ALIPHO/$data_name
#	cp ${matlab_src}/ALIPHO_save.m ALIPHO/${data_name}
#	cp ${matlab_src}/copy-feats ALIPHO/${data_name}
#	cp ${matlab_src}/frame_annotation.m ALIPHO/${data_name}
#	cp ${matlab_src}/create_ali.m ALIPHO/${data_name}
#	cp ${matlab_src}/eliminarSil.m ALIPHO/${data_name}
#	cp ${matlab_src}/etiquetas.txt ALIPHO/${data_name}
#	cp ${matlab_src}/etiquetaScript.m ALIPHO/${data_name}
#	cp ${matlab_src}/extractAnot.m ALIPHO/${data_name}
#	cp ${matlab_src}/ali_str2int.m ALIPHO/${data_name}
#	cp ${matlab_src}/feature_extraction.m ALIPHO/${data_name}
#	cp ${matlab_src}/extractAnot.m ALIPHO/${data_name}
#	cp ${matlab_src}/generate_kaldi_files.m ALIPHO/${data_name}
#	cp ${matlab_src}/generate_labels.m ALIPHO/${data_name}
#	cp ${matlab_src}/GGM_PHO_write_3.m ALIPHO/${data_name}
#	cp ${matlab_src}/prepare_data.m ALIPHO/${data_name}
#	cp ${matlab_src}/make_ali.m ALIPHO/${data_name}
#	cp ${matlab_src}/mel_filterbanks.m ALIPHO/${data_name}
#	cp ${matlab_src}/procFrame.m ALIPHO/${data_name}
#	cp ${matlab_src}/readkaldifeatures.m ALIPHO/${data_name}
#	cp ${matlab_src}/removeRows.m ALIPHO/${data_name}
#	cp ${matlab_src}/splitTest.m ALIPHO/${data_name}
#	cp ${matlab_src}/splitTestManual.m ALIPHO/${data_name}
#	cp ${matlab_src}/unir12.m ALIPHO/${data_name}
#	cp ${matlab_src}/writekaldifeatures.m ALIPHO/${data_name}
#	cp conf/conf_frame_size.txt ALIPHO/${data_name}
done

# Copy Matlab scripts to ALIPHO.
cp $matlab_src/prepare_data_v2.m ALIPHO
#cp ${matlab_src}/ALIPHO_save.m ALIPHO
#cp ${matlab_src}/copy-feats ALIPHO
#cp ${matlab_src}/create_ali.m ALIPHO
#cp ${matlab_src}/frame_annotation.m ALIPHO
#cp ${matlab_src}/eliminarSil.m ALIPHO
#cp ${matlab_src}/etiquetas.txt ALIPHO
#cp ${matlab_src}/etiquetaScript.m ALIPHO
#cp ${matlab_src}/extractAnot.m ALIPHO
#cp ${matlab_src}/ali_str2int.m ALIPHO
#cp ${matlab_src}/feature_extraction.m ALIPHO
#cp ${matlab_src}/extractAnot.m ALIPHO
#cp ${matlab_src}/generate_kaldi_files.m ALIPHO
#cp ${matlab_src}/generate_labels.m ALIPHO
#cp ${matlab_src}/GGM_PHO_write_3.m ALIPHO
#cp ${matlab_src}/prepare_data.m ALIPHO
#cp ${matlab_src}/make_ali.m ALIPHO
#cp ${matlab_src}/mel_filterbanks.m ALIPHO
#cp ${matlab_src}/procFrame.m ALIPHO
#cp ${matlab_src}/readkaldifeatures.m ALIPHO
#cp ${matlab_src}/removeRows.m ALIPHO
#cp ${matlab_src}/splitTest.m ALIPHO
#cp ${matlab_src}/splitTestManual.m ALIPHO
#cp ${matlab_src}/unir12.m ALIPHO
#cp ${matlab_src}/writekaldifeatures.m ALIPHO
cd ALIPHO
matlab -nojvm -nodisplay -nosplash -r prepare_data_v2 


