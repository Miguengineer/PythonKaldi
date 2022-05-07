def check_all_silent(utterance):
    for frame in utterance.frames:
        if not frame.sil_frame:
            return False
    return True



def make_ali(annotations, audio, frame_size=0.512, overlap=0.5, modify_annotations=True):
    """
    Make a frame-to-frame alignment based on given annotations for audio. Divides the audio into overlapping frames and
    assign each frame a label.
    :param annotations: dictionary that contains annotations for given audio
    :param audio: audio from which annotations are made
    :param frame_size: frame size of each frame in seconds
    :param overlap: overlap (0 < overlap < 1)
    :param modify_annotations: if True, use default dictionary to modify annotations to a different format
    :return: frame-to-frame alignments for audio
    """
    import numpy as np
    from Frame import Frame
    from utils import modify_annotations
    # Sample rate
    fs = 250
    annotations = modify_annotations(annotations)
    # Retrieve relevant info for annotations
    begin_times = annotations['begin']
    end_times = annotations['end']
    labels = annotations['label']
    snrs = annotations['snr']
    audio_length_sec = audio.size / fs
    hop_size = frame_size * overlap
    # Safety check!
    if len(begin_times) != len(end_times) != len(labels) != len(snrs):
        print("Data has not the same number of elements. This is a serious error. Stopping ...")
        return
    # Frame length in samples
    num_frames = get_num_frames(audio_length_sec, frame_size, overlap)

    current_frames = [Frame() for _ in range(num_frames)]
    current_snr_l = [-100 for _ in range(num_frames)]
    for annotation_idx in range(len(begin_times)):
        current_annotation = labels[annotation_idx]
        current_bt = begin_times[annotation_idx]
        current_et = end_times[annotation_idx]
        current_snr = snrs[annotation_idx]
        # First frame the current annotation covers
        first_frame = int(np.floor(current_bt / hop_size))
        # Last frame the current annotation covers
        last_frame = int(np.floor(current_et / hop_size))
        # Re-assign some frames creating non-sil Frame objects
        for frame_idx in range(first_frame, last_frame + 1):
            # Check for overlapped frames
            if not current_frames[frame_idx].sil_frame and current_frames[frame_idx].label != current_annotation:
                previous_annotation_label = current_frames[frame_idx].label
                # Overlap already spotted
                if current_annotation not in previous_annotation_label:
                    overlapped_annotation = previous_annotation_label + current_annotation
                    current_frames[frame_idx] = Frame(current_snr, overlapped_annotation, sil_frame=False)
            else:
                current_frames[frame_idx] = Frame(current_snr, current_annotation, sil_frame=False)
    return current_frames, current_snr_l


