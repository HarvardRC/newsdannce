import { usePreviewPredictionQuery } from '@/hooks';
import PreviewPrediction from './PreviewPrediction';
import { PredictionDetailsType } from '@/api';

type Props = {
  predictionId: number;
  frames: number[];
  camera1: string;
  camera2: string;
  predictionDetails: PredictionDetailsType;
};
const PreviewContainer: React.FC<Props> = ({ ...props }) => {
  const {
    data: previewData,
    // isSuccess: isPreviewSuccess,
    isLoading: isPreviewLoading,
    isError: isPreviewError,
    // refetch: fetchPreview,
  } = usePreviewPredictionQuery(
    props.predictionId,
    props.frames,
    props.camera1,
    props.camera2
  );

  if (isPreviewLoading) {
    return <div>Loading...</div>;
  }

  if (isPreviewError) {
    return <div> Error fetching preview frames</div>;
  }

  return (
    <div>
      {previewData ? (
        <PreviewPrediction
          data={previewData!}
          predictionDetails={props.predictionDetails}
        />
      ) : (
        <div>No data</div>
      )}
    </div>
  );
};

export default PreviewContainer;
