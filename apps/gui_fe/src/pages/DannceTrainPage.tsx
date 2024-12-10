// TOOD: VERY WIP - finsih page
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
  useSubmitDannceTrainJobMutation,
} from '@/hooks';
import { useNavigate } from 'react-router-dom';
import { appPages } from '@/routes';

const formSchema = z.object({
  name: z.string().min(1).max(1000),
  video_folder_ids: z
    .array(z.any())
    .min(1, 'Must select at least one data folder'),
  output_model_name: z.string().min(1).max(1000),
  config: z.string(),
  epochs: z.coerce.number().min(1).max(2000),
  runtime_id: z.coerce.number().min(0, 'Must select a runtime'),
});

type formType = z.infer<typeof formSchema>;

const DannceTrainPage = () => {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      video_folder_ids: [],
      output_model_name: '',
      config: '',
      epochs: 0,
      runtime_id: -1,
    },
  });
  const navigate = useNavigate();

  const { data: runtimesData, isLoading: isRuntimesLoading } =
    useListRuntimesQuery();
  const { data: videoFolderData, isLoading: isVideoFoldersLoading } =
    useListVideoFoldersQuery();

  const mutation = useSubmitDannceTrainJobMutation();

  const onSubmit = async (values: formType) => {
    console.log('Dannce train submission. Values=', values);
    let { config, ...rest } = values;
    if (config.length == 0) {
      config = '{}';
    }
    const ret = await mutation.mutateAsync({ config, ...rest });
    console.log('RETURNED DATA', ret);
    navigate(appPages.monitorJobs.path);
  };

  if (isRuntimesLoading || isVideoFoldersLoading) {
    return <div>Data still loading...</div>;
  }

  const videoFolderOptions = videoFolderData!
    .filter((x) => x.current_com_prediction)
    .map((x) => ({
      id: x.id,
      name: x.name,
      path: x.path,
    }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Train DANNCE Model</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Training Job Name</FormLabel>
                <FormControl>
                  <Input placeholder="E.g. Train DANNCE Rat 2" {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="output_model_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Output Model Name</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g. alone-tethered-dannce-1"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Must be unique. This controls where DANNCE will store the
                  trained model weights
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="video_folder_ids"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Data Folders to use in DANNCE Training</FormLabel>{' '}
                <FormControl>
                  <AddVideoFoldersInput
                    options={videoFolderOptions}
                    multiSelect={true}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Each folder will use the most recent COM label files and COM
                  predictions by default. Click on the folder name to get more
                  info in a new tab.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="epochs"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Training Epochs</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="e.g. 100" {...field} />
                </FormControl>
                <FormMessage />
                <FormDescription>
                  Number of epochs for training. Recommended 100-200. This sets
                  the epochs option in the config file.
                </FormDescription>
              </FormItem>
            )}
          />
          {/* <FormField
            control={form.control}
            name="vol_size"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Size of bounding box</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="e.g. 100" {...field} />
                </FormControl>
                <FormMessage />
                <FormDescription>
                  Recommended 240 or 320 for rats. This sets the vol_size option
                  in the config file.
                </FormDescription>
              </FormItem>
            )}
          /> */}
          <FormField
            control={form.control}
            name="config"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Additional config options (JSON)</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder={`e.g. {
      "batch_size": 4,
      "train_mode":"new"
    }`}
                    className="min-h-[130px]"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Optional JSON arguments for the training job. Must be a
                  properly formatted JSON string (or empty)
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

export default DannceTrainPage;
