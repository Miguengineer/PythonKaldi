def get_annotations(path):
    """
    Obtain annotations from .xlsx files. Excel file is expected to have columns Begin Time (s), End Time (s), Signal ID,
    and SNR(dB). Function reads all these columns and puts them in a dictionary, with keys begin, end, label, and snr.
    Each key holds a list with all the values read from the excel
    :param path: path where the .xlsx file exists
    :return: dictionary whose keys contain the main information for each annotation
    """
    import pandas as pd
    import os
    files = [f for f in os.listdir(path) if
             os.path.isfile(os.path.join(path, f))]
    begin_times = []
    end_times = []
    labels = []
    snrs = []
    for file in files:
        # Get only the extension to check if is an excel file
        if os.path.splitext(file)[1] == '.xlsx':
            annotations = pd.read_excel(os.path.join(path, file))
            begin_times = annotations["Begin Time (s)"].values
            end_times = annotations["End Time (s)"].values
            labels = annotations["Signal ID"].values
            snrs = annotations["SNR(dB)"].values
        elif os.path.splitext(file)[1] == '.csv':
            annotations = pd.read_csv(os.path.join(path, file), skip_blank_lines=True)
            begin_times = annotations["Begin Time (s)"].values
            end_times = annotations["End Time (s)"].values
            labels = annotations["Signal ID"].values
            snrs = annotations["SNR(dB)"].values
    annotations = {'begin': begin_times, 'end': end_times, 'label': labels, 'snr': snrs}
    return annotations


def check_disjoint(idx1, idx2):
    return len(set(idx1) & set(idx2)) == 0


def load_data(path):
    import pickle, os
    from Frame import Frame, Utterance
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
    
def get_utt_idxs():
    utt_idx = []
    f_wav = open('wav.scp')
    wav_lines = f_wav.readlines()
    for line in wav_lines:
        utt_idx.append(line[0:5])
    return utt_idx


def write_text(utt_idxs, events, filename):
    f = open(filename, 'w')
    for utt_idx in range(len(events)):
        current_events = events[utt_idx]
        # Write current utt idx
        f.write(utt_idxs[utt_idx])
        f.write(" ")
        # Write events
        for event_idx in range(len(current_events)):
            event = current_events[event_idx]
            if event_idx == len(current_events) - 1:
                f.write(event)
            else:
                f.write(event)
                f.write(" ")
        f.write("\n")
    
    
def modify_annotations(original_annotations, new_annotations_dict=None):
    if new_annotations_dict is None:
        new_annotations_dict = {
        "S1.1": "SEP",
        "S1.2": "S12",
        "S1.3": "S13",
        "S2.1": "S21",
        "S2.2": "S22",
        "S2.3": "S23",
        "S2.4": "S23",
        "AA.1": "AA",
        "AA.2": "AA",
        "AA.3": "AA",
        "FW.S": "FWS",
        "FW.D": "FWD",
        "FW.D2": "FWD2",
        "FW.D3": "FWD3",
        "FW.D4": "FWD3",
        "SW.D": "SWD",
        "SW.U": "SWU",
        "UND-G": "UND",
        "U.W": "UW",
        "A.N": "AN",
        "U.AN": "UAN",
        "AG.P": "AGP",
        "UND.B": "UNDB",
    }
    labels = original_annotations['label']
    original_begin_times = original_annotations['begin']
    original_end_times = original_annotations['end']
    original_snrs = original_annotations['snr']
    new_begins = []
    new_ends = []
    new_labels = []
    new_snrs = []
    for annotation_idx in range(len(original_begin_times)):
        current_annotation = labels[annotation_idx]
        if current_annotation in new_annotations_dict.keys():
            current_annotation = new_annotations_dict[current_annotation]
        new_begins.append(original_begin_times[annotation_idx])
        new_ends.append(original_end_times[annotation_idx])
        new_labels.append(current_annotation)
        new_snrs.append(original_snrs[annotation_idx])
    new_annotations = {'begin': new_begins, 'end': new_ends, 'label': new_labels, 'snr': new_snrs}
    return new_annotations


def join_dictionaries(all_dicts):
    """
    Join in a single dictionary a dictionary of events
    :param all_dicts: Dictionary of dictionaries
    :return: A single dictionary containing all the training examples
    """
    all_utts = {}
    utt_idx = 1
    for db_key in all_dicts.keys():
        for train_idx in all_dicts[db_key].keys():
            all_utts[utt_idx] = all_dicts[db_key][train_idx]
            utt_idx += 1
    return all_utts