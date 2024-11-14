import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { useVideoFolderDetailsQuery } from '@/hooks';
import { appPages } from '@/routes';
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';

const VideoFolderDetailsPage: React.FC = () => {
  const { id: idStr } = useParams();
  const [showPreview, setShowPreview] = useState(false);

  const id = parseInt(idStr!);

  const { isLoading, isError, data } = useVideoFolderDetailsQuery(id);

  if (isNaN(id)) {
    return null;
  }
  if (isLoading) return <div>Loading...</div>;

  if (isError || !data) return <div>Error</div>;

  //  hide params from labelData so they don't take up as much space
  const labelData =
    data.label_files.length > 0
      ? data.label_files.map(({ params, ...x }) => ({
          params: '[HIDDEN]',
          ...x,
        }))
      : [];

  const predictionData = (data as any).prediction_data;

  const predictJobs = (data as any).predict_jobs;

  return (
    <div>
      <h1 className="text-xl">Video Folder information</h1>
      <ul className="pl-4 pt-2 list-disc">
        <li>
          <span className="font-bold">Name:</span> {data.name}
        </li>
        <li>
          <span className="font-bold">Path:</span> {data.path}
        </li>
        <li>
          <span className="font-bold">Created on:</span>{' '}
          {new Date(data.created_at * 1000).toLocaleString('US-en')}
        </li>
        <li>
          <span className="font-bold">Current COM Label File:</span>{' '}
          {data.com_labels_file || '[NONE]'}
        </li>
        <li>
          <span className="font-bold">Current DANNCE Label File:</span>{' '}
          {data.dannce_labels_file || '[NONE]'}
        </li>
        <li>
          <span className="font-bold">Current COM Predictions:</span>{' '}
          {data.current_com_prediction ? (
            <Link
              to={appPages.predictionDetailsPage.path.replace(
                ':id',
                data.current_com_prediction
              )}
            >
              {data.current_com_prediction_name} [ID=
              {data.current_com_prediction}]
            </Link>
          ) : (
            '[NONE]'
          )}
        </li>
      </ul>
      <div>
        <Collapsible>
          <h2 className="my-6 text-lg">
            Labeled Files:{' '}
            <CollapsibleTrigger>(click to show)</CollapsibleTrigger>
          </h2>
          <CollapsibleContent>
            <pre>{JSON.stringify(labelData, null, 2)}</pre>
          </CollapsibleContent>
        </Collapsible>
      </div>
      <div>
        {
          <Collapsible>
            <h2 className="my-6 text-lg">
              Prediction Data:{' '}
              <CollapsibleTrigger>(click to show)</CollapsibleTrigger>
            </h2>
            <CollapsibleContent>
              <pre>{JSON.stringify(predictionData, null, 2)}</pre>
            </CollapsibleContent>
          </Collapsible>
        }
      </div>
      <div>
        <Collapsible>
          <h2 className="my-6 text-lg">
            Prediction Jobs run on this data:{' '}
            <CollapsibleTrigger>(click to show)</CollapsibleTrigger>
          </h2>
          <CollapsibleContent>
            <pre>{JSON.stringify(predictJobs, null, 2)}</pre>
          </CollapsibleContent>
        </Collapsible>
      </div>
      <div className="my-8">
        {showPreview ? (
          <>
            <h2 className="text-xl">Video Preview</h2>
            <video autoPlay controls className="max-w-xl">
              <source
                src={`/v1/video_folder/${id}/preview?camera_name=Camera1`}
                type="video/mp4"
              ></source>
            </video>
          </>
        ) : (
          <div>
            <Button onClick={() => setShowPreview(true)}>
              Show Video Preview (first 5 secs)
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoFolderDetailsPage;
