%% Calculate extrinsics from a common view of a checkerboard pattern  - 
% Code by Iris Odstrcil 07/10/23

%% Common user-set variables
numcams = 5;

%% Test if checkerboads get detected
% Load an image containing the checkerboard pattern for each camera to
% figure out the parameters that are needed to detect the points
clear all;

[baseName, folder] = uigetfile('.png'); % '.jpeg'
imageFileName = fullfile(folder, baseName);

Image = imread(imageFileName);
I = imread(imageFileName);
%I= uint16(imbinarize(Image));

%%
% Detect the checkerboard points
[imagePoints1, boardSize1] = detectCheckerboardPoints( ...
    I, 'MinCornerMetric', 0.15, 'HighDistortion', false, 'PartialDetections', true);


%% Display detected points
J = insertText(I, imagePoints1, 1:size(imagePoints1, 1));
J = insertMarker(J, imagePoints1, 'o', 'Color', 'red', 'Size', 5);
imshow(J);
title(sprintf('Detected a %d x %d Checkerboard', boardSize1));

%%
for ii = 1 : numcams
    imagePoints1(:, :, ii) = imagePoints;
    boardSize1(:, :, ii) = boardSize;
end 

clear imagePoints boardSize;

imagePoints = imagePoints1;
boardSize = boardSize1;

save([folder 'checker_points'], 'boardSize', 'imagePoints');


%% Start here for real
% Once I have determined the parameters (mincornermetric and distortion) for each camera, this is the actual pipeline 
%% Finding the imagePoints

numcams=5;

% For this to work as is, the images have to be in a common folder.

%Write a vector that defines whether each image is hi or lo distortion for
%point detection.
hi_distortion=[0,0,0,0,0];

% Create a cell array of file names of calibration images
[imageFileNames, folder] = uigetfile('.png', 'Multiselect', 'on'); % '.jpeg'

% Detect calibration pattern
for ii=1: numel(imageFileNames)
    [imagePoints(:,:,ii), boardSize(:,:,ii)] = detectCheckerboardPoints(fullfile(folder,imageFileNames{ii}), ...
        'MinCornerMetric', 0.15, 'HighDistortion', hi_distortion(ii), 'PartialDetections', false);   
end

% Display detected points

for ii = 1:numel(imageFileNames)
    I = imread(fullfile(folder,imageFileNames{ii}));
    subplot(2,3,ii);
    imshow(I); hold on; plot(imagePoints(:,1,ii), imagePoints(:,2,ii), 'ro');
    plot(imagePoints(1,1,ii), imagePoints(1,2,ii), 'g*'); %show origin in green
end
 
% Now we have a collection of points detected in all images, which will be
% used for extrinsic parameter calculation.

save([folder 'imagePoints'],'boardSize','imagePoints');

%% Extrinsics 

% Access the intrinsic parameters of each camera
pathName = "\\tungsten-nas.fmi.ch\tungsten\scratch\gluthi\odstiris\data\HomeCage_BLA\Calibration_231121\IRLights\";

intrinsics = cell(1,numcams);
params_individual = cell(1,5);

for ii = 1:numcams
    load(strcat(pathName, 'Camera', num2str(ii),'\cameraParams.mat')) 
    intrinsics{ii}= cameraParams.Intrinsics;
    params_individual{ii}= cameraParams;

    clear cameraParams
end

%% Create a matrix containing the checkerboard points 
% Extract the checkerboard's world points.
% The current board I am using is 6 x 7, 25 mm, so 30 points

y_spacing = 0 : 25 : 5*25;
x_spacing = 0 : 25 : 4*25;

checkerPoints_world(:, 1) = repmat(x_spacing, 1, 6); 
checkerPoints_world(:, 2) = repelem(y_spacing, 5); 

worldPoints = checkerPoints_world;
worldPoints(:, 3) = zeros(size(checkerPoints_world, 1), 1);

