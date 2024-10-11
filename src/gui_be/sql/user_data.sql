PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

INSERT INTO runtime VALUES(1,'olveczkygpu','olveczkygpu',30,12,12,1728489542);

-- INSERT INTO prediction VALUES(1,'predict_e70','PENDING',1,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(2,'predict02_train06','PENDING',1,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(3,'predict01','PENDING',1,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(4,'predict01','PENDING',1,'COM',1728489382);
-- INSERT INTO prediction VALUES(5,'predict_e70','PENDING',2,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(6,'predict02_train06','PENDING',2,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(7,'predict01','PENDING',2,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(8,'predict01','PENDING',2,'COM',1728489382);
-- INSERT INTO prediction VALUES(9,'predict_e70','PENDING',3,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(10,'predict02_train06','PENDING',3,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(11,'predict01','PENDING',3,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(12,'predict01','PENDING',3,'COM',1728489382);
-- INSERT INTO prediction VALUES(13,'predict_e70','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(14,'predict02_train03','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(15,'predict_e70_test','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(16,'predict02_train06','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(17,'predict01','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(18,'predict02_train04','PENDING',4,'DANNCE',1728489382);
-- INSERT INTO prediction VALUES(19,'predict02','PENDING',4,'COM',1728489382);
-- INSERT INTO prediction VALUES(20,'predict01','PENDING',4,'COM',1728489382);

INSERT INTO weights VALUES(1,'com-weights-1','/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/weights/train-com-1','COMPLETED','COM',1728489563);

-- INSERT INTO video_folder VALUES(1,'240625_143814_M5','/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5','20240808_125331_COM_Label3D_dannce.mat','20240925_181406_DANNCE_Label3D_dannce.mat',1728489382);
-- INSERT INTO video_folder VALUES(2,'240624_151330_M6','/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_151330_M6',NULL,NULL,1728489382);
-- INSERT INTO video_folder VALUES(3,'240624_155346_M7','/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_155346_M7',NULL,NULL,1728489382);
-- INSERT INTO video_folder VALUES(4,'240624_135840_M4','/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_135840_M4','20240808_125105_COM_Label3D_dannce.mat','20240925_182150_DANNCE_Label3D_dannce.mat',1728489382);

INSERT INTO train_job VALUES(1,'Train Com 1',1,50490059,1,'{"META_cwd": "/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/slurm-cwd", "META_command": "TRAIN.COM", "camnames": ["Camera1", "Camera2", "Camera3", "Camera4", "Camera5", "Camera6"], "n_instances": 1, "n_channels_out": 1, "downfac": 8, "n_channels_in": 3, "raw_im_h": 1200, "raw_im_w": 1920, "train_mode": "new", "num_validation_per_exp": 2, "batch_size": 4, "epochs": 1, "lr": 5e-05, "metric": [], "loss": {"MSELoss": {"loss_weight": 1.0}}, "save_period": 5, "max_num_samples": "max", "io_config": "./io.yaml", "crop_height": [0, 1152], "crop_width": [0, 1920], "com_train_dir": "/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/weights/train-com-1", "com_exp": [{"label3d_file": "/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5/20240808_125331_COM_Label3D_dannce.mat"}, {"label3d_file": "/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_135840_M4/20240808_125105_COM_Label3D_dannce.mat"}]}',1728489563);

INSERT INTO slurm_job VALUES(50490059,'COMPLETED','/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/logs/%j.out',1728489563);

INSERT INTO train_job_video_folder VALUES(1,1);
INSERT INTO train_job_video_folder VALUES(1,4);

COMMIT;
