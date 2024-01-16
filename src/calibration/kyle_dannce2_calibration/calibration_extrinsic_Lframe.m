%% Manually target L-frame points to determine extrinsic camera parameters,
% including camera locations and orientations
clear; close all
% basedrive = 'Y:\Kyle\Data\BodyPro';
% basedirs = {
%     '20220424\KSp017'
%     };

basedrive = 'E:\Kyle';
recdirs = {
%     '20230803\KSp023'
%     '20230804\KSp023'
%     '20230805\KSp023'
%     '20230806\KSp023'
%     '20230807\KSp023'
%     '20230808\KSp023'
%     '20230809\KSp023'
%     '20230810\KSp023'
%     '20230811\KSp023'
%     '20230812\KSp023'
%     '20230813\KSp023'
%     '20230814\KSp023'
%     '20230815\KSp023'
    '20230816\KSp023'
    };

numCams = 6;
numPoints = 5;
img_ext = '.tiff';
vid_ext = '.mp4';
filename = '0';

% Input the physical (x,y,z) dimensions for each of the post tops on the L-frame device.
% LFrame_coordinates = [ -5 -5 2.5; 5 -5 4.5; -5 5 6.5; 0 0 8.5; 5 5 10.5];% old imprecise
LFrame_coordinates = [ -5 -5 2.40; 5 -5 4.42; -5 5 6.4; 0 0 8.40; 5 5 10.30]; % empirically-measured
LFrame_coordinates = 10*(double(LFrame_coordinates)); % cm to mm

%% Convert average frame of video to tiff
for b = 1:numel(recdirs)
    basedir = recdirs{b};
    try
        disp(basedir)
        for kk = 1:numCams
            disp(['Computing mean extrinsic image for Camera' num2str(kk)])
            extrdir = fullfile(basedrive, basedir, 'video', 'calibration', 'extrinsic');
            viddir = fullfile(extrdir, ['Camera' num2str(kk)], [filename vid_ext]);
            video_temp = VideoReader(viddir, 'CurrentTime',0);
            frame_temp = zeros(video_temp.Height,video_temp.Width,3);
            for i = 1:video_temp.NumFrames
                frame_temp = frame_temp + double(readFrame(video_temp));
            end
            frame_temp = frame_temp / video_temp.NumFrames;
            frame_temp = uint8(frame_temp);
            imwrite(frame_temp, fullfile(extrdir, ['Camera' num2str(kk)], [filename img_ext]))
        end
    catch e
        disp(e)
    end
end
clear video_temp

%% Click points for each post top in order for each view
close all;

basedir = recdirs{1};

calibdir = fullfile(basedrive, basedir, 'video', 'calibration');
extrdir = fullfile(calibdir, 'extrinsic');
lframe = cell(numCams,1);
for i = 1:numCams
    lframe{i} = imread( fullfile(extrdir, ['Camera' num2str(i)], [filename img_ext]) );
end
load( fullfile(calibdir, 'intrinsic', 'cam_intrinsics.mat') );

figure('Name','Click L-Frame points from shortest to tallest!');
for kk = numel(lframe):-1:1
    camparams = params_individual{kk};
    LFrame_image{kk} = undistortImage(lframe{kk}, camparams);
    imshow(LFrame_image{kk}); %colormap(gray)
    [xi,yi] = getpts;
    point_coordinates{kk} = [xi yi];
end

% Remove any extra points at the end that were accidentally marked
for kk = 1:numel(lframe)
    point_coordinates{kk} = point_coordinates{kk}(1:numPoints,:);
end
point_coordinates = cellfun(@(x) double(x), point_coordinates, 'Uni',0);
save(fullfile(extrdir, 'point_coordinates.mat'), 'point_coordinates');

%% Use selected points to calculate camera extrinsics

basedir = recdirs{1};
calibdir = fullfile(basedrive, basedir, 'video', 'calibration');
extrdir = fullfile(calibdir, 'extrinsic');
lframe = cell(numCams,1);
for i = 1:numCams
    lframe{i} = imread( fullfile(extrdir, ['Camera' num2str(i)], [filename img_ext]) );
end
params_individual = matfile(fullfile(calibdir, 'intrinsic', 'cam_intrinsics.mat')).params_individual;
point_coordinates = matfile(fullfile(extrdir, 'point_coordinates.mat')).point_coordinates;

[final_err, ...
rotationMatrix, ...
translationVector, ...
worldOrientation, ...
worldLocation] = deal(cell(numel(lframe),1));