%% Create a cell with all the common-view images

% Create a cell array of file names of calibration images
[imageFileNames, folder] = uigetfile('.png', 'Multiselect', 'on'); % '.jpeg'

for ii = 1:numel(imageFileNames)
    Images{ii} = imread(fullfile(folder, imageFileNames{ii}));
    subplot(2, 3, ii);
    imshow(Images{ii});
    hold on;
    plot(imagePoints(:, 1, ii), imagePoints(:, 2, ii), 'ro');
    plot(imagePoints(1, 1, ii), imagePoints(1, 2, ii), 'g*'); %show origin in green
end
 
% From here go to Tim's code:

%% Just use wtf to calibrate extrinsics de novo
squareSize = 25.0; %mm
%worldPoints = generateCheckerboardPoints(nc.boardSize,squareSize);
%worldPoints(:,3) = 0;
point_coordinates_undistorted_checker = {};

wrf = cell(1,numcams);
for ii=1:numcams %[1,2,3,4,5]
    wtf{ii}=imagePoints(:,:,ii); 
end

for kk = 1:numcams %[1,2,3,4,5]
    points2d = double(wtf{kk});
    point_coordinates_undistorted_checker{kk} = points2d;
    [worldOrientation{kk}, worldLocation{kk}] = estimateWorldCameraPose(points2d, double(worldPoints), ...
        params_individual{kk}, 'Confidence', 98, 'MaxReprojectionError', 2, 'MaxNumTrials', 5000);
    [rotationMatrix{kk}, translationVector{kk}] = cameraPoseToExtrinsics(worldOrientation{kk},worldLocation{kk});
    
    figure(222)
    plotCamera('Location',worldLocation{kk},'Orientation',worldOrientation{kk},'Size',50,'Label',num2str(kk));
    hold on
end

%% Plot projected checkerboard
for kk = 1:numcams %[1,2,3,4,5]
    fh = figure(kk);
    %imagesc(nc.lframe_undistorted{kk});colormap(gray);
    imagesc(Images{kk});
    colormap(gray);
    set(gca,'dataaspectratio', [1,1,1]);
    hold on;
    imagePoints = worldToImage(params_individual{kk}, rotationMatrix{kk}, translationVector{kk}, double(worldPoints));
    colorarray = hsv(size(imagePoints ,1));
    for llll = 1:size(imagePoints,1)
        plot(imagePoints(llll,1),imagePoints(llll,2), 'o', 'MarkerSize', 4, ...
            'MarkerEdgeColor', colorarray(llll,:))
    end

    % plot the detected 2d points on top
    plot(wtf{kk}(:,1), wtf{kk}(:,2), 'bx')
    clear llll
        err = sqrt(sum((imagePoints-wtf{kk}).^2, 2));
        display(['mean repojection error for camera ' num2str(kk) ' is ' num2str(mean(err(:)))])    
end

%%
basedir = './';
dateString = strcat(datestr(now, 'yyMMdd'), 'd', datestr(now, 'HHmm'), 't');
save([basedir filesep dateString '_camera_params_checkerboard'], ...
    'params_individual','worldOrientation','worldLocation','rotationMatrix','translationVector','-v7.3');


