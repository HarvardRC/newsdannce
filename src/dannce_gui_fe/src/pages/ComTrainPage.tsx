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
  useSubmitComTrainJobMutation,
} from '@/hooks';
import { appPages } from '@/routes';
import { useNavigate } from 'react-router-dom';

const formSchema = z.object({
  name: z.string().min(1).max(1000),
  video_folder_ids: z
    .array(z.any())
    .min(1, 'Must select at least one data folder'),
  output_model_name: z.string().min(1).max(1000),
  config: z.string(),
  epochs: z.coerce.number().min(1).max(2000),
  vol_size: z.coerce.number().min(1).max(800),
  runtime_id: z.coerce.number().min(0, 'Must select a runtime'),
});

type formType = z.infer<typeof formSchema>;

const ComTrainPage = () => {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      video_folder_ids: [],
      output_model_name: '',
      config: '',
      epochs: 0,
      vol_size: 240,
      runtime_id: -1,
    },
  });
  const navigate = useNavigate();

  const { data: runtimesData, isLoading: isRuntimesLoading } =
    useListRuntimesQuery();
  const { data: videoFolderData, isLoading: isVideoFoldersLoading } =
    useListVideoFoldersQuery();

  const mutation = useSubmitComTrainJobMutation();

  const onSubmit = async (values: formType) => {
    console.log('Com train submission. Values=', values);
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

  // Only show options with valid COM LABELS
  const videoFolderOptions = videoFolderData!
    .filter((x) => x.com_labels_file)
    .map((x) => ({
      id: x.id,
      name: x.name,
      path: x.path,
    }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Train COM Model</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Training Job Name</FormLabel>
                <FormControl>
                  <Input placeholder="E.g. Train COM Rat 2" {...field} />
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
                  <Input placeholder="e.g. alone-tethered-com-1" {...field} />
                </FormControl>
                <FormDescription>
                  Must be unique. This controls where the application will store
                  the trained COM model weights
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
                <FormLabel>
                  Select data folders to use in training. Only folders with COM
                  labels are listed.
                </FormLabel>
                <FormControl>
                  <AddVideoFoldersInput
                    options={videoFolderOptions}
                    multiSelect={true}
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
          <FormField
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
      "downfac": 8,
      "batch_size": 4
    }`}
                    className="min-h-[130px]"
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  Optional JSON arguments for the training job. Must be a
                  properly formatted JSON string
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

export default ComTrainPage;
