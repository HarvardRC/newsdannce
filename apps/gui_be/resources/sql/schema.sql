DROP TABLE IF EXISTS runtime;
DROP TABLE IF EXISTS video_folder;
DROP TABLE IF EXISTS train_job;
DROP TABLE IF EXISTS prediction;
DROP TABLE IF EXISTS predict_job;
DROP TABLE IF EXISTS gpu_job;
DROP TABLE IF EXISTS weights;
-- many:many relationship table
DROP TABLE IF EXISTS train_job_video_folder;
-- single row table for global settings
DROP TABLE IF EXISTS global_state;

CREATE TABLE runtime (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    partition_list TEXT,
    runtime_type TEXT NOT NULL CHECK (runtime_type IN ('LOCAL', 'SLURM')) DEFAULT 'SLURM',
    memory_gb INTEGER,
    time_hrs INTEGER,
    n_cpus INTEGER,
    n_gpus INTEGER,
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

-- predicted COM or DANNCE data
CREATE TABLE prediction (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL, --human readible name
    path TEXT NOT NULL UNIQUE, --path to the prediction folder
    src_path TEXT, --path where the video was imported from (if relevant)
    status TEXT DEFAULT 'PENDING'
        CHECK(status IN (
            'PENDING', 'COMPLETED','FAILED')),
    video_folder INTEGER REFERENCES video_folder(id), -- predictions are associated with a video folder
    mode TEXT NOT NULL CHECK (mode IN ('COM', 'DANNCE', 'SDANNCE')),
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

-- trained dannce model
CREATE TABLE weights (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL, --human readible name of weights (ie "output-model-name")
    path TEXT NOT NULL UNIQUE, -- path to the folder containing a checkpoint-final.pth
    src_path TEXT, --path where the video was imported from (if relevant)
    status TEXT DEFAULT 'PENDING'
        CHECK(status IN (
            'PENDING', 'COMPLETED','FAILED')),
    mode TEXT NOT NULL CHECK (mode IN ('COM', 'DANNCE', 'SDANNCE')),
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

-- store details of a data folder (single recording)
CREATE TABLE video_folder (
id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    path TEXT UNIQUE, --path to folder containing videos directory
    src_path TEXT, --path where the video was imported from
    com_labels_file TEXT, --path to dannce.mat file with COM labels
    dannce_labels_file TEXT, -- path to dannce.mat file with DANNCE labels
    current_com_prediction REFERENCES prediction(id),
    calibration_params JSON,
    camera_names JSON DEFAULT '["Camera1","Camera2","Camera3","Camera4","Camera5","Camera6"]',
    video_width INTEGER DEFAULT 1920,
    video_height INTEGER DEFAULT 1200,
    n_cameras INTEGER DEFAULT 6,
    n_animals INTEGER DEFAULT 1,
    n_frames INTEGER DEFAULT 30000,
    duration_s FLOAT DEFAULT 1800,
    fps FLOAT DEFAULT 50,
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

CREATE TABLE train_job (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    weights INTEGER REFERENCES weights(id), -- output weights resource
    gpu_job INTEGER REFERENCES gpu_job(id),
    runtime INTEGER REFERENCES runtime(id),
    config JSON,
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

CREATE TABLE predict_job (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    -- prediction INTEGER REFERENCES prediction()
    weights INTEGER REFERENCES weights(id), -- input weights resource used for predictions
    prediction INTEGER REFERENCES prediction(id), -- ouptut prediction resource
    video_folder INTEGER REFERENCES video_folder(id),
    gpu_job INTEGER REFERENCES gpu_job(id),
    runtime INTEGER REFERENCES runtime(id),
    config JSON,
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now'))
);

-- store details of a single running job
CREATE TABLE gpu_job (
    id INTEGER PRIMARY KEY NOT NULL,
    log_path TEXT,
    -- job_type TEXT NOT NULL CHECK (job_type IN ('LOCAL', 'SLURM')) DEFAULT 'SLURM',
    created_at INTEGER DEFAULT (STRFTIME('%s', 'now')),
    -- SLURM JOB FIELDS
    slurm_job_id INTEGER,
    slurm_status TEXT
        CHECK(slurm_status IS NULL OR slurm_status IN (
            'CANCELLED','COMPLETED','COMPLETING','FAILED','NODE_FAIL',
            'OUT_OF_MEMORY','PENDING','PREEMPTED','RUNNING',
            'SUSPENDED','STOPPED','TIMEOUT',
            'LOST_TO_SLURM' -- custom status meaning the job could not be fetched from slurm
            )),
    -- LOCAL JOB FIELDS
    local_status TEXT CHECK (local_status IS NULL OR local_status IN ('QUEUEUD','RUNNING','FAILED',"COMPLETED")),
    local_process_id INTEGER
);

CREATE TABLE train_job_video_folder (
    train_job INTEGER NOT NULL REFERENCES train_job(id) ON DELETE CASCADE,
    video_folder INTEGER NOT NULL REFERENCES video_folder(id) ON DELETE CASCADE,
    PRIMARY KEY(train_job, video_folder)
);

-- table continaing database metadata
CREATE TABLE global_state (
    id INTEGER PRIMARY KEY CHECK (id=0),
    last_update_jobs INTEGER DEFAULT 0,
    skeleton_file TEXT DEFAULT null
);

-- Create singleton row entry in global_state for storing settings
INSERT INTO global_state (id) VALUES (0);
