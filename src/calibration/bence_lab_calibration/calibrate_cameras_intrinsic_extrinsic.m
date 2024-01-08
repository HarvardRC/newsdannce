function [] = calibrate_cameras_intrinsic_extrinsic(checkerboard_vids, lframe_image, squareSize, savepath)

%% Script for calibrating multiple cameras in Matlab
% original: Jesse Marshall 2019
% updated, v1: Kiah Hardcastle, Aug 2020

% NOTES ON INPUTS

% checkerboard_vids: should contain frames with checkerboard visible in
% 20-40 frames. should be 100+ frames in total. best if the exposure time
% is short so there isn't blur in the images. will have to change camera
% settings to accomodate this (lower fps, shorter exposure).
% Cell array of h x w x c x f videos with nCamera elements
%
% lframe_image: frame from each of the cameras with the l-frame in
%               it. l-frame can be the checkerboard, with markings on it.
%
%   
%
% squareSize - mm of a checkerboard square
%
% LFrame_coordinates - the x y z coords of each L frame point


num_cams = numel(checkerboard_vids);
num_cams = 1;
% set names

%% get intrinsic parameters for each camera

params_individual = cell(1,num_cams);
estimationErrors = cell(1,num_cams);
for kk = 1:num_cams

    % find the checkerboard in the frames
    fprintf('finding checkerboard points \n')
    
    [imagePoints, boardSize, imagesUsed] = ...
        detectCheckerboardPoints(checkerboard_vids{kk});
    
    worldPoints = generateCheckerboardPoints(boardSize,squareSize);
    imagesUsed = find(imagesUsed);
    
    % report images with checkerboard in them
    fprintf('images used %f \n',numel(imagesUsed))
    
    % estimate the camera parameters
    I = checkerboard_vids{kk}(:,:,:,1);
    imageSize = [size(I,1),size(I,2)];
    [params_individual{kk},~,estimationErrors{kk}] = estimateCameraParameters(...
        imagePoints,worldPoints, ...
        'ImageSize',imageSize,...
        'EstimateTangentialDistortion',true,...
        'NumRadialDistortionCoefficients',3,'EstimateSkew',true);
    
    % compute the reprojection errors
    figure(880+kk)
    showReprojectionErrors(params_individual{kk});
    print('-dpng',strcat(savepath,'Reprojection_errors_cam',num2str(kk),'.png'))
    
    % show the image with the checkerboard
    figure(980+kk)
    imshow(checkerboard_vids{kk}(:,:,:,imagesUsed(1)));
    hold on;
    plot(imagePoints(:,1,1), imagePoints(:,2,1),'go');
    plot(params_individual{kk}.ReprojectedPoints(:,1,1),...
        params_individual{kk}.ReprojectedPoints(:,2,1),'r+');
    legend('Detected Points','ReprojectedPoints');
    print('-dpng',strcat(savepath,'Reprojection_image_cam',num2str(kk),'.png'))
    
    hold off;
    
    
    % print the parameters
    fprintf('camera parameters \n')
    params_individual{kk}
    
end

%% get points on L frame

allimagepoints = cell(1,num_cams);
checkerboard_images_undistorted = cell(1,num_cams);
boardSize_ch_full = cell(1,num_cams);
point_coordinates_ch = cell(1,num_cams);
% keyboard
for kk = 1:num_cams
    
    % get the camera parameters
    camparams = params_individual{kk};
%     for nFrame = 1:size(lframe_image{kk},4)
        % use camparams to undistort the checkerboard iamge
    undistorted_checkerboard =  undistortImage(uint8(median(lframe_image{kk},4)),camparams);
%     undistorted_checkerboard =  undistortImage(imclose(uint8(median(lframe_image{kk},4)), strel('disk',1)),camparams);

    % find the checkerboard points
    fprintf('finding checkerboard points \n')
    [imagePoints_ch, boardSize_ch, ~] = ...
        detectCheckerboardPoints(undistorted_checkerboard,'MinCornerMetric',0.15);
    disp(boardSize_ch)
