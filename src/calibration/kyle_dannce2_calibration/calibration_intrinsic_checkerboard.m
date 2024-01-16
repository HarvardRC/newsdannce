%% Find the camera intrinsic parameters
% Input Parameters
clear
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
numcams = 6;
videoName = '0';
ext = '.mp4';
squareSize = 10.0; % Size of Checkerboard squares in mm
maxNumImages = 750;

% Give initial estimates for intrinsic matrix and radial distortion
K0 = [1700, 0, 0; ...
    0, 1700, 0; ...
    600, 500, 1];
RDistort0 = [-0.1 0.5];

error_thresh = 0.5; % max reprojection error in pixels

for f = 1:numel(recdirs)
    % Run Automated Checkerboard Frame Detection
    [params_individual,estimationErrors,imagePoints,boardSize,imagesUsed,imageNums] = deal(cell(1,numcams));
    basedir = fullfile(basedrive, recdirs{f}, 'video', 'calibration', 'intrinsic');

    clear video_temp
    for kk = 1:numcams
        tic
        
        % Initialize video reader
        viddir = fullfile(basedir, ['Camera' num2str(kk)]);
        vidname = [videoName ext];
        video_temp = VideoReader(fullfile(viddir,vidname), 'CurrentTime',0);
        maxFrames = floor(video_temp.FrameRate * video_temp.Duration);
        
        % Read frames from the video to memory
        video_base = cell(maxFrames,1);
        cnt = 1;
        while hasFrame(video_temp)
            video_base{cnt} = readFrame(video_temp,'native');
            cnt = cnt + 1;
        end
        clear video_temp
        
        % Detect checkerboard points in each frame
        num2use = length(video_base);
        imUse = floor(linspace(1,length(video_base),num2use));
        fprintf('finding checkerboard points for view %i \n', kk)
        [pts, board, imageLog] = detectCheckerboardPointsPar(cat(4,video_base{imUse}));
        
        % Get the 2D ground truth coordinates for the checkerboard points
        worldPoints = generateCheckerboardPoints(board,squareSize);
        
        % Partition sample of images used to estimate intrinsics
        imagesUsedTemp = find(imageLog);
        numImagesToUse = min([maxNumImages numel(imagesUsedTemp)]);
        [~,imageNum] = datasample(imagesUsedTemp, numImagesToUse, 'Replace',false);
        imageNum = sort(imageNum, 'ascend');
        disp(['Images used for view ' num2str(kk) ': ' num2str(numel(imageNum))]);
        imageSize = [size(video_base{1},1),size(video_base{1},2)];
        
        [params,~,errors] = estimateCameraParametersPar( ...
            pts(:,:,imageNum), ...
            worldPoints, ...
            'ImageSize',imageSize, ...
            'EstimateSkew',false, ...
            'EstimateTangentialDistortion',false, ...
            'NumRadialDistortionCoefficients',2);
        
        % Estimate params again if any errors above threshold
        ind2remove = any(errors.ExtrinsicsErrors.TranslationVectorsError >= error_thresh,2);
        if any(ind2remove)
            imageNum = imageNum(~ind2remove);
            disp(['Images used for view ' num2str(kk) ': ' num2str(numel(imageNum))]);

            [params,~,errors] = estimateCameraParametersPar( ...
                pts(:,:,imageNum), ...
                worldPoints, ...
                'ImageSize',imageSize, ...
                'EstimateSkew',false, ...
                'EstimateTangentialDistortion',false, ...
                'NumRadialDistortionCoefficients',2);
        end

        % Display intrinsic matrix
        disp(params.Intrinsics)
        disp(params.Intrinsics.K)
        
        % Display errors (re-run camera if any values or undistorted images abnormal)
        disp(errors.IntrinsicsErrors)
        disp('Extrinsic errors:')
        disp(mean(abs(errors.ExtrinsicsErrors.RotationVectorsError)))
        disp(mean(abs(errors.ExtrinsicsErrors.TranslationVectorsError)))
        toc

        save(fullfile(viddir, 'cam_intrinsics.mat'),'params','errors','pts','board','imageLog','imageNum');
    end

    % Save the camera parameters for all cameras
    for kk = 1:numcams
        viddir = fullfile(basedir, ['Camera' num2str(kk)]);
        load(fullfile(viddir, 'cam_intrinsics.mat'))
        params_individual{kk} = params;
        estimationErrors{kk} = errors;
        imagePoints{kk} = pts;
        boardSize{kk} = board;
        imagesUsed{kk} = imageLog;
        imageNums{kk} = imageNum;
    end
    save(fullfile(basedir, 'cam_intrinsics.mat'),'params_individual','imagePoints','boardSize','imagesUsed','imageNums');
end

% View Undistorted Images
basedir = fullfile(basedrive, recdirs{1}, 'video', 'calibration', 'intrinsic');
load( fullfile(basedir, 'cam_intrinsics.mat') )
numcams = 6;
videoName = '0';
ext = '.mp4';
for kk = 1:numcams
    imFiles1 = VideoReader( fullfile(basedir, ['Camera' num2str(kk)], [videoName ext]), 'CurrentTime',0); 
    figure(kk);
    im = readFrame(imFiles1,'native');
    
    subplot(121); 
    title('Distorted')
    imshow(im); 
    
    subplot(122);
    title('Undistorted');
    imshow(undistortImage(im, params_individual{kk}, 'OutputView','full')); 
end

%% Visualize Preprojections
f = 1;
basedir = fullfile(basedrive, recdirs{f}, 'video', 'calibration', 'intrinsic');
cd(basedir)
load('cam_intrinsics.mat')
for kk = 1:numcams
    video_temp = VideoReader( fullfile(basedir, ['Camera' num2str(kk)], [videoName ext]) );    
    maxframes = floor(video_temp.FrameRate * video_temp.Duration);
    video_base = cell(maxframes,1);
    cnt = 1;
    while hasFrame(video_temp)
        video_base{cnt} = readFrame(video_temp, 'native');
        cnt = cnt + 1;
    end
    
    clear M
    figure;
%     imagesUsed_ = find(imagesUsed{kk});
    imagesUsed_ = imageNums{kk};
    imagesUsedFull_ = find(imagesUsed{kk});
    imagesUsedFull_ = imagesUsedFull_(imagesUsed_);
    
    for im2use = 1:numel(imagesUsed_)
        imUsed = imagesUsed_(im2use);
        imDisp = imagesUsedFull_(im2use);
        pts = imagePoints{kk}(:,:,imUsed);
        repro = params_individual{kk}.ReprojectedPoints(:,:,im2use);
        imagesc(video_base{imDisp});colormap(gray)
        hold on;
        plot(pts(:,1),pts(:,2),'or');
        plot(repro(:,1),repro(:,2),'xg');
        drawnow;
        M(im2use) = getframe(gcf);
    end
    
    % write reproject video
    %vidfile = [basedir 'reproject_view' num2str(kk) '.mp4'];
    %vk = VideoWriter(vidfile);
    %vk.Quality = 100;
    %open(vk)
    %writeVideo(vk,M);
    %close(vk);
    
end
