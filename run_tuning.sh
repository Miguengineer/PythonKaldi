#!/bin/bash
. ./path.sh

# Language model directory
lang_dir=/home/miguel/HMM-GMM-Beta/lang_dir/lm
# Train data
exp_name=HMM-GMM-Beta
datadir=exp_data
matlab_code_dir=matlab_src
extract_features=false
compute_gmm=false
decode=true
use_gmm=false
nj=8
if $extract_features; then
	echo "Extracting features for" $datadir/train "directory"
	cp $matlab_code_dir/feature_extraction.m $datadir/train
	cp $matlab_code_dir/extract_features.m $datadir/train
	cp $matlab_code_dir/trifbank.m $datadir/train
	cp $matlab_code_dir/writekaldifeatures.m $datadir/train
	cp $matlab_code_dir/copy-feats $datadir/train
	cp $matlab_code_dir/mvn_per_utt.m $datadir/train
	cd $datadir/train
	matlab -nojvm -nosplash -nodisplay -r feature_extraction
	matlab -nojvm -nosplash -nodisplay -r mvn_per_utt
	cd /home/miguel/$exp_name
	echo "Done!"
	echo "Extracting features for" $datadir/test "directory"
	cp $matlab_code_dir/feature_extraction.m $datadir/test
	cp $matlab_code_dir/extract_features.m $datadir/test
	cp $matlab_code_dir/trifbank.m $datadir/test
	cp $matlab_code_dir/writekaldifeatures.m $datadir/test
	cp $matlab_code_dir/copy-feats $datadir/test
	cp $matlab_code_dir/mvn_per_utt.m $datadir/test
	cd $datadir/test
	matlab -nojvm -nosplash -nodisplay -r feature_extraction
	matlab -nojvm -nosplash -nodisplay -r mvn_per_utt
	cd /home/miguel/$exp_name
	echo "Done! "
	echo "Extracting features for" $datadir/dev "directory"
	cp $matlab_code_dir/feature_extraction.m $datadir/dev
	cp $matlab_code_dir/extract_features.m $datadir/dev
	cp $matlab_code_dir/trifbank.m $datadir/dev
	cp $matlab_code_dir/writekaldifeatures.m $datadir/dev
	cp $matlab_code_dir/copy-feats $datadir/dev
	cp $matlab_code_dir/mvn_per_utt.m $datadir/dev
	cd $datadir/dev
	matlab -nojvm -nosplash -nodisplay -r feature_extraction
	matlab -nojvm -nosplash -nodisplay -r mvn_per_utt
	cd /home/miguel/$exp_name
	echo "Done!"
fi

stage=1
if [ $stage -le 1 ]; then
	dir=exp/mono
	rm -rf $dir
	mkdir -p $dir
	if $use_gmm; then
		steps/train_mono_custom_gmm.sh --norm-vars true --boost-silence 1.7 --nj 6 --cmd run.pl \
					exp_data/train $lang_dir exp/mono_train exp_data/train/RAW.gmm || exit 1;
	else
		steps/train_mono.sh --norm-vars true --boost-silence 2 --nj 8 --cmd run.pl \
					${datadir}/train $lang_dir $dir || exit 1;
	fi
	# Copy GMM model to .txt for debugging purposes
	gmm-copy --binary=false $dir/0.mdl $dir/0.mdl.txt
	gmm-copy --binary=false $dir/final.mdl $dir/final.mdl.txt
	if $decode; then
		utils/mkgraph.sh $lang_dir $dir $dir/graph || exit 1;
		# Decode test
		steps/decode.sh --nj 6 \
		$dir/graph $datadir/dev $dir/decode_test
		steps/get_ctm.sh --frame-shift 1 $datadir/dev $lang_dir $dir/decode_test 
		# Show info about the final model
		gmm-info $dir/final.mdl
	fi
fi

#if [ $stage -le 2 ]; then
#	dir=exp/tri1
#	rm -r $dir
#	steps/align_si.sh --boost-silence 1.5 --nj 6 --cmd run.pl \
#		$datadir/train $lang_dir exp/mono exp/mono_ali
#		
#	steps/train_deltas.sh --boost-silence 1.5 --cmd run.pl 500 5000 \
#		$datadir/train $lang_dir exp/mono_ali exp/tri1
#		
#	utils/mkgraph.sh $lang_dir exp/tri1 exp/tri1/graph
#	steps/decode.sh --nj 6 --cmd run.pl exp/tri1/graph \
#		$datadir/dev exp/tri1/decode_test
#		
#	steps/get_ctm.sh --frame-shift 1 exp_data/dev $lang_dir exp/tri1/decode_test 
#fi





