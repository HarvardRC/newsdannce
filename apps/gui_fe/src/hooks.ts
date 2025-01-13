import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listRuntimes,
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
  importVideoFolders,
  getPredictionDetails,
  previewPrediction,
  submitDannceTrainJob,
  submitDanncePredictJob,
} from './api';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';

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
    queryFn: listPredictJobs,
    refetchInterval: 60_000, // refetch every 60 seconds
  });
}

export function usePredictionDetailsQuery(predictionId: number) {
  return useQuery({
    queryKey: ['predictionDetails', predictionId],
    queryFn: () => getPredictionDetails(predictionId),
    // enabled: false,
  });
}

export function useListTrainJobsQuery() {
  return useQuery({
    queryKey: ['listTrainJobs'],
    queryFn: listTrainJobs,
    refetchInterval: 60_000, // refetch every 60 seconds
  });
}

export function useListPredictionsQuery() {
  return useQuery({
    queryKey: ['listPredictions'],
    queryFn: listPredictions,
  });
}
export function useListWeightsQuery() {
  return useQuery({
    queryKey: ['listWeights'],
    queryFn: listWeights,
  });
}

export function useListVideoFoldersQuery() {
  return useQuery({
    queryKey: ['listVideoFolders'],
    queryFn: listVideoFolders,
  });
}

export function useVideoFolderDetailsQuery(videoFolderId: number) {
  return useQuery({
    queryKey: ['videoFolder', videoFolderId],
    queryFn: () => {
      return videoFolderDetails(videoFolderId);
    },
  });
}

export function useSlurmLogfileQuery(slurmJobId: number) {
  return useQuery({
    queryKey: ['slurmLogfile', slurmJobId],
    retry: false,
    queryFn: () => {
      return getSlurmLogfile(slurmJobId);
    },
  });
}

export function usePreviewPredictionQuery(
  predictionId: number,
  frames: number[],
  cameraName1: string,
  cameraName2: string
) {
  return useQuery({
    queryKey: [
      'previewPrediction',
      predictionId,
      frames,
      cameraName1,
      cameraName2,
    ],
    retry: false,
    // enabled: false,
    queryFn: () => {
      return previewPrediction(predictionId, frames, cameraName1, cameraName2);
    },
  });
}

/* #######################
 *        MUTATIONS
 * #######################*/

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
export function useSubmitDannceTrainJobMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitDannceTrainJob,
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

export function useSubmitDanncePredictJobMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitDanncePredictJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listPredictJobs'] });
    },
  });
}

export function useImportVideoFoldersMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: importVideoFolders,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listVideoFolders'] });
    },
  });
}

/* #######################
 *   OTHER CUSTOM HOOKS
 * #######################*/

export function useWindowSize() {
  // Returns a state variable which update (& triggers rerender) on window resize
  const [size, setSize] = useState([0, 0]);
  useLayoutEffect(() => {
    function updateSize() {
      setSize([window.innerWidth, window.innerHeight]);
    }
    window.addEventListener('resize', updateSize);
    updateSize();
    return () => window.removeEventListener('resize', updateSize);
  }, []);
  return size;
}

export function useDebounce<T>(value: T, delayInMs = 500) {
  // Debounce - updates returned value (debouncedValue) only after delayInMs milliseconds
  // after last value update
  const [debouncedValue, setDebouncedValue] = useState<T | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    timerRef.current = setTimeout(() => setDebouncedValue(value), delayInMs);

    return () => {
      clearTimeout(timerRef.current!);
    };
  }, [value, delayInMs]);

  return debouncedValue;
}
