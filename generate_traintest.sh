#!/bin/bash
matlab_dir=matlab_src/SplitDataset
# Assuming directory ALIPHO with all the required files are already there, security check anyway
[ ! -f ALIPHO/ALI_PHO.mat ] && echo "File ALI_PHO.mat doesn't exist!" && exit 1;
cp $matlab_dir/split_train.m ALIPHO
cp $matlab_dir/splitDataset.m ALIPHO
cp $matlab_dir/generate2.m ALIPHO
cp $matlab_dir/crossover.m ALIPHO
cp $matlab_dir/epoque.m ALIPHO
cp $matlab_dir/fitness.m ALIPHO
cp $matlab_dir/getTrainExamples.m ALIPHO
cp $matlab_dir/getPhoneCounts.m ALIPHO
cp $matlab_dir/mutation.m ALIPHO
cp $matlab_dir/tournement.m ALIPHO
cp $matlab_dir/removeRows.m ALIPHO
cp $matlab_dir/split_test.m ALIPHO
cp $matlab_dir/splitDatasetDev.m ALIPHO

rm -r ALIPHO/train
rm -r ALIPHO/test
rm -r ALIPHO/dev
mkdir ALIPHO/train
mkdir ALIPHO/test
mkdir ALIPHO/dev

cd ALIPHO
matlab -nojvm -nodisplay -nosplash -r split_train
cp ALI_PHO.mat train
cp ALI_PHO.mat test
cp removeRows.m train
cp removeRows.m test
cp removeRows.m dev
cp wav.scp train
cp text train
cp utt2spk train
cp spk2utt train
cp spk2gender train
cp wav.scp test
cp text test
cp utt2spk test
cp spk2utt test
cp spk2gender test
matlab -nojvm -nodisplay -nosplash -r splitDataset

cp best.mat test
cp split_test.m test
cp generate2.m test
cp splitDataset.m test
cp splitDatasetDev.m test
cp epoque.m test
cp crossover.m test
cp fitness.m test
cp getPhoneCounts.m test
cp tournement.m test
cp removeRows.m test
cp getTrainExamples.m test
cp mutation.m test

cd test
matlab -nojvm -nodisplay -nosplash -r split_test
cp ALI_PHO.mat ../dev
cp wav.scp ../dev
cp text ../dev
cp utt2spk ../dev
cp spk2utt ../dev
cp spk2gender ../dev
matlab -nojvm -nodisplay -nosplash -r splitDatasetDev