%% Extra code that I wrote at some point but doesn't quite work
% Load an image of a checkerboard in a shared location.
for ii = 1:numcams
    imOrig{ii} = imread(fullfile(folder, imageFileNames{ii})); 
    figure;
    imshow(imOrig{ii});
    title("Input Image");

    % Undistort the image.
    [im{ii}, newOrigin{ii}] = undistortImage(imOrig{ii}, intrinsics{1, ii}, OutputView="full");

    %Find the reference object in the new image.
    [imagePoints(:, :, ii),boardSize(:, :, ii)] = detectCheckerboardPoints( ...
        im{ii}, 'MinCornerMetric', 1.5, 'HighDistortion', false, 'PartialDetections', false);

    %[imagePoints1,boardSize1] = detectCheckerboardPoints(im{ii},'MinCornerMetric', 0.5, 'HighDistortion', false, 'PartialDetections', true);

    % Display detected points
    J = insertText(im{ii}, imagePoints(:, :, ii), 1 : size(imagePoints(:, :, ii), 1));
    J = insertMarker(J, imagePoints(:, :, ii), 'o', 'Color', 'red', 'Size', 5);
    imshow(J);
    title(sprintf('Detected a %d x %d Checkerboard', boardSize(:, :, ii)));

    %Compensate for the image coordinate system shift.
    imagePoints(:, :, ii) = imagePoints(:, :, ii) + newOrigin{ii};

    %Calculate new extrinsics.
    camExtrinsics{ii} = estimateExtrinsics(imagePoints(:, :, ii), checkerPoints_world, intrinsics{1, ii});

    %Calculate the camera pose.
    camPose{ii} = extr2pose(camExtrinsics{1, ii});
    figure
    plotCamera(AbsolutePose=camPose{1, ii}, Size=20);
    hold on;
    pcshow([checkerPoints_world, zeros(size(checkerPoints_world, 1), 1)], ...
        VerticalAxisDir="down", MarkerSize=40);

    % Calculate the camera world pose
    worldPose{ii} = estworldpose(imagePoints(:, :, ii), worldPoints, intrinsics{1, ii});
end


%% camera to world image

figure(222)
%plot checkerboard points
plot3(worldPoints(:, 1), worldPoints(:, 2), zeros(size(worldPoints, 1), 1), "o");
hold on;
%mark origin
plot3(0, 0, 0, "go");
%set(gca,CameraUpVector=[0 0 -1]);

for kk = 1:numcams
    %plotCamera('Location',worldLocation{kk},'Orientation',worldOrientation{kk},'Size',5,'Label',num2str(kk));
    plotCamera(AbsolutePose = camPose{1, kk}, Size=20, Label=num2str(kk));
    hold on;
end


%% Save full camera parameters: intrinsics, extrinsics

basedir = "\\tungsten-nas.fmi.ch\tungsten\scratch\gluthi\odstiris\data\HomeCage_BLA\Calibration\";

worldOrientation = cell(1, numcams);
worldLocation = cell(1, numcams);
rotationMatrix = cell(1, numcams);
translationVector = cell(1, numcams);


for ii = 1:numcams
    worldOrientation{ii} = camPose{1, ii}.R';  % it's the transpose of Worldpose.R
    worldLocation{ii} = camPose{1, ii}.Translation;
    rotationMatrix{ii} = camExtrinsics{1, ii}.R;  
    translationVector{ii} = camExtrinsics{1, ii}.Translation;  
end

save([basedir 'camera_params'], 'params_individual', 'worldOrientation', 'worldLocation', 'rotationMatrix', 'translationVector');
%% Turn params into mat file for label3d

path_to_cam_params = "\\tungsten-nas.fmi.ch\tungsten\scratch\gluthi\odstiris\data\HomeCage_BLA\Calibration_231121\IR_Checker7\camera_params_checkerboard";
path_to_video = "\\tungsten-nas.fmi.ch\tungsten\scratch\gluthi\odstiris\data\HomeCage_BLA\Calibration_231121\Mouse_IR\";
output_path = "\\tungsten-nas.fmi.ch\tungsten\scratch\gluthi\odstiris\data\HomeCage_BLA\Calibration_231121\Mouse_IR\TestMouse_ch7_mouse18__dannce.mat";
n_landmarks = 18;

transferParams(path_to_cam_params, path_to_video, output_path, n_landmarks);

%%
% worldPoints1= worldPoints;
% worldPoints1(:,3)= zeros(30,1); 
% 
% for ii=1:5;
%     worldPose{ii} = estworldpose(imagePoints(:,:,ii),worldPoints1,intrinsics{1,ii});
% end

