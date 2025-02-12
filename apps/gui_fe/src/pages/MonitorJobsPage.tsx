// import { listJobs } from '@/api';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  useListPredictJobsQuery,
  useListTrainJobsQuery,
  useRefreshJobsMutation,
} from '@/hooks';
import { timestampString } from '@/lib/utils';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

export default function MonitorJobs() {
  const { data: trainJobData, isLoading: trainJobLoading } =
    useListTrainJobsQuery();

  const { data: predictJobData, isLoading: predictJobLoading } =
    useListPredictJobsQuery();

  const mutation = useRefreshJobsMutation();

  if (predictJobLoading || trainJobLoading) {
    return <div>Loading...</div>;
  }
  const handleRefreshClick = () => {
    console.log('REFRESHING JOBS');
    mutation.mutate();
  };
  return (
    <>
      <TooltipProvider>
        <h1 className="text-2xl font-semibold mb-4">Training Jobs</h1>
        <Table className="mb-5">
          <TableCaption>Training Jobs</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">Job ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Command</TableHead>
              <TableHead>Runtime</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Slurm Job</TableHead>
              <TableHead>Output Weights</TableHead>
              <TableHead>Log File</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Actions </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trainJobData!.map((x) => {
              return (
                <TableRow key={x.train_job_id}>
                  <TableCell>{x.train_job_id}</TableCell>
                  <TableCell className="font-medium">
                    <Link
                      to={appPages.trainJobDetails.path.replace(
                        /:id/,
                        `${x.train_job_id}`
                      )}
                    >
                      {x.train_job_name.length > 0 ? (
                        x.train_job_name
                      ) : (
                        <i>UNNAMED</i>
                      )}
                    </Link>
                  </TableCell>
                  <TableCell>{x.mode}</TableCell>
                  <TableCell>{x.runtime_name}</TableCell>
                  <TableCell>
                    {x.runtime_type == 'SLURM'
                      ? x.slurm_status
                      : x.local_status}
                  </TableCell>
                  <TableCell>
                    {x.runtime_type == 'SLURM'
                      ? x.slurm_job_id
                      : x.local_process_id}
                  </TableCell>
                  <TableCell>{x.weights_name}</TableCell>
                  <TableCell>
                    <Tooltip>
                      <TooltipTrigger>...</TooltipTrigger>
                      <TooltipContent>{x.log_path_external}</TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{timestampString(x.created_at)}</TableCell>
                  <TableCell>
                    {/* <div className="cursor-pointer">Cancel</div> */}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <h1 className="text-2xl font-semibold mb-4">Inference Jobs</h1>
        <Table>
          <TableCaption>Inference Jobs</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">Job ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Command</TableHead>
              <TableHead>Runtime</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Slurm Job</TableHead>
              <TableHead>Video Folder</TableHead>
              <TableHead>Predictons</TableHead>
              <TableHead>Log File</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Actions </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {predictJobData!.map((x) => {
              return (
                <TableRow key={x.predict_job_id}>
                  <TableCell className="font-medium">
                    {x.predict_job_id}
                  </TableCell>
                  <TableCell className="font-medium">
                    <Link
                      to={appPages.predictJobDetails.path.replace(
                        /:id/,
                        `${x.predict_job_id}`
                      )}
                    >
                      {x.predict_job_name.length > 0 ? (
                        x.predict_job_name
                      ) : (
                        <i>UNNAMED</i>
                      )}
                    </Link>
                  </TableCell>
                  <TableCell>{x.mode}</TableCell>
                  <TableCell>{x.runtime_name}</TableCell>
                  <TableCell>
                    {x.runtime_type == 'SLURM'
                      ? x.slurm_status
                      : x.local_status}
                  </TableCell>
                  <TableCell>
                    {x.runtime_type == 'SLURM'
                      ? x.slurm_job_id
                      : x.local_process_id}
                  </TableCell>{' '}
                  <TableCell>{x.weights_name}</TableCell>
                  <TableCell>{x.prediction_name}</TableCell>
                  <TableCell>
                    <Tooltip>
                      <TooltipTrigger>...</TooltipTrigger>
                      <TooltipContent>{x.log_path_external}</TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{timestampString(x.created_at)}</TableCell>
                  <TableCell>
                    {/* <div className="cursor-pointer">Cancel</div> */}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <Button
          onClick={handleRefreshClick}
          className="max-w-40"
          variant="default"
        >
          Refresh All Jobs
        </Button>
        Note: Automatically refetches every 5 minutes
      </TooltipProvider>
    </>
  );
}
