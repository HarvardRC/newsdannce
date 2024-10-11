import { BASE_API_URL, BASIC_AUTH_TOKEN } from './config';
import { DannceMode } from './constants';
// import secrets_json from './secrets.json';

export function make_url(...segments: string[]) {
  /** Make url from segments: e.g "foo", "bar" => foobar */
  segments = segments.map((x) => x.replace(/\/?(.+?)\/?/, '$1'));
  return segments.join('/');
}

export async function post(route: string, data: object = {}) {
  const full_url: string = make_url(BASE_API_URL, route);
  const response = await fetch(full_url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return await response.json();
}

export async function get(route: string) {
  const full_url: string = make_url(BASE_API_URL, route);

  const response = await fetch(full_url, {
    method: 'GET',
    headers: {},
  });
  return await response.json();
}

export async function getFile(route: string) {
  const full_url: string = make_url(BASE_API_URL, route);

  const response = await fetch(full_url, {
    method: 'GET',
    headers: {
      'Cache-Control': 'no-cache',
    },
  });
  if (response.status == 200) {
    return await response.text();
  } else {
    throw Error('Non-200 response returned');
  }
}

//  SPECIFIC ROUTES

type CreateRuntimeData = {
  name: string;
  partiton_list: string;
  memory_gb: number;
  time_hrs: number;
  n_cpus: number;
};

export async function createRuntime(data: CreateRuntimeData) {
  post('/runtime/', data);
}

type ListRuntimesData = {
  id: number;
  name: string;
  partition_list: string;
  memory_gb: number;
  time_hrs: number;
  n_cpus: number;
}[];

export async function listRuntimes(): Promise<ListRuntimesData> {
  return get('/runtime/list');
}

type TrainFolder = {
  name: string;
  path: string;
};

type ListTrainingFolder = {
  id: number;
  name: string;
  path: string;
  has_model: number; // boolean False=0; 1=True
  mode: DannceMode;
  created_at: number;
}[];

export async function listTrainingFolders(): Promise<ListTrainingFolder> {
  return get('/training_folder/list');
}

type ListVideoFolder = {
  id: number;
  name: string;
  path: string;
  created_at: number;
  com_labels_file?: string;
  dannce_labels_file?: string;
}[];

export async function listVideoFolders(): Promise<ListVideoFolder> {
  return get('/video_folder/list');
}

// type VideoFolder = {
//   name: string;
//   path: string;
// };

// type TrainJobType = {
//   id: number;
//   config_file: string;
//   name: string;
//   mode: DannceMode;
//   training_folder: TrainFolder;
//   video_folders: VideoFolder[];
// };

// type PredictJobType = {
//   id: number;
//   config_file: string;
//   name: string;
//   mode: DannceMode;
//   training_folder: TrainFolder | null;
//   video_folder: VideoFolder;
// };

type VideoFolderDetails = {
  id: number;
  name: string;
  path: string;
  created_at: number;
  com_labels_file?: string;
  dannce_labels_file?: string;
  label_files: {
    n_cameras: number;
    n_frames: number;
    n_joints: number;
    params: {
      K: [
        [number, number, number],
        [number, number, number],
        [number, number, number]
      ];
      r: [
        [number, number, number],
        [number, number, number],
        [number, number, number]
      ];
      t: [[number, number, number]];
      RDistort: [[number, number]];
      TDistort: [[number, number]];
    };
  }[];
  predict_jobs: any[];
  prediction_data: any[];
};

export async function videoFolderDetails(
  id: number
): Promise<VideoFolderDetails> {
  if (isNaN(id)) throw new Error('Video folder ID is not a number');
  return get(`/video_folder/${id}`);
}

type MakeVideoFolderData = {
  name: string;
  path: string;
  com_data_file?: string;
  dannce_data_file?: string;
};

export async function makeVideoFolder(
  data: MakeVideoFolderData
): Promise<void> {
  return post('/video_folder/', data);
}

type MakeRuntimeData = {
  name: string;
  partition_list: string;
  memory_gb: number;
  time_hrs: number;
  n_cpus: number;
};

export async function makeRuntime(data: MakeRuntimeData): Promise<void> {
  return post('/runtime/', data);
}

type ListPredictJobsType = {
  predict_job_id: number;
  predict_job_name: string;
  stdout_file: string;
  mode: 'COM' | 'DANNCE';
  status: string;
  prediction_id: string;
  prediction_name: string;
  // prediction_path: string;
  weights_id: string;
  weights_name: string;
  // weights_path: string;
  video_folder_id: number;
  video_folder_name: string;
  // video_folder_path: string;
  slurm_job_id: number;
  runtime_id: number;
  created_at: number;
}[];

export async function listPredictJobs(): Promise<ListPredictJobsType> {
  return get('/predict_job/list');
}

type ListTrainJobsType = {
  slurm_job_id: number;
  stdout_file: string | null;
  mode: 'COM' | 'DANNCE';
  status: string;
  train_job_id: number;
  train_job_name: string;
  runtime_id: number;
  weights_id: number;
  weights_name: string;
  // weights_path: string;
  created_at: number;
}[];

export async function listTrainJobs(): Promise<ListTrainJobsType> {
  return get('/train_job/list');
}

type ListPredictionsType = {
  prediction_name: string;
  prediction_id: number;
  prediction_path: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED';
  video_folder_id: number;
  mode: 'COM' | 'DANNCE';
  created_at: number;
}[];
export async function listPredictions(): Promise<ListPredictionsType> {
  return get('/prediction/list');
}

type SubmitComTrainJobData = {
  name: string;
  video_folder_ids: number[];
  output_model_name: string;
  config: string;
  epochs: number;
  vol_size: number;
  runtime_id: number;
};

export async function submitComTrainJob(
  data: SubmitComTrainJobData
): Promise<void> {
  return post('/train_job/submit_com', data);
}

type SubmitComPredictJobData = {
  name: string;
  prediction_name: string;
  video_folder_id: number;
  weights_id: number;
  config: string;
  runtime_id: number;
};

export async function submitComPredictJob(
  data: SubmitComPredictJobData
): Promise<void> {
  return post('/predict_job/submit_com', data);
}

export async function refreshJobs(): Promise<void> {
  return post('/jobs_common/update-live-jobs', {});
}

type PredictJobDetailsType = {
  name: string;
  weights_id: number;
  weights_path: string;
  weights_status: 'PENDING' | 'COMPLETED' | 'FAILED';
  config: object;
  mode: 'DANNCE' | 'COM';
  video_folder_id: number;
  video_folder_name: string;
  video_folder_path: string;
  prediction_id: number;
  prediction_name: string;
  prediction_path: string;
  runtime_id: number;
  runtime_name: string;
  slurm_job_id: number;
  slurm_job_status: string;
  stdout_file: string;
};
export async function getPredictJobDetails(
  predictJobId: number
): Promise<PredictJobDetailsType> {
  return get(`/predict_job/${predictJobId}`);
}

type TrainJobDetailsType = {
  name: string;
  weights_id: number;
  weights_path: string;
  weights_status: 'PENDING' | 'COMPLETED' | 'FAILED';
  config: object;
  mode: 'DANNCE' | 'COM';
  video_folders: {
    id: number;
    name: string;
    path: string;
  }[];
  runtime_id: number;
  runtime_name: string;
  slurm_job_id: number;
  slurm_job_status: string;
  stdout_file: string;
};
export async function getTrainJobDetails(
  trainJobId: number
): Promise<TrainJobDetailsType> {
  return get(`/train_job/${trainJobId}`);
}

export async function getSlurmLogfile(slurmJobId: number): Promise<any> {
  return getFile(`/jobs_common/get_log/${slurmJobId}`);
}

type ListWeightsData = {
  id: number;
  name: string;
  path: string;
  status: 'COMPLETED' | 'FAILED' | 'PENDING';
  mode: 'COM' | 'DANNCE';
  created_at: number;
}[];

export async function listWeights(): Promise<ListWeightsData> {
  return get('/weights/list');
}
