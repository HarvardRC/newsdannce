
bb = [1 2 3; 1 3 2; 2 1 3; 2 3 1; 3 2 1; 3 1 2];


kk = 1;
imagesc(checkerboard_images_undistorted{kk}); hold on;
scatter(allimagepoints{kk}(:,1),allimagepoints{kk}(:,2),[],L3D{kk}(:,2))

aip = allimagepoints{kk};
l3d = L3D{kk}; l3d(:,2) = flipud(l3d(:,2));


imagesc(checkerboard_images_undistorted{kk}); hold on;
scatter(aip(:,1),aip(:,2),[],l3d(:,2))



[worldOrientation{kk},worldLocation{kk}] = estimateWorldCameraPose(aip,l3d,params_individual{kk},'Confidence',95,'MaxReprojectionError',4,'MaxNumTrials',5000);
[rotationMatrix{kk},translationVector{kk}] = cameraPoseToExtrinsics(worldOrientation{kk},worldLocation{kk});
image(checkerboard_images_undistorted{kk})
hold on
imagePoints = worldToImage(params_individual{kk},rotationMatrix{kk},...
    translationVector{kk},double(location3d));
plot(allimagepoints{kk}(:,1),allimagepoints{kk}(:,2),'or')
plot(imagePoints(:,1),imagePoints(:,2),'ok')


for i = 1:6
    aip = double(allimagepoints{kk});
    l3d = double(L3D{kk}); l3d(:,2) = flipud(l3d(:,2)); l3d(:,3) = 0;
    l3d = l3d(:,bb(i,:));
    
    subplot(3,2,i);
    
    [worldOrientation{kk},worldLocation{kk}] = estimateWorldCameraPose(aip,l3d,params_individual{kk},'Confidence',95,'MaxReprojectionError',4,'MaxNumTrials',5000);
    
    [rotationMatrix{kk},translationVector{kk}] = cameraPoseToExtrinsics(worldOrientation{kk},worldLocation{kk});
    image(checkerboard_images_undistorted{kk})
    hold on
    imagePoints = worldToImage(params_individual{kk},rotationMatrix{kk},...
        translationVector{kk},double(l3d));
    plot(allimagepoints{kk}(:,1),allimagepoints{kk}(:,2),'or')
    plot(imagePoints(:,1),imagePoints(:,2),'ok')
end
%%
% save('params_temp.mat','params_individual','worldPoints','estimationErrors');
% 
% lframe_image = extrinsic_videos;
% for i = 1:6
% tempIm = lframe_image{i}(:,:,:,1);
% %ti = tempIm; %(500:end,400:end,:);
% ti = rgb2gray(tempIm);
% 
% 
% 
% camparams = params_individual{i};
% %     for nFrame = 1:size(lframe_image{kk},4)
%         % use camparams to undistort the checkerboard iamge
%  ti =  undistortImage(uint8(median(lframe_image{i},4)),camparams);
% [imp,bs,~] = detectCheckerboardPoints(ti,'MinCornerMetric',.4);
% try
% subplot(2,3,i); imagesc(ti); hold on; scatter(imp(:,1),imp(:,2))
% catch
% end
% end
% 
% figure(2); imagesc(lframe_image{1}(:,:,:,1))
% 
% ti = lframe_image{1}(:,:,:,1);
% 
% tim = sum(ti>100,3);
% tim2 = tim==3;
% 
% [imps,bs,~] = detectCheckerboardPoints(tim2,'MinCornerMetric',.3);
% imagesc(tim2); hold on; scatter(imps(:,1),imps(:,2));
% 
% 
% for i = 1:6
%     camparams = params_individual{i};
%     %     for nFrame = 1:size(lframe_image{kk},4)
%     % use camparams to undistort the checkerboard iamge
%     ti =  undistortImage(uint8(median(lframe_image{i},4)),camparams);
%     exIm(:,:,:,i) = ti;
% end
% 
% save('tempCal.mat','exIm');
% 
% for i = 1:6
%     subplot(2,3,i);
% imagesc(exIm(:,:,:,i)); hold on;
% exp = squeeze(a(i,:,:));
% exp2 = squeeze(b(i,:,:,:));
% scatter(exp2(:,1),exp2(:,2))
% end
