-- remove existing tables if they exist
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS jobs;

-- create a new table for 
CREATE TABLE job (
    job_id INTEGER PRIMARY KEY NOT NULL,
    sdannce_command TEXT NOT NULL
        CHECK(sdannce_command IN (
            'train com',
            'train dannce',
            'predict com',
            'predict dannce'
        )),
    status TEXT NOT NULL
        CHECK(status IN (
            'PENDING',
            'RUNNING',
            'COMPLETED',
            'FAILED'
        )) DEFAULT 'PENDING',
    -- unix seconds since epoch
    created_at INTEGER NOT NULL,
    project_folder TEXT NOT NULL,
    stdout_file TEXT
);
