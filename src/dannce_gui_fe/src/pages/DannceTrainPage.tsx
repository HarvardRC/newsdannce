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
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { BASE_API_URL } from '@/config';
import { Textarea } from '@/components/ui/textarea';
import AddVideoFoldersInput from '@/components/AddVideoFoldersInput';
import { useListRuntimesQuery, useListVideoFoldersQuery } from '@/hooks';
import { RadioGroup } from '@/components/ui/radio-group';
import { RadioGroupItem } from '@radix-ui/react-radio-group';

const placeholder_data_files = `e.g. [
    {
        "base_folder": "/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_135840_M4",
        "com_prediction_folder": "./COM/predict01",
        "dannce_label_file": "./20240808_124927_DANNCE_Label3D_dannce.mat"
    },
    {
        "base_folder": "/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5",
        "com_prediction_folder": "./COM/predict01",
        "dannce_label_file": "./20240808_125233_DANNCE_Label3D_dannce.mat"
    }
]`;

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

  const { data: runtimesData, isLoading: isRuntimesLoading } =
    useListRuntimesQuery();
  const { data: videoFolderData, isLoading: isVideoFoldersLoading } =
    useListVideoFoldersQuery();

  const onSubmit = (values: formType) => {
    // TODO: Handle job submission logic here
    console.log('values', values);
  };

  if (isRuntimesLoading || isVideoFoldersLoading) {
    return <div>Data still loading...</div>;
  }

  const videoFolderOptions = videoFolderData!.map((x) => ({
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
                <FormLabel>Select data folders to use in training</FormLabel>
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
          {/* <FormField
            control={form.control}
            name="video_files"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Data folders to include in training</FormLabel>
                <FormControl>
                  <Textarea
                    className="min-h-[250px]"
                    placeholder={placeholder_data_files}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
                <FormDescription>
                  Specify a JSON list containing items with keys "base_folder",
                  "com_prediction_folder", and "dannce_label_file".
                </FormDescription>
              </FormItem>
            )}
          /> */}

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
      "downfac": 8,
      "batch_size": 4,
      "train_mode":"new"
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

export default DannceTrainPage;
