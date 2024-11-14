import { Input } from '@/components/ui/input';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import AddVideoFoldersInput from '@/components/AddVideoFoldersInput';
import {
  useListRuntimesQuery,
  useListVideoFoldersQuery,
  useListWeightsQuery,
  useSubmitComPredictJobMutation,
} from '@/hooks';
import { appPages } from '@/routes';
import { useNavigate } from 'react-router-dom';
import SelectWeightsComboBox from '@/components/SelectWeightsComboBox';

const formSchema = z.object({
  name: z.string().min(1).max(1000),
  prediction_name: z.string().min(1).max(1000),
  video_folder_ids: z
    .array(z.any())
    .min(1, 'Must select at least one data folder'),
  weights_id: z.coerce.number().min(0, 'Must select weights'),
  config: z.string(),
  runtime_id: z.coerce.number().min(0, 'Must select a runtime'),
});

type formType = z.infer<typeof formSchema>;

const ComPredictPage = () => {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      prediction_name: '',
      video_folder_ids: [],
      weights_id: -1,
      config: '',
      runtime_id: -1,
    },
  });
  const navigate = useNavigate();

  const { data: runtimesData, isLoading: isRuntimesLoading } =
    useListRuntimesQuery();
  const { data: videoFolderData, isLoading: isVideoFoldersLoading } =
    useListVideoFoldersQuery();
  const { data: weightsData, isLoading: isWeightsLoading } =
    useListWeightsQuery();
  const mutation = useSubmitComPredictJobMutation();

  const onSubmit = async (values: formType) => {
    console.log('Com Predict submission. VALUES BEFORE TRANSFORM=', values);
    const newValues = {
      name: values.name,
      prediction_name: values.name,
      weights_id: values.weights_id,
      video_folder_id: values.video_folder_ids[0],
      runtime_id: values.runtime_id,
      config: values.config.length == 0 ? '{}' : values.config,
    };
    console.log('Com Pred. sub. val post transform: ', newValues);
    const ret = await mutation.mutateAsync(newValues);
    console.log('RETURNED DATA', ret);
    navigate(appPages.monitorJobs.path);
  };

  if (isRuntimesLoading || isVideoFoldersLoading || isWeightsLoading) {
    return <div>Data still loading...</div>;
  }

  const videoFolderOptions = videoFolderData!.map((x) => ({
    id: x.id,
    name: x.name,
    path: x.path,
  }));

  const weightsOptions = weightsData!
    .filter((x) => x.mode == 'COM')
    .filter((x) => x.status == 'COMPLETED')
    .map((x) => ({
      id: x.id,
      name: x.name,
    }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Predict COM Data</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Inference Job Name</FormLabel>
                <FormControl>
                  <Input placeholder="E.g. Predict COM Rat" {...field} />
                </FormControl>
                <FormDescription>
                  This name will help you identify the job
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="prediction_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Prediction Data Name</FormLabel>
                <FormControl>
                  <Input placeholder="predict01" {...field} />
                </FormControl>
                <FormDescription>
                  This name will help you identify the prediction data for this
                  animal.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="weights_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select Trained COM Model (Weights)</FormLabel>
                <FormControl>
                  <SelectWeightsComboBox
                    options={weightsOptions}
                    mode="COM"
                    {...field}
                  />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="video_folder_ids"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Select One Data Folder for COM Inference</FormLabel>
                <FormControl>
                  <AddVideoFoldersInput
                    options={videoFolderOptions}
                    multiSelect={false}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Each folder will use the most recent COM label files by
                  default. Click on the folder name to get more info in a new
                  tab.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="config"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Additional config options (JSON)</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder={`e.g. {
      "max_num_samples": 250
    }`}
                    className="min-h-[130px]"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Optional JSON arguments for the prediction job. Must be a
                  properly formatted JSON string (or emtpy)
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="runtime_id"
            render={({ field }) => {
              const options = runtimesData;
              return (
                <FormItem>
                  <FormLabel>Runtime Configuration</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={''}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select ">
                          {options
                            ? options.find((x) => x.id == field.value)?.name
                            : null}
                        </SelectValue>
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {options!.map((x) => (
                        // @ts-ignore
                        <SelectItem key={x.id} value={x.id}>
                          {x.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Select a SLURM runtime defined on the Runtimes page
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              );
            }}
          />

          <Button type="submit">Submit</Button>
        </form>
      </Form>
    </div>
  );
};

export default ComPredictPage;
