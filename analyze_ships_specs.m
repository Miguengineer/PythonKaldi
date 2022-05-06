 utt_keys = [1865, 1868, 1874, 3038, 3674, 4099, 4103, 4105, 4107, 4109, 4348, 4351, 4352, 4353, 4354, 4400, 4401, 4402, 4416, 4737, 4738, 4739, 4740, 4743, 4744, 4745, 4747, 4748, 4749, 4751, 4752, 4838, 4859, 1866, 1875, 3025, 4100, 4101, 4104, 4110, 4112, 4350, 4355, 4741, 4746, 4861, 1867, 4102, 4106, 4108, 4111, 4349, 4417, 4736, 4742, 4750, 4839, 4860];
wav = fopen('/home/miguel/HMM-GMM-Beta/exp_data/train/wav.scp');
line = fgetl(wav);
ships_dirs = cell(1, length(utt_keys));
ships_idx = 1;
while ischar(line)
    utt_idx = str2double(line(1:5));
    if sum(ismember(utt_idx, utt_keys)) ~= 0
        ships_dirs{ships_idx} = line(7:end);
        ships_idx = ships_idx + 1;
    end
    line = fgetl(wav);
end
fclose(wav);
wav = fopen('/home/miguel/HMM-GMM-Beta/exp_data/test/wav.scp');
line = fgetl(wav);
while ischar(line)
    utt_idx = str2double(line(1:5));
    if sum(ismember(utt_idx, utt_keys)) ~= 0
        ships_dirs{ships_idx} = line(7:end);
        ships_idx = ships_idx + 1;
    end
    line = fgetl(wav);
end
fclose(wav);
wav = fopen('/home/miguel/HMM-GMM-Beta/exp_data/dev/wav.scp');
line = fgetl(wav);
while ischar(line)
    utt_idx = str2double(line(1:5));
    if sum(ismember(utt_idx, utt_keys)) ~= 0
        ships_dirs{ships_idx} = line(7:end);
        ships_idx = ships_idx + 1;
    end
    line = fgetl(wav);
end
fclose(wav);
audios = cell(1, length(utt_keys));
for i=1:length(ships_dirs)
    audios{i} = audioread(ships_dirs{i});
end

plot_ships=true;
if plot_ships
    figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i}, 64, 32, 256, 250, 'yaxis')
    end
    figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i + 9}, 64, 32, 256, 250, 'yaxis')
    end
    
    figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i + 9*2}, 64, 32, 256, 250, 'yaxis')
    end
    figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i + 9*3}, 64, 32, 256, 250, 'yaxis')
    end
    figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i + 9*4}, 64, 32, 256, 250, 'yaxis')
    end
        figure;
    for i=1:9
        subplot(3, 3, i)
        spectrogram(audios{i + 9*5}, 64, 32, 256, 250, 'yaxis')
    end
end



