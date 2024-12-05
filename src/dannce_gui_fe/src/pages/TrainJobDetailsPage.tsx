import LogStream from '@/components/LogStream';
import { useTrainJobDetailsQuery } from '@/hooks';

import { useParams } from 'react-router-dom';

const TrainJobDetailsPage: React.FC = () => {
  const { id: idStr } = useParams();
  const trainJobId = parseInt(idStr!);

  const {
    data: trainJobData,
    isLoading: trainJobLoading,
    isError: trainJobError,
  } = useTrainJobDetailsQuery(trainJobId);

  if (trainJobLoading) {
    return <div>Loading</div>;
  }
  if (trainJobError || !trainJobData) {
    return <div>Error</div>;
  }

  return (
    <div>
      <h1 className="text-2xl mb-4">Train Job Details</h1>
      <h2 className="text-xl mb-2">Full Job Details</h2>
      <pre className="p-4 bg-gray-50 border rounded-md mb-4 text-wrap">
        {JSON.stringify(trainJobData, null, 2)}
      </pre>
      <h2 className="text-xl">Log File</h2>
      <LogStream slurmJobId={trainJobData.slurm_job_id} />
    </div>
  );
};

export default TrainJobDetailsPage;
