function [rotationMatrix, translationVector] = calibrate_cameras_extrinsic(lframe_image, params_individual, savePath)
% LFrame_coordinates - the x y z coords of each L frame point
num_cams = numel(lframe_image);
allimagepoints = cell(1,num_cams);
checkerboard_images_undistorted = cell(1,num_cams);
boardSize_ch_full = cell(1,num_cams);
L3D = cell(1,num_cams);

% Save files for checkerboard detection in python.
tempFile = 'C:/data/calibration/calPyScratch.mat';
tempFile2 = 'C:/data/calibration/calPyScratchOut.mat';
[s1,s2,~,~] = size(lframe_image{1});
undistortedIms = uint8(zeros(s1,s2,3,num_cams));
for i = 1:num_cams
    camparams = params_individual{i};
    medianImage = uint8(median(lframe_image{i},4));
%     medianImage = uint8(lframe_image{i}(:,:,:,end));
    undistortedIms(:,:,:,i) = undistortImage(medianImage, camparams);
%     undistortedIms(:,:,:,i) = medianImage;
end
figure;
for i = 1:num_cams
    subplot(2,3,i);
    imshow(undistortedIms(:,:,:,i))
end
% keyboard;

save(tempFile,'undistortedIms');

% Run checkerboard detection in python
commandStr = 'python C:/code/calibration/cal.py';
[status, stdout] = system(commandStr);
disp(stdout)
if status ~= 0 
%     keyboard;
    error('Checkerboard detection failed') 
end

% Collect the checkerboard points
load(tempFile2,'objPoints','imgPoints');
% keyboard
for kk = 1:num_cams
    pIds = squeeze(objPoints(kk,:,:));
    imagePoints_ch = squeeze(imgPoints(kk,:,:,:));
    boardSize_ch_full{kk} = max(pIds(:,1:2));
    allimagepoints{kk} = imagePoints_ch;
   
    % We need to have the x axis be the short axis, and the y axis be the
    % long axis if we want the z-axis to be positive pointing upward.
    % (right-hand rule) This is different than what is on the checkerboard
    % pattern. 
    L3D{kk} = pIds(:, [2 1 3]);
    checkerboard_images_undistorted{kk} = undistortedIms(:,:,:,kk)./255;
end

% compute the world coordinates
worldOrientation = cell(num_cams,1);
worldLocation = cell(num_cams,1);
rotationMatrix = cell(num_cams,1);
translationVector = cell(num_cams,1);

for kk=1:num_cams
     [worldOrientation{kk},worldLocation{kk}] = estimateWorldCameraPose2(double(allimagepoints{kk}),...
        double(L3D{kk}),params_individual{kk},'Confidence',95,'MaxReprojectionError',4,'MaxNumTrials',5000);

    [rotationMatrix{kk},translationVector{kk}] = cameraPoseToExtrinsics(worldOrientation{kk},worldLocation{kk});
    
    % Plot to verify
    figure(1); subplot(3,2,kk)
    image(checkerboard_images_undistorted{kk})
    hold on
    imagePoints = worldToImage(params_individual{kk},rotationMatrix{kk},...
        translationVector{kk},double(L3D{kk}));
    plot(allimagepoints{kk}(:,1),allimagepoints{kk}(:,2),'or')
    plot(imagePoints(:,1),imagePoints(:,2),'ok')
    
    figure(226)
    plotCamera('Location',worldLocation{kk},'Orientation',worldOrientation{kk},'Size',100,'Label',num2str(kk));
    hold on
    view([-91 84])
    if (kk == num_cams)
        print('-dpng',strcat(savePath,'cameraarrangement.png'));
    end
    xlabel('x')
    ylabel('y')
    figure(227)
    plotCamera('Location',worldLocation{kk},'Orientation',worldOrientation{kk},'Size',100,'Label',num2str(kk));
    hold on
    xlabel('x')
    ylabel('y')
%     view([-91 84])
    if (kk == num_cams)
        print('-dpng',strcat(savePath,'cameraarrangement.png'));
    end
end
