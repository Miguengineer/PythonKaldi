# Import libraries
import utils

TRA_FILES = ["hyp_1.tra.txt", "hyp_2.tra.txt", "hyp_3.tra.txt", "hyp_4.tra.txt", "hyp_5.tra.txt", "hyp_6.tra.txt",
            "hyp_7.tra.txt", "hyp_8.tra.txt", "hyp_9.tra.txt", "hyp_10.tra.txt", "hyp_11.tra.txt",
            "hyp_12.tra.txt", "hyp_13.tra.txt", "hyp_14.tra.txt", "hyp_15.tra.txt", "hyp_16.tra.txt",
            "hyp_17.tra.txt", "hyp_18.tra.txt", "hyp_19.tra.txt", "hyp_20.tra.txt", "ref.txt"]
utt_idxs = utils.get_utt_idxs()


for tra_f in TRA_FILES:
    f = open(tra_f)
    f_lines = f.readlines()
    events = []
    for line in f_lines:
        events_temp = []
        # Ignore utt idx
        events_ali = line[6:-1].split(" ")
        events_ali.pop()
        for event in events_ali:
            if event != "SIL":
                events_temp.append(event)
        events.append(events_temp)
    if tra_f == "ref.txt":
		    utils.write_text(utt_idxs, events, "ref.txt")
    else:
        utils.write_text(utt_idxs, events, tra_f)