parfor kk = 1:numel(lframe)
    rng("shuffle")
    disp(strcat("Calculating extrinsics for Camera", num2str(kk)))
    pause(0.001)

    % Do hyperparameter search
    [curr_err, mn] = deal(1e10);
    [cnt, c_save, mr_save, worldO_save, worldL_save] = deal(0);

    % Load intrinsic params and L-frame data
    params_ind = params_individual{kk};
    point_coords = point_coordinates{kk};
    
    % Because camera pose estimation is not deterministic, 
    % run loop many times to find the best extrinsic parameters
    for i = 1:500
        success = false;
        while success == false
            for c = [99:-4:79 50 1]
                for mr = [0.5:1:3 20 100]
                    try
                        [worldO, worldL] = estimateWorldCameraPose( ...
                            point_coords, ...
                            LFrame_coordinates, ...
                            params_ind, ...
                            'Confidence',c, ...
                            'MaxReprojectionError',mr, ...
                            'MaxNumTrials',mn);
                        [rotationM, translationV] = cameraPoseToExtrinsics(worldO, worldL);
                        imagePoints = worldToImage(params_ind, rotationM, translationV, LFrame_coordinates);
                        err = mean(sqrt(sum((imagePoints - point_coords).^2, 2)));
                        if err < curr_err
                            disp(strcat("Found better repro error for Camera", ...
                                num2str(kk), ": ", num2str(err)))
                            pause(0.001)
                            curr_err = err;
                            worldO_save = worldO;
                            worldL_save = worldL;
                        end
                        success = true;
                    catch e
                        %disp(e)
                    end
                end
            end
        end
        
    end
      
    try
        [rotationM, translationV] = cameraPoseToExtrinsics(worldO_save, worldL_save);
        imagePoints = worldToImage(params_ind, rotationM, translationV, double(LFrame_coordinates));
        final_err{kk} = mean( sqrt( sum( (imagePoints - point_coords) .^ 2, 2) ) );
        rotationMatrix{kk} = rotationM;
        translationVector{kk} = translationV;
        worldOrientation{kk} = worldO_save;
        worldLocation{kk} = worldL_save;
    catch e
        disp(e)
    end
end

figure(222); set(gcf,'Color','w')
set(gca,'TickDir','out')
hold on
for kk = 1:numel(lframe)
    plotCamera('Location',worldLocation{kk}, ...
        'Orientation',worldOrientation{kk}, ...
        'Size',50, ...
        'Label',num2str(kk));
    disp(['Final error for Camera' num2str(kk) ': ' num2str(final_err{kk})])
    pause(0.01)
end
print('-dpng',fullfile(calibdir, 'cameraArrangement.png'));

% Save full camera parameters: intrinsics, extrinsics
save(fullfile(calibdir, 'camera_params.mat'), ...
    'params_individual', ...
    'worldOrientation', ...
    'worldLocation', ...
    'rotationMatrix', ...
    'translationVector');

% Save annotated points
point_coordinates = cellfun(@(x) double(x), point_coordinates, 'Uni',0);
save(fullfile(calibdir, 'extrinsic', 'point_coordinates.mat'), 'point_coordinates');
disp('Done!')

%% Examine reprojections
for kk = 1:numel(lframe)
    figure(233+kk)
    imshow(LFrame_image{kk}); colormap(gray);
    hold on
    
    tmp_v = translationVector{kk};
    tmp_r = rotationMatrix{kk};
    imagePoints = worldToImage(params_individual{kk}, tmp_r, tmp_v, double(LFrame_coordinates)); % ,'ApplyDistortion',true
    
    colorarray = jet(size(imagePoints,1));%{'r','g','b','y','m','w','k'};
    for llll = 1:size(imagePoints,1)
        plot(imagePoints(llll,1),imagePoints(llll,2),'o', 'MarkerSize',4, ...
            'MarkerEdgeColor',colorarray(llll,:), 'MarkerFaceColor',colorarray(llll,:))
    end
    for llll = 1:size(imagePoints,1)
        plot(point_coordinates{kk}(llll,1),point_coordinates{kk}(llll,2),'x', 'MarkerSize',4, ...
            'MarkerEdgeColor',colorarray(llll,:), 'MarkerFaceColor',colorarray(llll,:))
    end
    hold off
    print('-dpng',fullfile(calibdir, ['camerareproject',num2str(kk),'.png']));
    mean(sqrt(sum((imagePoints - point_coordinates{kk}).^2,2)))
end
