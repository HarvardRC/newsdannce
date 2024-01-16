clear; clc

numCams = 6;

basedirs = {
    'E:\Kyle\20230815\KSp023'
    };

for b = 1:numel(basedirs)
    baseFolder = basedirs{b};

    load( fullfile(baseFolder, 'video', 'calibration', 'camera_params.mat') )
    load( fullfile(baseFolder, 'video', 'calibration', 'intrinsic', 'cam_intrinsics.mat') )
    % extrinsics
    % r = rotation matrix
    % t = translation matrix

    % intrinsics
    % K = intrinsic matrix
    % RDistort = RadialDistortion
    % TDistort = TangentialDistortion

    for i = 1:numCams
        outputFolder = fullfile(baseFolder, 'video', 'calibration');
        r = rotationMatrix{i};
        t = translationVector{i};
        K = params_individual{i}.IntrinsicMatrix;
        RDistort = params_individual{i}.RadialDistortion;
        TDistort = params_individual{i}.TangentialDistortion;
        save([outputFolder filesep 'kyle_cam' num2str(i) '_params'],'r','t','K','RDistort','TDistort')
    end
end

disp('Done!')





