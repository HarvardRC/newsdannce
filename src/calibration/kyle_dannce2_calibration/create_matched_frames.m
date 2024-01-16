%% Use this to create a Jesse-like matched_frames precursor
clear; clc;

camnames{1} = 'Camera1';
camnames{2} = 'Camera2';
camnames{3} = 'Camera3';
camnames{4} = 'Camera4';
camnames{5} = 'Camera5';
camnames{6} = 'Camera6';

vidname = '0.mp4';
frame_rate = 100; % frame rate
frame_period = 1000 / frame_rate; % frame period
num_markers = 44; %for mouse44
% num_markers = 22; %for mouse22
        
baseDir = 'E:\Kyle';
recDirs = {'20230815'};
key = 'KSp*';
        
for d = 1:numel(recDirs)
    mouseDirs = dir(fullfile(baseDir,recDirs{d},key));
    for m = 1:numel(mouseDirs)
        try
            recDir = fullfile(recDirs{d},mouseDirs(m).name);
            baseFolder = fullfile(baseDir, recDir, 'video');
            syncDir = fullfile(baseFolder, 'sync');
            cd(baseFolder)
            disp(baseFolder)

            for cam = numel(camnames):-1:1
                disp(num2str(cam))
                videoFolder = fullfile(baseFolder,'videos',camnames{cam});
                vid = VideoReader(fullfile(videoFolder,vidname), 'CurrentTime',0);
                vid_len(cam) = vid.Duration * vid.FrameRate;
            end
            num_frames = min(vid_len)

            mframes = 1 : num_frames * frame_period;
            mframes = floor(mframes / frame_period) + 1; %for matlab 1-indexing

            matched_frames_aligned = {};
            for i = numel(camnames):-1:1
                matched_frames_aligned{i} = mframes;
            end

            % load
            for cam = 1:numel(camnames)
                clear data_2d data_3d
                frame_inds = 1 : frame_period : length(matched_frames_aligned{cam});
                frame_inds = round(frame_inds);    
                data_sampleID = nan(length(frame_inds),1);
                data_frame = nan(length(frame_inds),1);
                data_2d = zeros(length(frame_inds),2*num_markers);
                data_3d = zeros(length(frame_inds),3*num_markers);

                cnt = 1;
                for frame_to_plot = frame_inds  
                    data_sampleID(cnt) = frame_to_plot;
                    data_frame(cnt) = matched_frames_aligned{cam}(frame_to_plot) - 1;    
                    cnt = cnt + 1;
                end
                data_frame(data_frame<0) = 0;
                save(fullfile(syncDir, [camnames{cam} '_Sync']),'data_frame','data_2d','data_3d','data_sampleID');
            end
        catch e
            disp(e)
        end
    end
end