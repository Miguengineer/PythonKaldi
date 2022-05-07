#%%
from scipy.io import loadmat
PATH = '/home/miguel/HMM-GMM-Beta/ALIPHO/'
ali = loadmat(PATH + 'ALI_PHO.mat')
ali = ali['ALI'][0]
#%%
# Convert ali to just a list of lists
final_ali = []
for utt in ali:
    current_ali = []
    for frame_list in utt:
        current_ali.append(int(frame_list[0]))
    final_ali.append(current_ali)
#%% Initialize dict
phones_count = {}
phones_avgs_count = {}
# We have 1-71 phones
for phone_idx in range(1, 72):
    # [min, max, avg, min_idx, max_idx]
    phones_count[phone_idx] = [10000, -1, 0, -1, -1]
    phones_avgs_count[phone_idx] = []
#%% Compute statistics
import numpy as np
# For each utterance
for utt_idx in range(len(final_ali)):
    utt_list = final_ali[utt_idx]
    first_label = utt_list[0]
    count = 1
    # For each alignment of each frame in current utterance
    for frame_idx in range(1, len(utt_list)):
        current_frame_label = utt_list[frame_idx]
        if first_label == current_frame_label:
            count = count + 1
            # Check if we have reached last frame
            if frame_idx == len(utt_list) - 1 and count > 1:
                # Check statistics for phone that has just changed
                statistics = phones_count[first_label]
                if statistics[0] > count:
                    phones_count[first_label] = [count, statistics[1], statistics[2], utt_idx + 1, statistics[4]]
                if statistics[1] < count:
                    phones_count[first_label] = [statistics[0], count, statistics[2], statistics[3], utt_idx + 1]
                phones_avgs_count[first_label].append(count)
                count = 1
        else:
            phones_avgs_count[first_label].append(count)
            # Check for 'dummy' min, which is the first frame
            if count == 1 and frame_idx == 1:
                first_label = current_frame_label
                continue
            # Check statistics for phone that has just changed
            statistics = phones_count[first_label]
            # Update min
            if statistics[0] > count:
                phones_count[first_label] =[count, statistics[1], statistics[2], utt_idx + 1, statistics[4]]
            # Update max
            if statistics[1] < count:
                phones_count[first_label] = [statistics[0], count, statistics[2], statistics[3], utt_idx + 1]
            count = 1
            first_label = current_frame_label
for p_idx in phones_avgs_count.keys():
    stats = phones_count[p_idx]
    phones_count[p_idx] = [stats[0], stats[1], np.sum(phones_avgs_count[p_idx]) / len(phones_avgs_count[p_idx]),
                           stats[3], stats[4]]
#%% To pandas dataframe
import pandas as pd
import numpy as np
phone_idx = []
mins = []
maxs = []
avgs = []
min_idxs= []
max_idxs = []
for p_idx in phones_count.keys():
    stats = phones_count[p_idx]
    phone_idx.append(p_idx)
    mins.append(stats[0])
    maxs.append(stats[1])
    avgs.append(np.round(stats[2]))
    min_idxs.append(stats[3])
    max_idxs.append(stats[4])
df = pd.DataFrame(list(zip(phone_idx, mins, maxs, avgs, min_idxs, max_idxs)), columns=['Phone', 'Min', 'Max','Avg',
                                                                                       'Min Idx', 'Max Idx'])
df.to_csv('frame_statistics.csv', index=False)
#%% Count frames
import pandas as pd
frames_count = {}
for phone_idx in range(1, 72):
    # [min, max, avg, min_idx, max_idx]
    frames_count[phone_idx] = 0
for utt in ali:
    for frame in utt:
        frames_count[frame[0]] += 1
# To list
phone_idx = []
num_frames = []
for p_idx in frames_count.keys():
    phone_idx.append(p_idx)
    num_frames.append(frames_count[p_idx])
df = pd.DataFrame(list(zip(phone_idx, num_frames)))
df.to_csv('frames_count.csv', index=False)