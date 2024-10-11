-- load demo data for testing 

INSERT INTO runtime 
    (
        name,  partition_list, memory_gb, time_hrs, n_cpus
    ) VALUES 
        ('DEMO_bigmem_train', 'gpu', 150, 72, 16),
        ('DMEO_olveczkygpu', 'olveczkygpu', 50, 72, 16)
;


INSERT INTO video_folder
    (
        name,
        path
    ) VALUES 
    (
        'Wk 2 Day 2 M5',
        '/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5'
    ),
    (
        'Wk 2 Day 3 M6',
        '/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day3_wk2/240626_130941_M6'
    ),
        (
        'Wk 2 Day 2 M4',
        '/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_140208_M4'
    ),
    (
        'Wk 2 Day 2 M7',
        '/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_160541_M7'
    )
;


INSERT INTO weights 
    (name, path, status, mode) VALUES
    ('com-checkpoint-epoch20', '/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/models/com/com-checkpoint-epoch20.pth', 'PENDING', 'COM'),
    ('com-checkpoint-epoch80', '/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/models/dannce/dannce-checkpoint-epoch80.pth', 'PENDING', 'DANNCE'),
    ('com-new-1','/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/models/com/new-com1.pth', 'PENDING', 'COM'),
    ('com-new-2','/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/models/com/new-com2.pth', 'PENDING', 'COM');


INSERT INTO train_job
        -- video folders MANY:MANY are specified by table "train_job_video_folder"
    ( name, runtime, weights) VALUES 
    (
        'Train COM #1',
        1,
        2
    ),
    (
        'Train DANNCE #1',
        2,
        3
    )
;


INSERT INTO predict_job
    (
        name,
        video_folder,
        weights,
        runtime
    ) VALUES 
    (
        'Predict COM #1',
        1,
        1,
        1
    ),
    (
        'Predict COM #2',
        2,
        1,
        1
    ),
    (
        'Predict DANNCE #1',
        1,
        1,
        2
    )
;

INSERT INTO train_job_video_folder 
    (train_job, video_folder) VALUES 
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 1),
    (2, 4)
    ;

-- create dummy slurm jobs
INSERT INTO slurm_job
    (slurm_job_id, stdout_file, status) VALUES
    (1000001, './out/file1', 'PENDING'),
    (1000002, './out/file2', 'PENDING'),
    (1000003, './out/file3', 'PENDING'),
    (49462389, null, 'PENDING')
    ;

--  connect slurm jobs with train_job, predict_job
UPDATE predict_job SET slurm_job=1000001 WHERE id=1;

UPDATE predict_job SET slurm_job=1000002 WHERE id=2;

UPDATE train_job SET slurm_job=1000003 WHERE id=1;

UPDATE train_job SET slurm_job=49462389 WHERE id=2;