def make_utterances(ali, frame_size, audio, audioname, audios_path, frames_per_utterance=600,
                    max_frames=1000, remove_sil=True):
    """
    Divide an alignment matrix in frames_per_utterance frames
    :param ali: alignments for audio
    :param snrs: snr annotations for frames
    :param frame_size: frame size in seconds
    :param audio: audio (to which the alignments belong)
    :param audioname: name of the units that will be created (utterances)
    :param audios_path: absolute path where to store the audio units
    :param frames_per_utterance: total frames that will contain
    :param max_frames: the utterances division are divided to a maximum of max_frames
    :param remove_sil: if True, remove utterances that contain only silence
    :return: list of utterances
    """
    import soundfile as sf
    import numpy as np
    import os
    from Frame import Utterance
    db_utterances = []
    aux_ali = ali.copy()
    initial_total_frames = len(aux_ali)
    units_idx = 0
    # Audio sample rate
    fs = 250
    units_dict = {}
    # While there are still frames to assign
    while len(aux_ali) > 0:
        # Extract first frames_per_utterance frames given length is at least frames_per_utterance
        if len(aux_ali) < frames_per_utterance:
            frames = aux_ali.copy()
        else:
            frames = aux_ali[0:frames_per_utterance]
        # Last frame annotation. We check it to make sure we are not splitting an event. Max. Thresh is max_frames
        last_frame_event = frames[-1].label
        frames_added = 0
        for i in range(frames_per_utterance, max_frames + 1):
            # Do not go beyond maximum number of frames available
            if i >= len(aux_ali):
                break
            if aux_ali[i].label == last_frame_event and aux_ali[i].label != "SIL":
                frames.append(aux_ali[i])
                frames_added += 1
            else:
                break
        # Update ali removing added frames
        aux_ali = aux_ali[frames_per_utterance + frames_added:]
        # Extract samples from audio based on number of frames
        num_frames = len(frames)
        samples_to_extract = int(np.ceil(num_frames / 2 * frame_size * fs))
        new_unit = audio[0:samples_to_extract]
        audio = audio[samples_to_extract:]
        unit_name = audioname + '_' + str(units_idx) + '.wav'
        alignments = []
        for frame in frames:
            alignments.append(frame.label)
        events = get_events_in_ali(alignments)
        new_utt = Utterance(frames, new_unit, unit_name, events)
        if remove_sil and not check_all_silent(new_utt):
            db_utterances.append(new_utt)
        assert len(new_unit) > 0, "Error! An unit with length 0 is being written. This is bad, some error occurred when" \
                                  "creating utterances"
        # Write new audio unit
        sf.write(os.path.join(audios_path, unit_name), new_unit, fs)
        units_dict[units_idx] = unit_name
        units_idx += 1
    print("Created " + str(len(db_utterances)) + " utterances from " + str(initial_total_frames) + " frames")
    return db_utterances


def join_utterances(data_per_db):
    """
    Join in a single database a list of utterances
    :param data_per_db: dictionary with utterances. Each key is subdatabase
    :return: all utterances joined in a single dictionary, where each key is a dummy-id-indexing. Id goes from 1 to num
    of utterances. Dictionary contains another dictionary with alignments, snrs, and name of audio unit
    """
    # All utterances are key-indexed
    all_data = {}
    utt_idx = 1
    for db_key in data_per_db.keys():
        for utt in data_per_db[db_key]:
            all_data[utt_idx] = utt
            utt_idx += 1
    return all_data


def get_num_frames(dur, frame_size, overlap=0.5):
    """
    Heuristic (and very poorly implemented) to compute the number of frames we should have, given duration,
    frame size, and overlap in samples.
    :param dur: duration in samples
    :param frame_size: frame size in samples
    :param overlap: overlap in range 0 < x < 1
    :return: number of frames
    """
    init_ptr = 0
    final_ptr = frame_size
    num_frames = 1
    while final_ptr <= dur:
        init_ptr += overlap * frame_size
        final_ptr = init_ptr + frame_size
        num_frames += 1
    if init_ptr < dur < final_ptr:
        num_frames += 1
    return num_frames




def get_events_in_ali(data):
    """
    Get the events present in a dictionary containing utterances. N consecutive frames of one phone is considered
    an event. For example, an alignment of five frames which looks like: [ERQ, ERQ, ERQ, SHIP, ERQ] would be represented
    by 3 events: [ERQ, SHIP ,ERQ]
    :param data: Dictionary containing utterances keyed by utterance id or key.
    :return: Same data structure, but with a new item in the dictionary ['events']
    """
    trans = [v for i, v in enumerate(data) if i == 0 or v != data[i - 1]]
    return trans


def get_phones(data):
    """
    Get the phones present in a list of utterances. In the project this code was written for, each phone is actually
    an event
    :param data: a dictionary keyed with utterance IDS. Each member of this dictionary MUST have the key ['events']
    which is a list of events of that utterance
    :return: list of all phones (events) present in a dictionary of utterances
    """
    phones = set()
    for utt_key in data:
        utt = data[utt_key]
        for event in utt.events:
            phones.add(event)
    return phones


