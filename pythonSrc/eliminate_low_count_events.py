from preprocessing_tools import write_text, write_phones, \
    make_wav, make_lexicon, make_spk2gender, make_utt2spk, make_text_txt, make_silence_phones, make_words, make_spk2utt
from split_dataset_tools import train_test_dev_split
from preprocessing_tools import compute_events_statistics
from utils import load_data
import pickle


def eliminate_low_count_events(statistics, data, threshold=30):
    # Figure out what events should be eliminated
    events_to_eliminate = []
    for event in statistics.keys():
        if statistics[event] < threshold:
            events_to_eliminate.append(event)

    print("Threshold has been set to a minimum of " + str(threshold) + " events")
    print("The utterances containing one of the following events will be eliminated : ")
    for event in events_to_eliminate:
        print(event)
    new_data = {}
    new_key_idx = 1
    for utt_key in data.keys():
        current_data = data[utt_key]
        events = current_data['events']
        test_list = [test_event for test_event in events_to_eliminate if test_event in events]
        if len(test_list) == 0:
            new_data[new_key_idx] = current_data
            new_key_idx += 1
    return new_data


_, _, _, all_data = load_data('/home/miguel/HMM-GMM-Beta/data')
stats = compute_events_statistics(all_data)
new_data = eliminate_low_count_events(stats, all_data)

train_idxs, test_idxs = train_test_dev_split(all_data, test_per=40)
# Sort all data
train_idxs = sorted(train_idxs)
train_data = {}
test_data = {}
for key in train_idxs:
    train_data[key] = all_data[key]
for key in test_idxs:
    test_data[key] = all_data[key]
test_idxs, dev_idxs = train_test_dev_split(test_data, test_per=50)
test_idxs = sorted(test_idxs)
dev_idxs = sorted(dev_idxs)
test_data = {}
dev_data = {}
for key in test_idxs:
    test_data[key] = all_data[key]
for key in dev_idxs:
    dev_data[key] = all_data[key]

print("Done preprocessing data. Making Kaldi needed files... ")
write_phones(new_data)
write_text(new_data, path='/home/miguel/HMM-GMM-Beta/data')
make_spk2utt(train_data, path='/home/miguel/HMM-GMM-Beta/exp_data/train')
make_utt2spk(train_data, path='/home/miguel/HMM-GMM-Beta/exp_data/train')
make_spk2gender(train_data, path='/home/miguel/HMM-GMM-Beta/exp_data/train')
make_wav(train_data, path='/home/miguel/HMM-GMM-Beta/exp_data/train')
write_text(train_data, path='/home/miguel/HMM-GMM-Beta/exp_data/train')
make_spk2utt(test_data, path='/home/miguel/HMM-GMM-Beta/exp_data/test')
make_utt2spk(test_data, path='/home/miguel/HMM-GMM-Beta/exp_data/test')
make_spk2gender(test_data, path='/home/miguel/HMM-GMM-Beta/exp_data/test')
make_wav(test_data, path='/home/miguel/HMM-GMM-Beta/exp_data/test')
write_text(test_data, path='/home/miguel/HMM-GMM-Beta/exp_data/test')
make_spk2utt(dev_data, path='/home/miguel/HMM-GMM-Beta/exp_data/dev')
make_utt2spk(dev_data, path='/home/miguel/HMM-GMM-Beta/exp_data/dev')
make_spk2gender(dev_data, path='/home/miguel/HMM-GMM-Beta/exp_data/dev')
make_wav(dev_data, path='/home/miguel/HMM-GMM-Beta/exp_data/dev')
write_text(dev_data, path='/home/miguel/HMM-GMM-Beta/exp_data/dev')
make_text_txt(new_data, '/home/miguel/HMM-GMM-Beta/data')
make_words(new_data, '/home/miguel/HMM-GMM-Beta/data')
make_silence_phones(new_data, '/home/miguel/HMM-GMM-Beta/data')
make_lexicon(new_data, '/home/miguel/HMM-GMM-Beta/data')
print("Saving data as pickle objects ...")

with open('train_data.pkl', 'wb') as f:
    pickle.dump(train_data, f)
with open('test_data.pkl', 'wb') as f:
    pickle.dump(test_data, f)
with open('dev_data.pkl', 'wb') as f:
    pickle.dump(dev_data, f)
with open('all_data.pkl', 'wb') as f:
    pickle.dump(new_data, f)

print("Done!")
