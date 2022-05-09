#!/bin/bash

# V1.0. Last edit: Miguel Duran (09/2021)


exp_name='HMM-GMM-Base'
database_path=/home/miguel/Database_Filtered
matlab_code_dir=/home/miguel/$exp_name/matlab_src
python_code_dir=/home/miguel/$exp_name/pythonSrc
audio_units_dir=/home/miguel/$exp_name/audio_units
rm -r data
rm -r exp_data
mkdir data
mkdir -p exp_data/train
mkdir exp_data/test
mkdir exp_data/dev
for db_folder in $database_path/*; do
	cp -r $db_folder data
done

cp $python_code_dir/initialize_hmm_gmm.py data
cp $python_code_dir/eliminate_low_count_events.py data
cp $python_code_dir/utils.py data
cp $python_code_dir/preprocessing_tools.py data
cp $python_code_dir/split_dataset_tools.py data
#cp $python_code_dir/Frame.py data
cd data


python -W ignore initialize_hmm_gmm.py $HOME/$exp_name
cp phones.txt ../exp_data/train
cp phones.txt ../exp_data/test
cp phones.txt ../exp_data/dev
#python -W ignore eliminate_low_count_events.py $HOME/$exp_name
#cp phones.txt ../exp_data/train
#cp phones.txt ../exp_data/test
#cp phones.txt ../exp_data/dev