def add_events(data):
    """
    Add the events present in a dictionary containing utterances. N consecutive frames of one phone is considered
    an event. For example, an alignment of five frames which looks like: [ERQ, ERQ, ERQ, SHIP, ERQ] would be represented
    by 3 events: [ERQ, SHIP ,ERQ]
    :param data: Dictionary containing utterances keyed by utterance id or key.
    :return: Same data structure, but with a new item in the dictionary ['events']
    """
    new_all_data = {}
    for utt_key in data.keys():
        utt_dict = data[utt_key]
        ali = utt_dict['alignments']
        trans = [v for i, v in enumerate(ali) if i == 0 or v != ali[i - 1]]
        utt_dict['events'] = trans
        new_all_data[utt_key] = utt_dict
    return new_all_data


def write_phones(data):
    """
    Write phones.txt file needed to create a Language Model
    :param data: dictionary keyed by utt ids. Events must be present in each member
    """
    phones = set()
    for utt_key in data:
        utt = data[utt_key]
        for event in utt.events:
            phones.add(event)
    file = open("phones.txt", "w")
    file.write("<eps> 0 \n")
    phone_idx = 1
    for phone in phones:
        file.write(phone + " " + str(phone_idx) + "\n")
        phone_idx += 1
    file.write("#0 " + str(len(phones) + 1) + "\n")
    file.write("#1 " + str(len(phones) + 2) + "\n")
    file.close()


def make_spk2utt(data, path):
    """
    Write file spk2utt needed by Kaldi
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    """
    import os
    file = open(os.path.join(path, "spk2utt"), "w")
    for utt_idx in data.keys():
        file.write("%05d %05d\n" % (utt_idx, utt_idx))
    file.close()


def make_utt2spk(data, path):
    """
    Write file utt2spk needed by Kaldi
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    """
    import os
    file = open(os.path.join(path, "utt2spk"), "w")
    for utt_idx in data.keys():
        file.write("%05d %05d\n" % (utt_idx, utt_idx))
    file.close()


def make_spk2gender(data, path):
    """
    Write file spk2gender needed by Kaldi. This is a dummy file, you must modify as needed
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    """
    import os
    file = open(os.path.join(path, "spk2gender"), "w")
    for utt_idx in data.keys():
        file.write("%05d m\n" % utt_idx)
    file.close()


def make_wav(data, path, dirpath=''):
    """
    Write file wav needed by Kaldi.
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    :param units_path: prepend this path to the final path for wav file
    """
    import os
    file = open(os.path.join(path, "wav.scp"), "w")
    for utt_idx in data.keys():
        file.write("%05d " % utt_idx + os.path.join(dirpath, data[utt_idx].unit_name) + "\n")
    file.close()


def write_text(data, path):
    """
    Write text file needed by Kaldi. This file is the transcription of each audio
    :param data: dictionary keyed by utt ids. Key 'events' must be present
    :param path: path where the file will be written
    """
    import os
    file = open(os.path.join(path, "text"), "w")
    for utt_idx in data.keys():
        file.write("%05d " % utt_idx)
        for event in data[utt_idx].events:
            file.write(event + " ")
        file.write("\n")
    file.close()


def make_text_txt(data, path):
    """
    Write file text.txt needed by Kaldi. This is a dummy transcription.
    :param data: dictionary keyed by utt ids.
    :param path: path where the file will be written
    """
    import os
    phones = get_phones(data)
    file = open(os.path.join(path, "text.txt"), "w")
    for phone in phones:
        file.write("<s> " + str(phone) + " </s> \n")
    file.close()


def make_words(data, path):
    """
    Write file words needed by Kaldi
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    """
    import os
    phones = get_phones(data)
    file = open(os.path.join(path, "words.txt"), "w")
    file.write("<eps> 0 \n")
    phone_idx = 1
    for phone in phones:
        file.write(phone + " " + str(phone_idx) + "\n")
        phone_idx += 1
    file.write("#0 " + str(len(phones) + 1) + "\n")
    file.write("<s> " + str(len(phones) + 2) + "\n")
    file.write("</s> " + str(len(phones) + 3) + "\n")
    file.close()


