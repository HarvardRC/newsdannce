import { useWeightsDetailsQuery } from '@/hooks';
import { useParams } from 'react-router-dom';

type CustomProps = {};

const WeightsDetailsPage: React.FC<CustomProps> = () => {
  const { id: idStr } = useParams();
  const id = parseInt(idStr!);
  const { data, isLoading, isError } = useWeightsDetailsQuery(id);

  if (isLoading) {
    return <div>Loading</div>;
  }
  if (isError) {
    return <div> error</div>;
  }

  return (
    <div>
      <h1 className="text-2xl mb-4">Weights Details</h1>
      <pre className="p-2 bg-gray-100 rounded-md border overflow-clip text-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default WeightsDetailsPage;
