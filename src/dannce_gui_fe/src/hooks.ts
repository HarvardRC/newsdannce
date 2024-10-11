import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listRuntimes,
  listTrainingFolders,
  listVideoFolders,
  makeVideoFolder,
  videoFolderDetails,
  listPredictJobs,
  listTrainJobs,
  makeRuntime,
  submitComTrainJob,
  refreshJobs,
  getPredictJobDetails,
  getTrainJobDetails,
  getSlurmLogfile,
  submitComPredictJob,
  listWeights,
  listPredictions,
} from './api';

/* #######################
 *         QUERIES
 * ###################∂###*/

export function useListRuntimesQuery() {
  return useQuery({
    queryKey: ['listRunntimes'],
    // TODO: add query FN
    queryFn: listRuntimes,
  });
}

export function usePredictJobDetailsQuery(predictJobId: number) {
  return useQuery({
    queryKey: ['predictJobDetails', predictJobId],
    queryFn: () => getPredictJobDetails(predictJobId),
  });
}
export function useTrainJobDetailsQuery(trainJobId: number) {
  return useQuery({
    queryKey: ['trainJobDetails', trainJobId],
    queryFn: () => getTrainJobDetails(trainJobId),
  });
}

export function useListPredictJobsQuery() {
  return useQuery({
    queryKey: ['listPredictJobs'],
    // TODO: add query FN
    queryFn: listPredictJobs,
  });
}

export function useListTrainJobsQuery() {
  return useQuery({
    queryKey: ['listTrainJobs'],
    // TODO: add query FN
    queryFn: listTrainJobs,
  });
}

export function useListPredictionsQuery() {
  return useQuery({
    queryKey: ['listPredictions'],
    // TODO: add query FN
    queryFn: listPredictions,
  });
}
export function useListWeightsQuery() {
  return useQuery({
    queryKey: ['listWeights'],
    queryFn: listWeights,
  });
}

export function useListTrainingFoldersQuery() {
  return useQuery({
    queryKey: ['listTrainingFolders'],
    // TODO: add query FN
    queryFn: listTrainingFolders,
  });
}

export function useListVideoFoldersQuery() {
  return useQuery({
    queryKey: ['listVideoFolders'],
    // TODO: add query FN
    // queryFn: listPredictJobs,
    queryFn: listVideoFolders,
  });
}

export function useVideoFolderDetailsQuery(videoFolderId: number) {
  return useQuery({
    queryKey: ['videoFolder', videoFolderId],
    // TODO: add query FN
    // queryFn: listPredictJobs,
    queryFn: () => {
      return videoFolderDetails(videoFolderId);
    },
  });
}

export function useSlurmLogfileQuery(slurmJobId: number) {
  return useQuery({
    queryKey: ['SlurmLogfile', slurmJobId],
    retry: false,
    // TODO: add query FN
    // queryFn: listPredictJobs,
    queryFn: () => {
      return getSlurmLogfile(slurmJobId);
    },
  });
}

/* #######################
 *        MUTATIONS
 * ###################∂###*/

export function useMakeVideoFolderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: makeVideoFolder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listVideoFolders'] });
    },
  });
}

export function useMakeRuntimeMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: makeRuntime,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listVideoFolders'] });
    },
  });
}

export function useSubmitComTrainJobMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitComTrainJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listTrainJobs'] });
    },
  });
}

export function useRefreshJobsMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: refreshJobs,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listTrainJobs'] });
      queryClient.invalidateQueries({ queryKey: ['listPredictJobs'] });
    },
  });
}

export function useSubmitComPredictJobMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitComPredictJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listPredictJobs'] });
    },
  });
}