def make_silence_phones(data, path, silence_phones=None, optional_silence_phones=None):
    """
    Write files silence_phones.txt, nonsilence_phones.txt, optional_silence.txt needed by Kaldi. This file includes all
    the silent phones (events in our case), non silent phones, and optional silent phones.
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    :param silence_phones: list of silent phones. The set difference all_phones - silence_phones makes the non silent
    phones
    :param optional_silence_phones: list of optional silences
    """
    if optional_silence_phones is None:
        optional_silence_phones = ['SIL']
    if silence_phones is None:
        silence_phones = ['SIL', 'UND']
    import os
    phones = get_phones(data)
    non_silence_phones = [p for p in phones if not p in silence_phones]
    file = open(os.path.join(path, "silence_phones.txt"), "w")
    for phone in silence_phones:
        file.write(phone + "\n")
    file.close()
    file = open(os.path.join(path, "nonsilence_phones.txt"), "w")
    for phone in non_silence_phones:
        file.write(phone + "\n")
    file.close()
    file = open(os.path.join(path, "optional_silence.txt"), "w")
    for phone in optional_silence_phones:
        file.write(phone + "\n")
    file.close()


def make_lexicon(data, path):
    """
    Make lexicon file needed by Kaldi
    :param data: dictionary keyed by utt ids
    :param path: path where the file will be written
    """
    import os
    phones = get_phones(data)
    file = open(os.path.join(path, "lexicon.txt"), "w")
    phone_idx = 1
    for phone in phones:
        file.write(phone + " " + phone + "\n")
        phone_idx += 1
    file.close()


def make_kaldi_files(path, all_data, train_data, test_data, dev_data):
    from os.path import join
    train_dir = join(path, 'exp_data/train')
    test_dir = join(path, 'exp_data/test')
    dev_dir = join(path, 'exp_data/dev')
    data_dir = join(path, 'data')
    write_phones(all_data)
    write_text(all_data, path=data_dir)
    make_text_txt(all_data, data_dir)
    make_words(all_data, data_dir)
    make_silence_phones(all_data, data_dir)
    make_lexicon(all_data, data_dir)
    make_spk2utt(train_data, path=train_dir)
    make_utt2spk(train_data, path=train_dir)
    make_spk2gender(train_data, path=train_dir)
    make_wav(train_data, dirpath=data_dir, path=train_dir)
    write_text(train_data, path=train_dir)
    make_spk2utt(test_data, path=test_dir)
    make_utt2spk(test_data, path=test_dir)
    make_spk2gender(test_data, path=test_dir)
    make_wav(test_data, dirpath=data_dir, path=test_dir)
    write_text(test_data, path=test_dir)
    make_spk2utt(dev_data, path=dev_dir)
    make_utt2spk(dev_data, path=dev_dir)
    make_spk2gender(dev_data, path=dev_dir)
    make_wav(dev_data, dirpath=data_dir, path=dev_dir)
    write_text(dev_data, path=dev_dir)


def compute_events_statistics(data):
    event_counts = {}
    total_events = 0
    for utt_key in data.keys():
        events = data[utt_key].events
        total_events += len([event for event in events if event != "SIL"])
        for event in events:
            if event not in event_counts.keys():
                event_counts[event] = 1
            else:
                event_counts[event] += 1
    return event_counts


def get_event_counts(data):
    event_counts = {}
    total_events = 0
    for utt_key in data.keys():
        events = data[utt_key]['events']
        total_events += len([event for event in events if event != "SIL"])
        for event in events:
            if event not in event_counts.keys():
                event_counts[event] = 1
            else:
                event_counts[event] += 1
    return event_counts
