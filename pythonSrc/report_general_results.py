import sys


def get_ali_pairs(path=''):
    import os
    alignments = []
    for f_idx in range(1, 21):
        f = open(os.path.join(path, 'ali_hyp_' + str(f_idx) + '.tra.txt'))
        f_lines = f.readlines()
        temp_alignments = []
        for line in f_lines:
            # Ignore utt idx
            events_ali = line[6:-1]
            # Kaldi Events are separated by a semicolon in the alignment
            ali_pairs = events_ali.split(" ; ")
            if len(ali_pairs) == 1:
                split_events = ali_pairs[0].split(" ")
                temp_alignments.append([(split_events[0], split_events[1])])
            else:
                temp_pairs = []
                for pair in ali_pairs:
                    split_events = pair.split(" ")
                    temp_pairs.append((split_events[0], split_events[1]))
                temp_alignments.append(temp_pairs)
        alignments.append(temp_alignments)
    return alignments


def compute_accuracy(ali):
    num_events = 0
    hits = 0
    errors = 0
    # For each utterance
    for utt_idx in range(len(ali)):
        alis = ali[utt_idx]
        for ali_pair in alis:
            ref = ali_pair[0]
            hyp = ali_pair[1]
            # Only process actual ref events for accuracy
            if ref != "<eps>":
                num_events = num_events + 1
                # Check match
                if ref == hyp:
                    hits = hits + 1
                else:
                    errors = errors + 1
    return hits / num_events * 100


def generate_report(ali, filename='results.csv'):
    from sklearn.metrics import classification_report
    import pandas
    y = []
    y_hat = []
    for utt_idx in range(len(ali)):
        alis = ali[utt_idx]
        for ali_pair in alis:
            ref = ali_pair[0]
            hyp = ali_pair[1]
            y.append(ref)
            y_hat.append(hyp)
    report = classification_report(y, y_hat, output_dict=True)
    df = pandas.DataFrame(report).transpose()
    df.to_csv(filename, index=True)


def load_data(path):
    import pickle, os
    train_data_path = os.path.join(path, "train_data.pkl")
    test_data_path = os.path.join(path, "test_data.pkl")
    dev_data_path = os.path.join(path, "dev_data.pkl")
    all_data_path = os.path.join(path, "all_data.pkl")
    with open(train_data_path, 'rb') as f:
        train_data = pickle.load(f)
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    with open(dev_data_path, 'rb') as f:
        dev_data = pickle.load(f)
    with open(all_data_path, 'rb') as f:
        all_data = pickle.load(f)
    return train_data, test_data, dev_data, all_data

def snr_per_event(data):
    snr_per_event_per_utt = {}
    for utt_idx in data.keys():
        snr_per_frame  = data[utt_idx]['snrs']
        alis = data[utt_idx]['alignments']
        snr_per_event = [snr_per_frame[i] for i, v in enumerate(alis) if (i == 0 and v != 'SIL')
                 or (v != alis[i - 1] and v != 'SIL')]
        # Clean (remove SILs)
        snr_per_event = [e for e in snr_per_event if e != 0]
        current_events = data[utt_idx]['events']
        current_events = [e for e in current_events if e != "SIL"]
        snr_per_event_per_utt[utt_idx] = list(zip(current_events, snr_per_event))
    return snr_per_event_per_utt


def compute_accuracy_snr(ali, snr_events, SNR_TRESHOLD=-1000):
    event_count = 0
    hits = 0
    # SNR events to just list of lists
    snr_per_event_l = []
    for utt_key in snr_events.keys():
        current_snr = snr_events[utt_key]
        aux = []
        for event, snr in current_snr:
            aux.append(snr)
        snr_per_event_l.append(aux)

    for utt_idx in range(len(ali)):
        current_ali = ali[utt_idx]
        pair_count = 0
        for ali_pair in current_ali:
            ref = ali_pair[0]
            hyp = ali_pair[1]
            if ref != "<eps>":
                ref_snr = snr_per_event_l[utt_idx][pair_count]
                pair_count += 1
                # Count only if threshold is met
                if ref_snr >= SNR_TRESHOLD:
                    event_count += 1
                    if ref == hyp:
                        hits += 1

    return hits / event_count * 100, event_count


def compute_hits_per_class_snr(ali, snr_events, SNR_TRESHOLD=-10):
    # SNR events to just list of lists
    snr_per_event_l = []
    for utt_key in snr_events.keys():
        current_snr = snr_events[utt_key]
        aux = []
        for event, snr in current_snr:
            aux.append(snr)
        snr_per_event_l.append(aux)
    # Each key has a list with (count, hits, false negatives)
    class_dict = {}
    for utt_idx in range(len(ali)):
        alis = ali[utt_idx]
        pair_count = 0
        for ali_pair in alis:
            ref = ali_pair[0]
            hyp = ali_pair[1]
            # Process only reference events
            if ref != "<eps>":
                ref_snr = snr_per_event_l[utt_idx][pair_count]
                pair_count += 1
                # Check if current ref event meets threshold and process
                if ref_snr >= SNR_TRESHOLD:
                    # Initialize
                    if not ref in class_dict:
                        class_dict[ref] = [0, 0, 0]
                    if not hyp in class_dict:
                        class_dict[hyp] = [0, 0, 0]
                    # Update count
                    class_dict[ref][0] += 1
                    # Hit, true positive
                    if ref == hyp:
                        class_dict[ref][1] += 1
                    # No hit means false negative for ref
                    else:
                        # Update false negative
                        class_dict[ref][2] += 1
    # Compute statistics
    statistics = {}
    for key in class_dict:
        total = class_dict[key][0]
        tp = class_dict[key][1]
        fn = class_dict[key][2]
        if tp + fn == 0:
            recall = 0
        else:
            recall = round(tp / (tp + fn) * 100, 2)
        statistics[key] = (recall, fn, total)
    return statistics


