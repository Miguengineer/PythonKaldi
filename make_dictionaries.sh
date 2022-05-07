#!/bin/bash
. ./cmd.sh 
. ./path.sh
export PATH=$PATH:/home/miguel/CMU-Cam_Toolkit_v2/bin
exp_dir=$HOME/HMM-GMM-Base
lang_dir=$exp_dir/lang_dir
dict_plain=$exp_dir/lang_dir/init_plain
lang_files_dir=$exp_dir/data

echo "Creating language model ..."
rm -rf $lang_dir
mkdir $lang_dir
rm -rf $dict_plain
mkdir $dict_plain
cp $lang_files_dir/text.txt $dict_plain/text.txt
cp $lang_files_dir/text $dict_plain/text
cd $dict_plain
# output for debugging purposes 
text2wfreq < text.txt > textfreq.txt
text2wfreq < text.txt | (wfreq2vocab) > text.vocab > text.vocab.txt
text2wfreq < text.txt | wfreq2vocab > text.vocab
# Combinations of trigrams
cat text.txt | text2idngram -vocab text.vocab -temp ./ > text.idngram
cat text.txt | text2idngram -vocab text.vocab -write_ascii -temp ./ > text.idngram.txt
idngram2lm -vocab_type 0 -idngram text.idngram -vocab text.vocab -arpa text.arpa
gzip text.arpa

cd $lang_dir

language_model_dir=lm
language_model_tmp=lm_tmp
dict_init=dictionaries
rm -rf $dict_init
mkdir $dict_init
rm -rf $language_model_dir
mkdir $language_model_dir
# Check if phones.txt and words.txt exist
[ ! -f $lang_files_dir/phones.txt ] && echo "Expected phones.txt to exist" && exit 1;
[ ! -f $lang_files_dir/words.txt ] && echo "Expected words.txt to exist" && exit 1;
cp $lang_files_dir/phones.txt $language_model_dir/phones.txt
cp $lang_files_dir/words.txt $language_model_dir/words.txt


# Require files to exist
[ ! -f $lang_files_dir/lexicon.txt ] && echo "Expected lexicon.txt to exist" && exit 1;
[ ! -f $lang_files_dir/silence_phones.txt ] && echo "Expected silence_phones.txt to exist" && exit 1;
[ ! -f $lang_files_dir/nonsilence_phones.txt ] && echo "Expected nonsilence_phones.txt to exist" && exit 1;
[ ! -f $lang_files_dir/optional_silence.txt ] && echo "Expected optional_silence.txt to exist" && exit 1;
cp $lang_files_dir/lexicon.txt $dict_init/lexicon.txt
cp $lang_files_dir/silence_phones.txt $dict_init/silence_phones.txt
cp $lang_files_dir/nonsilence_phones.txt $dict_init/nonsilence_phones.txt
cp $lang_files_dir/optional_silence.txt $dict_init/optional_silence.txt
cd $exp_dir
utils/prepare_lang.sh --num-sil-states 3 --num-nonsil-states 3 --position-dependent-phones false --sil-prob 0.5 $lang_dir/$dict_init "UND" $lang_dir/$language_model_tmp $lang_dir/$language_model_dir
# Custom topo
#cp topo $lang_dir/$language_model_dir

gunzip -c $dict_plain/text.arpa.gz | utils/find_arpa_oovs.pl $lang_dir/$language_model_dir/words.txt  > $lang_dir/$language_model_tmp/oovs.txt
# grep -v '<s> <s>' because the LM seems to have some strange and useless
# stuff in it with multiple <s>'s in the history.  Encountered some other similar
# things in a LM from Geoff.  Removing all "illegal" combinations of <s> and </s>,
# which are supposed to occur only at being/end of utt.  These can cause 
# determinization failures of CLG [ends up being epsilon cycles].
gunzip -c $dict_plain/text.arpa.gz | \
	               grep -v '<s> <s>' | \
	               grep -v '</s> <s>' | \
	               grep -v '</s> </s>' | \
	               arpa2fst - | fstprint | \
	               utils/remove_oovs.pl $lang_dir/$language_model_tmp/oovs.txt | \
	               utils/eps2disambig.pl | utils/s2eps.pl | fstcompile --isymbols=$lang_dir/$language_model_dir/words.txt \
	               --osymbols=$lang_dir/$language_model_dir/words.txt  --keep_isymbols=false --keep_osymbols=false | \
	    				   fstrmepsilon > $lang_dir/$language_model_dir/G.fst
	  fstisstochastic $lang_dir/$language_model_dir/G.fst
	  fstdraw --isymbols=$lang_dir/$language_model_dir/words.txt --osymbols=$lang_dir/$language_model_dir/words.txt -portrait $lang_dir/$language_model_dir/G.fst $lang_dir/$language_model_dir/G.dot
	echo "Succeeded in formatting data."



