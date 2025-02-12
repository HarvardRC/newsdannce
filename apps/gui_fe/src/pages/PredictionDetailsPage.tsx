import ComPreviewChart from '@/components/ComPreviewChart';
import PreviewContainer from '@/components/PreviewContainer';
import { Button } from '@/components/ui/button';
import ComTraceChart from '@/components/ComTraceChart';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { usePredictionDetailsQuery } from '@/hooks';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useParams } from 'react-router-dom';
import { z } from 'zod';
import ComHistogramChart from '@/components/ComHistogramChart';

type CustomProps = {};

const formSchema = z.object({
  frames: z.string(),
});

const PredictionDetailsPage: React.FC<CustomProps> = () => {
  const [showPositionGraph, setShowPositionGraph] = useState(false);
  const [showPositionTrace, setShowPositionTrace] = useState(false);
  const [showComHistogram, setShowComHistogram] = useState(false);

  const { id: idStr } = useParams();
  const id = parseInt(idStr!);
  const [frames, setFrames] = useState<any>(null);

  const { data, isLoading, isError } = usePredictionDetailsQuery(id);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      frames: '',
    },
  });

  if (isLoading) {
    return <div>Loading</div>;
  }
  if (isError) {
    return <div> error</div>;
  }

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log('VALUES ARE ', values);
    let frames = values.frames.split(',').map((x) => parseInt(x.trim()));
    frames.forEach((x) => {
      if (x < 0 || x >= data!.n_frames)
        throw Error(
          'frame numbers must be between 0 (inclusive) and n_frames (exclusive)'
        );
    });
    setFrames(frames);
  };

  return (
    <div>
      <h1 className="text-2xl mb-4">Prediction Details</h1>
      <pre className="p-2 bg-gray-100 rounded-md border overflow-clip text-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
      {data!.status == 'COMPLETED' ? (
        <>
          <div className="my-4">
            <div>
              <Form {...form}>
                <form
                  onSubmit={form.handleSubmit(onSubmit)}
                  className="space-y-8"
                >
                  <FormField
                    control={form.control}
                    name="frames"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Frames to Preview</FormLabel>
                        <FormControl>
                          <Input
                            className="max-w-[400px]"
                            {...field}
                            placeholder="E.g. 1,1000,2000"
                          />
                        </FormControl>
                        <FormDescription></FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type="submit" className="my-4">
                    Preview Prediction
                  </Button>
                </form>
              </Form>
            </div>
          </div>
          {frames && (
            <PreviewContainer
              predictionId={id}
              frames={frames}
              camera1="Camera1"
              camera2="Camera2"
              predictionDetails={data!}
            />
          )}
          <hr />
          {data!.mode == 'COM' && (
            <div className="mt-5 flex flex-col gap-5">
              <div>
                <Button
                  type="button"
                  onClick={() => setShowPositionGraph((x) => !x)}
                >
                  {showPositionGraph ? 'Hide' : 'Show'} Position Graph
                </Button>
              </div>
              {showPositionGraph && (
                <div>
                  <ComPreviewChart prediction_id={id} />{' '}
                </div>
              )}
              <div>
                <Button
                  type="button"
                  onClick={() => setShowPositionTrace((x) => !x)}
                >
                  {showPositionTrace ? 'Hide' : 'Show'} Position Trace
                </Button>
              </div>
              {showPositionTrace && (
                <div>
                  <ComTraceChart prediction_id={id} />{' '}
                </div>
              )}
              <div>
                <Button
                  type="button"
                  onClick={() => setShowComHistogram((x) => !x)}
                >
                  {showComHistogram ? 'Hide' : 'Show'} COM Histogram
                </Button>
              </div>
              {showComHistogram && (
                <div>
                  <ComHistogramChart prediction_id={id} />{' '}
                </div>
              )}
            </div>
          )}
        </>
      ) : (
        <div>
          Cannot show prediction previews for predictions where status is not
          COMPLETED
        </div>
      )}
    </div>
  );
};

export default PredictionDetailsPage;
