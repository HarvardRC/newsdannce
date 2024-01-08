function [params_individual] = calibrate_cameras_intrinsic(checkerboard_vids, squareSize, savepath)

num_cams = numel(checkerboard_vids);

% get intrinsic parameters for each camera
parfor kk = 1:num_cams

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


return