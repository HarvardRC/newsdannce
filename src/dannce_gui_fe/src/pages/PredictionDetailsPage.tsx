import PreviewPrediction from '@/components/PreviewPrediction';
import { usePredictionDetailsQuery } from '@/hooks';
import { useParams } from 'react-router-dom';

type CustomProps = {};

const PredictionDetailsPage: React.FC<CustomProps> = ({ ...props }) => {
  const { id: idStr } = useParams();
  const id = parseInt(idStr!);

  const { data, isLoading, isError } = usePredictionDetailsQuery(id);

  if (isLoading) {
    return <div>Loading</div>;
  }
  if (isError) {
    return <div> error</div>;
  }

  return (
    <div>
      <h1 className="text-2xl mb-4">Prediction Details</h1>
      <pre className="p-2 bg-gray-100 rounded-md border">
        {JSON.stringify(data, null, 2)}
      </pre>
      <PreviewPrediction
        cameraName1="Camera1"
        cameraName2="Camera2"
        frames={[0, 1000, 2000, 3000]}
        predictionId={id}
      />
    </div>
  );
};

export default PredictionDetailsPage;
