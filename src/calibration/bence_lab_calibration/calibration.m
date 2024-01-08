%% Script for camera calibration
% Before running this script, you need to collect intrinsic and extrinsic
% calibration videos using campy. 
%
% Set the sessionFolder to the calibration 

addpath(genpath("C:/Ucode/matlab_toolbox"))
%sessionFolder = 'C:/data/setupCal2/';
sessionFolder = 'C:\data\calibration\setupCalPhotometry\'
% sessionFolder = 'C:\data\calibration\10_22_2020_large_board';
savePath = sessionFolder;

% %% Load the videos 
% videoFolder = fullfile(sessionFolder, 'intrinsic');
% cameraFolders = dir(fullfile(videoFolder, 'Camera*'));
% cameraFolders = arrayfun(@(X) fullfile(videoFolder, X.name), cameraFolders,'uni',0);
% intrinsic_videos = cell(numel(cameraFolders),1);
% parfor nCam = 1:numel(cameraFolders)
%     videoFile = char(fullfile(cameraFolders{nCam}, '0.mp4'));
%     disp(sprintf('Loading: %s',videoFile))
%     intrinsic_videos{nCam} = readFrames(videoFile,1:10:6000);
% end

%% Load frames for the extrinsics
videoFolder = fullfile(sessionFolder, 'extrinsics');
cameraFolders = dir(fullfile(videoFolder, 'Camera*'));
cameraFolders = arrayfun(@(X) fullfile(videoFolder, X.name), cameraFolders,'uni',0);
extrinsic_videos = cell(numel(cameraFolders),1);
for nCam = 1:numel(cameraFolders)
    videoFile = char(fullfile(cameraFolders{nCam}, '0.mp4'));
    disp(sprintf('Loading: %s',videoFile))
    extrinsic_videos{nCam} = readFrames(videoFile, 1:10);
end

%%
% load('temp');
single_cam_calibration_folder = 'C:/data/calibration/setupCalPhotometry/intrinsics/';
cameraFolders = dir(fullfile(single_cam_calibration_folder,'Camera*'));
cameraFolders = arrayfun(@(X) fullfile(single_cam_calibration_folder, X.name), cameraFolders,'uni',0);
for i = 1:numel(cameraFolders)
    param = load(fullfile(cameraFolders{i},'intrinsic_params.mat'));
    intrinsic_params{i} = param.cameraParams;
end
[rotationMatrix, translationVector] = calibrate_cameras_extrinsic(extrinsic_videos, intrinsic_params, savePath);

%% saves data needed for dannce
for nCam = 1:numel(intrinsic_params)
    RDistort = intrinsic_params{nCam}.RadialDistortion;
    TDistort = intrinsic_params{nCam}.TangentialDistortion;
    r = rotationMatrix{nCam};
    t = translationVector{nCam};
    K = intrinsic_params{nCam}.IntrinsicMatrix;
    save(fullfile(savePath,sprintf('hires_cam%d_params.mat',nCam)),'K','r','t','RDistort','TDistort')
end




