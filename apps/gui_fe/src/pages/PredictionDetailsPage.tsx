import PreviewContainer from '@/components/PreviewContainer';
import { Button } from '@/components/ui/button';
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

type CustomProps = {};

const formSchema = z.object({
  frames: z.string(),
});

const PredictionDetailsPage: React.FC<CustomProps> = () => {
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

  // const handlePreparePreview = () => {
  //   fetchPreview({});
  // };

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    console.log('VALUES ARE ', values);
    let frames = values.frames.split(',').map((x) => parseInt(x.trim()));
    setFrames(frames);
  };

  return (
    <div>
      <h1 className="text-2xl mb-4">Prediction Details</h1>
      <pre className="p-2 bg-gray-100 rounded-md border overflow-clip text-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
      <div className="my-4">
        <div>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
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
              <Button
                type="submit"
                // onClick={handlePreparePreview}
                // disabled={isPreviewLoading}
                className="my-4"
              >
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
        />
      )}
    </div>
  );
};

export default PredictionDetailsPage;
