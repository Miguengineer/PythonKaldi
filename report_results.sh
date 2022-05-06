#!/bin/bash
. ./path.sh
decode_train=false
exp_name=HMM-GMM-Beta
python_code_dir='/home/miguel/HMM-GMM-Beta/pythonSrc'
test_datadir=exp_data/test
train_datadir=exp_data/train
tra_files=('1.tra' '2.tra' '3.tra' '4.tra' '5.tra' '6.tra' '7.tra' '8.tra' '9.tra' '10.tra' '11.tra' '12.tra' '13.tra' '14.tra' '15.tra' '16.tra' '17.tra' '18.tra' '19.tra' '20.tra')
hyp_files=('hyp_1.tra.txt' 'hyp_2.tra.txt' 'hyp_3.tra.txt' 'hyp_4.tra.txt' 'hyp_5.tra.txt' 'hyp_6.tra.txt' 'hyp_7.tra.txt' 'hyp_8.tra.txt' 'hyp_9.tra.txt' 'hyp_10.tra.txt' 'hyp_11.tra.txt' 'hyp_12.tra.txt' 'hyp_13.tra.txt' 'hyp_14.tra.txt' 'hyp_15.tra.txt' 'hyp_16.tra.txt' 'hyp_17.tra.txt' 'hyp_18.tra.txt' 'hyp_19.tra.txt' 'hyp_20.tra.txt')
ref_file='ref.txt'
echo "Removing directory results ..."
rm -r results
echo "Creating directory results ..."
mkdir -p results/mono/
mkdir -p results/tri/
mkdir -p results/mono_train
mkdir -p results/tri_train
for tra in "${tra_files[@]}"
do
  # -f 2- is to avoid converting utt id to integer
  if $decode_train; then
  	utils/int2sym.pl -f 2- exp/mono/graph/words.txt exp/mono/decode_train/scoring/$tra > results/mono_train/hyp_$tra.txt
  	utils/int2sym.pl -f 2- exp/tri1/graph/words.txt exp/tri1/decode_train/scoring/$tra > results/tri_train/hyp_$tra.txt
  fi
	utils/int2sym.pl -f 2- exp/mono/graph/words.txt exp/mono/decode_test/scoring/$tra > results/mono/hyp_$tra.txt
	utils/int2sym.pl -f 2- exp/tri1/graph/words.txt exp/tri1/decode_test/scoring/$tra > results/tri/hyp_$tra.txt
done
# Copy reference to each system report 
cp exp/mono/decode_test/scoring/test_filt.txt results/mono/ref.txt
cp exp/tri1/decode_test/scoring/test_filt.txt results/tri/ref.txt
if $decode_train; then
	cp exp/mono/decode_train/scoring/test_filt.txt results/mono_train/ref.txt
	cp exp/tri1/decode_train/scoring/test_filt.txt results/tri_train/ref.txt
fi

echo "Reporting MONO results ..."
cp $test_datadir/wav.scp results/mono/
cp $test_datadir/wav.scp results/tri/
if $decode_train; then
	cp $train_datadir/wav.scp results/tri_train
	cp $train_datadir/wav.scp results/mono_train
fi


cp $python_code_dir/preprocess_wer.py results/mono/
cp $python_code_dir/utils.py results/mono/utils.py
cp $python_code_dir/best_wer.py results/mono/best_wer.py
cp $python_code_dir/preprocess_wer.py results/tri/
cp $python_code_dir/report_general_results.py results/mono
cp $python_code_dir/report_general_results.py results/tri
cp $python_code_dir/utils.py results/tri/utils.py
cp $python_code_dir/best_wer.py results/tri/best_wer.py

if $decode_train; then
	cp $python_code_dir/preprocess_wer.py results/mono_train/
	cp $python_code_dir/utils.py results/mono_train/
	cp $python_code_dir/best_wer.py results/mono_train
	cp $python_code_dir/report_general_results.py results/mono_train
	cp $python_code_dir/preprocess_wer.py results/tri_train/
	cp $python_code_dir/utils.py results/tri_train/
	cp $python_code_dir/best_wer.py results/tri_train
	cp $python_code_dir/report_general_results.py results/tri_train
fi


echo "Computing WER and minimum-cost alignments ..."
cd results/mono/
## Preprocess transcriptions. Basically removes all SIL 'Events'
python preprocess_wer.py

mkdir alignments
# Compute WER and optimal alignments considering cleaned transcriptions (without SIL)
for hyp in "${hyp_files[@]}"
do
	compute-wer --text --mode=present ark:$ref_file ark:$hyp >& wer_$hyp
	align-text ark:$ref_file ark:$hyp ark,t:alignments/ali_$hyp
done
# From all WERs computed by Kaldi, pick the one with lowest WER
python best_wer.py
# Compute multi-class metrics. It also applies an SNR filter and evaluates the results.
python -W ignore report_general_results.py test

if $decode_train; then
	cd $HOME/$exp_name/results/mono_train/
	## Preprocess transcriptions. Basically removes all SIL 'Events'
	python preprocess_wer.py
	mkdir alignments
	# Compute WER and optimal alignments considering cleaned transcriptions (without SIL)
	for hyp in "${hyp_files[@]}"
	do
		compute-wer --text --mode=present ark:$ref_file ark:$hyp >& wer_$hyp
		align-text ark:$ref_file ark:$hyp ark,t:alignments/ali_$hyp
	done
	# From all WERs computed by Kaldi, pick the one with lowest WER
	python best_wer.py
	# Compute multi-class metrics. It also applies an SNR filter and evaluates the results.
	python -W ignore report_general_results.py train
fi


##### Tri1
cd $HOME/$exp_name/results/tri/
### Preprocess transcriptions. Basically removes all SIL 'Events'
python preprocess_wer.py
mkdir alignments
# Compute WER and optimal alignments considering cleaned transcriptions (without SIL)
for hyp in "${hyp_files[@]}"
do
	compute-wer --text --mode=present ark:$ref_file ark:$hyp >& wer_$hyp
	align-text ark:$ref_file ark:$hyp ark,t:alignments/ali_$hyp
done
# From all WERs computed by Kaldi, pick the one with lowest WER
python best_wer.py
python -W ignore report_general_results.py test
if $decode_train; then
	cd $HOME/$exp_name/results/tri_train
	python preprocess_wer.py
	mkdir alignments
	# Compute WER and optimal alignments considering cleaned transcriptions (without SIL)
	for hyp in "${hyp_files[@]}"
	do
		compute-wer --text --mode=present ark:$ref_file ark:$hyp >& wer_$hyp
		align-text ark:$ref_file ark:$hyp ark,t:alignments/ali_$hyp
	done
	# From all WERs computed by Kaldi, pick the one with lowest WER
	python best_wer.py
	python -W ignore report_general_results.py train
fi


