best_wer = 100
for hyp_idx in range(1, 21):
    f = open('wer_hyp_' + str(hyp_idx) + '.tra.txt')
    lines = f.readlines()
    if float(lines[1][5:11]) < best_wer:
        best_wer = float(lines[1][5:11])
        filename_idx = hyp_idx
        wer_line = lines[1][1:-1]
    f.close()
print("Best WER is: " + str(best_wer))
print("File with best WER: " + 'wer_hyp_' + str(filename_idx) + '.tra.txt')
print(wer_line)
f = open('best_wer.txt', 'w')
f.write("File: " + 'wer_hyp_' + str(filename_idx) + '.tra.txt')
f.write("\n")
f.write(wer_line)
f.close()
