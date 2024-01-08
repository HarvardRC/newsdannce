function [rotationMatrix, translationVector] = calibrate_cameras_extrinsic2(lframe_image, params_individual, savePath)
% LFrame_coordinates - the x y z coords of each L frame point
num_cams = numel(lframe_image);
allimagepoints = cell(1,num_cams);
checkerboard_images_undistorted = cell(1,num_cams);
boardSize_ch_full = cell(1,num_cams);
L3D = cell(1,num_cams);

% Undistort the images
[s1,s2,~,~] = size(lframe_image{1});
undistortedIms = uint8(zeros(s1,s2,3,num_cams));
for i = 1:num_cams
    camparams = params_individual{i};
    medianImage = uint8(median(lframe_image{i},4));
    undistortedIms(:,:,:,i) = undistortImage(medianImage, camparams);
end

% Plot the images
figure;
for i = 1:num_cams
    subplot(2,3,i);
    imshow(undistortedIms(:,:,:,i))
end

% save(tempFile,'undistortedIms');
% Detect the checkerboard points
% load(tempFile2,'objPoints','imgPoints');
[imgPoints, boardSize, objPoints] = deal(cell(num_cams,1));

for n_cam = 1:num_cams
    ax = subplot(2, 3, n_cam); hold on;
    im = undistortedIms(:,:,:,n_cam);
%     im = uint8(imbinarize(rgb2gray(undistortedIms(:,:,:,n_cam)),'adaptive','Sensitivity',.2))*255;
    imshow(im)
    [imgPoints{n_cam}, boardSize{n_cam}] = detectCheckerboardPoints(im,'MinCornerMetric',.05);
    disp(size(imgPoints{n_cam}))
    scatter(ax, imgPoints{n_cam}(:,1), imgPoints{n_cam}(:,2),'.')
end

keyboard
for n_cam = 1:num_cams
    pIds = squeeze(objPoints(n_cam,:,:));
    imagePoints_ch = squeeze(imgPoints(n_cam,:,:,:));
    boardSize_ch_full{n_cam} = max(pIds(:,1:2));
    allimagepoints{n_cam} = imagePoints_ch;
   
    % We need to have the x axis be the short axis, and the y axis be the
    % long axis if we want the z-axis to be positive pointing upward.
    % (right-hand rule) This is different than what is on the checkerboard
    % pattern. 
    L3D{n_cam} = pIds(:, [2 1 3]);
    checkerboard_images_undistorted{n_cam} = undistortedIms(:,:,:,n_cam)./255;
end

% Compute the world coordinates
worldOrientation = cell(num_cams,1);
worldLocation = cell(num_cams,1);
rotationMatrix = cell(num_cams,1);
translationVector = cell(num_cams,1);

for n_cam=1:num_cams
     [worldOrientation{n_cam},worldLocation{n_cam}] = estimateWorldCameraPose2(double(allimagepoints{n_cam}),...
        double(L3D{n_cam}),params_individual{n_cam},'Confidence',95,'MaxReprojectionError',4,'MaxNumTrials',5000);

    [rotationMatrix{n_cam},translationVector{n_cam}] = cameraPoseToExtrinsics(worldOrientation{n_cam},worldLocation{n_cam});
    
    % Plot to verify
    figure(1); subplot(3,2,n_cam)
    image(checkerboard_images_undistorted{n_cam})
    hold on
    imagePoints = worldToImage(params_individual{n_cam},rotationMatrix{n_cam},...
        translationVector{n_cam},double(L3D{n_cam}));
    plot(allimagepoints{n_cam}(:,1),allimagepoints{n_cam}(:,2),'or')
    plot(imagePoints(:,1),imagePoints(:,2),'ok')
    
    figure(1)
    plotCamera('Location',worldLocation{n_cam},'Orientation',worldOrientation{n_cam},'Size',100,'Label',num2str(n_cam));
    hold on
    view([-91 84])
    if (n_cam == num_cams)
        print('-dpng',strcat(savePath,'cameraarrangement.png'));
    end
    xlabel('x')
    ylabel('y')
    figure(2)
    plotCamera('Location',worldLocation{n_cam},'Orientation',worldOrientation{n_cam},'Size',100,'Label',num2str(n_cam));
    hold on
    xlabel('x')
    ylabel('y')
    if (n_cam == num_cams)
        print('-dpng',strcat(savePath,'cameraarrangement.png'));
    end
end