ali = get_ali_pairs(path='alignments')
max_acc = -1
best_idx = 0
for ali_idx in range(len(ali)):
    acc = compute_accuracy(ali[ali_idx])
    if acc > max_acc:
        max_acc = acc
        best_idx = ali_idx
print("The best accuracy is: " + "{:.2f}".format(max_acc) + "%")
print("The best accuracy occured at idx: " + str(best_idx + 1))
print("Generating report of per-class statistics ...")
print("Forced best_idx based on WER. Best idx is now 8")
best_idx = 8
generate_report(ali[best_idx])
f = open('max_acc.txt', 'w')
f.write("Acc: " + str(max_acc))
f.write("\n")
f.write("Idx: " + str(best_idx + 1))
f.close()
print("Done!")


train_data, test_data, dev_data, all_data = load_data('/home/miguel/HMM-GMM-Beta/data')
ali = get_ali_pairs(path='alignments')
data_to_use = sys.argv[1]
if data_to_use == 'train':
    snr_per_utt = snr_per_event(train_data)
elif data_to_use == 'test':
    snr_per_utt = snr_per_event(test_data)
elif data_to_use == 'dev':
    snr_per_utt = snr_per_event(dev_data)


snr_list_th = [-1000, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
num_events = []
accs = []
for snr_th in snr_list_th:
    acc, n_events = compute_accuracy_snr(ali[best_idx], snr_per_utt, snr_th)
    accs.append(acc)
    num_events.append(n_events)
f = open('num_events.txt', 'w')
for n in num_events:
    f.write(str(n))
    f.write("\n")
f.close()

import matplotlib.pyplot as plt
import numpy as np
num_events = np.array(num_events)
snr_list = np.arange(0, 21)
plt.figure(figsize=(10, 7))
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
plt1 = ax1.plot(snr_list, accs[1:], '-b', marker='o', label='Accuracy [%]')
plt2 = ax2.plot(snr_list, num_events[1:] / num_events[1], '-r', marker='s', label='Events Analyzed [%]')
plt.title('Accuracy v/s SNR threshold')
plt.ylabel('Accuracy [%]')
lns = plt1 + plt2
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper center')
ax1.set_xlabel('SNR Treshold [dB]')
ax1.set_ylabel('Accuracy [%]', color='b')
ax2.set_ylabel('Events Analyzed [%]', color='r')

plt.savefig('accuracy_vs_snr.jpg', bbox_inches='tight')
plt.clf()


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

labels = ["ERQ", "FWS", "S23", "AA", "SHIP", "FWD"]
stats_per_class = {}
snr_l = np.arange(0, 21)
print("Computing statistics per class. Only considering the following classes: ")
for l in labels:
    print(l)
for snr_th in snr_l:
    d = compute_hits_per_class_snr(ali[0], snr_per_utt, snr_th)
    for label in labels:
        if label not in d.keys():
            stats_per_class[label]['count'].append(0)
            stats_per_class[label]['fn'].append(0)
            stats_per_class[label]['recall'].append(0)
        else:
            if label in stats_per_class.keys():
                stats_per_class[label]['count'].append(d[label][2])
                stats_per_class[label]['fn'].append(d[label][1])
                stats_per_class[label]['recall'].append(d[label][0])
            else:
                stats_per_class[label] = {'count': [d[label][2]], 'fn': [d[label][1]], 'recall': [d[label][0]]}

df = pd.DataFrame({'SNR values': snr_l, 'ERQ Recall': stats_per_class['ERQ']['recall'],
                   'ERQ Counts': stats_per_class['ERQ']['count'], 'S23 Recall': stats_per_class['S23']['recall'],
                   'S23 Counts': stats_per_class['S23']['count'], 'FWS Recall': stats_per_class['FWS']['recall'],
                   'FWS Counts': stats_per_class['FWS']['count'],
                   'AA Recall': stats_per_class['AA']['recall'], 'AA Counts': stats_per_class['AA']['count'],
                   'SHIP Recall': stats_per_class['SHIP']['recall'], 'SHIP Counts': stats_per_class['SHIP']['count'],
                   'FWD Recalls': stats_per_class['FWD']['recall'], 'FWD Counts': stats_per_class['FWD']['count'],
                   'ACCS': accs[1:]})
df.to_csv('results_snr_filter.csv')

plt.figure(figsize=(10, 7))
for l in labels:
    label_recall = stats_per_class[l]['recall']
    counts = np.array(stats_per_class[l]['count'])
    counts_per = counts / counts[0] * 100.0
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    plt1 = ax1.plot(snr_l, label_recall, '-b', marker='o', label=l + ' Recall')
    plt2 = ax2.plot(snr_l, counts_per, '-r', marker='s', label='Events Analyzed [%]')
    lns = plt1 + plt2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='upper center')
    plot_title = l + ' Recall v/s SNR Treshold'
    ax1.set_xlabel('SNR Treshold [dB]')
    ax1.set_ylabel(l + ' recall', color='b')
    ax2.set_ylabel('Events Analyzed [%]', color='r')
    plt.title(plot_title)
    plt.savefig(l + '_recall_vs_snr.jpg')
    plt.clf()
print("Done!")
