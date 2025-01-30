import LogStream from '@/components/LogStream';
import { usePredictJobDetailsQuery } from '@/hooks';
import { useParams } from 'react-router-dom';
const PredictJobDetailsPage: React.FC = () => {
  const { id: idStr } = useParams();
  const predictJobId = parseInt(idStr!);

  const {
    data: predictJobData,
    isLoading: predictJobLoading,
    isError: predictJobError,
  } = usePredictJobDetailsQuery(predictJobId);

  if (predictJobLoading) {
    return <div>Loading</div>;
  }
  if (predictJobError || !predictJobData) {
    return <div>Error</div>;
  }

  return (
    <div>
      <h1 className="text-2xl mb-4">Predict Job Details</h1>
      <h2 className="text-xl mb-2">Full Job Details</h2>
      <pre className="p-4 bg-gray-50 border rounded-md mb-4">
        {JSON.stringify(predictJobData, null, 2)}
      </pre>
      <h2 className="text-xl">Log File</h2>
      <LogStream gpuJobId={predictJobData.gpu_job_id} />
    </div>
  );
};

export default PredictJobDetailsPage;