%         if ismember(6, boardSize_ch) && ismember(9, boardSize_ch)
%             break
%         end
%     end
    
    % get the L frame points
    figure(8078)
    imshow(undistorted_checkerboard);
    hold on;
    [xi,yi] = getpts ;
    
    % do a bunch of axis flipping stuff
    point_coordinates_ch{kk} = [xi yi];
    point_coordinates_ch{kk} = reshape(point_coordinates_ch{kk},[],2);
    point_coordinates_ch{kk} =point_coordinates_ch{kk}(1:4,:);
    long_axis = -(point_coordinates_ch{kk}(3,:)-point_coordinates_ch{kk}(1,:));
    short_axis = -(point_coordinates_ch{kk}(4,:)-point_coordinates_ch{kk}(1,:));
    
    detected_long_axis = -(imagePoints_ch(1,:)-imagePoints_ch(min(boardSize_ch),:));
    detected_short_axis = -(imagePoints_ch(1,:)-imagePoints_ch(min(boardSize_ch)-1,:));
    
    long_axis_dot = dot(long_axis,detected_long_axis)./(norm(long_axis)*norm(detected_long_axis));
    short_axis_dot =dot(short_axis,detected_short_axis)./(norm(short_axis)*norm(detected_short_axis));
    disp(long_axis_dot)
    disp(short_axis_dot)
    
    [~,longdim] = max(abs(long_axis));
    [~,shortdim] = max(abs(short_axis));
    pointindex = 1:((boardSize_ch(1)-1)*((boardSize_ch(2)-1)));
    pointindex = reshape(pointindex,min(boardSize_ch)-1,[]);
    
    if long_axis_dot<0
        fprintf('flipped long \n')
        pointindex = flip(pointindex,longdim);
    end
    
    if short_axis_dot<0
        fprintf('flipped short \n')
        pointindex = flip(pointindex,shortdim);
    end
    
    pointindex_unflipped = reshape(pointindex,[],1);
    %   [imagePoints_ch, boardSize_ch, imagesUsed] = ...
    %         detectCheckerboardPoints(flipped_undistorted_checkerboard,'MinCornerMetric',0.15);
    imagePoints_ch = imagePoints_ch(pointindex_unflipped,:);
    
    
    figure(8078+kk)
    imshow(undistorted_checkerboard);
    hold on;
    plot(imagePoints_ch(1,1), imagePoints_ch(1,2),'ro');
    plot(imagePoints_ch(2,1), imagePoints_ch(2,2),'bo');
    plot(imagePoints_ch(3:end,1), imagePoints_ch(3:end,2),'go');
    hold off
    allimagepoints{kk} = imagePoints_ch;
    checkerboard_images_undistorted{kk} = undistorted_checkerboard;
    boardSize_ch_full{kk} = boardSize_ch;
end
% keyboard
%% compute the world coordinates

worldOrientation = cell(num_cams,1);
worldLocation = cell(num_cams,1);
rotationMatrix = cell(num_cams,1);
translationVector = cell(num_cams,1);

for kk=1:num_cams
    [X,Y] = meshgrid(1:(max(boardSize_ch_full{kk})-1),1:(min(boardSize_ch_full{kk})-1));
    y_step = squareSize;
    x_step = squareSize;
    location3d = [(reshape(Y,[],1)-1)*y_step (reshape(X,[],1)-1)*x_step  zeros(numel(X),1)];
    
    [worldOrientation{kk},worldLocation{kk}] = estimateWorldCameraPose(double(allimagepoints{kk}),...
        double(location3d),params_individual{kk},'Confidence',95,'MaxReprojectionError',4,'MaxNumTrials',5000);
    
    [rotationMatrix{kk},translationVector{kk}] = cameraPoseToExtrinsics(worldOrientation{kk},worldLocation{kk});
    
    figure(333+kk)
    image(checkerboard_images_undistorted{kk})
    hold on
    imagePoints = worldToImage(params_individual{kk},rotationMatrix{kk},...
        translationVector{kk},double(location3d));
    plot(allimagepoints{kk}(:,1),allimagepoints{kk}(:,2),'or')
    plot(imagePoints(:,1),imagePoints(:,2),'ok')
    
    hold off
    legend('Ground truth','Checkerboard')
    print('-dpng',strcat(savepath,'camerareproject_checkerboard',num2str(kk),'.png'));
    
    figure(227)
    plotCamera('Location',worldLocation{kk},'Orientation',worldOrientation{kk},'Size',50,'Label',num2str(kk));
    hold on
    view([-91 84])
    if (kk == num_cams)
        print('-dpng',strcat(savepath,'cameraarrangement.png'));
    end
    %
    
end

%% saves data needed for dannce

for nCam = 1:num_cams
    RDistort = params_individual{nCam}.RadialDistortion;
    TDistort = params_individual{nCam}.TangentialDistortion;
    r = rotationMatrix{nCam};
    t = translationVector{nCam};
    K = params_individual{nCam}.IntrinsicMatrix;
    save(strcat(savepath,'hires_cam',num2str(nCam),'_params.mat'),'K','r','t','RDistort','TDistort')
end


return
