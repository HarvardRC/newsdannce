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
import { useMakeVideoFolderMutation } from '@/hooks';
import { appPages } from '@/routes';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

const formSchema = z.object({
  path: z.string().min(2).max(1000),
  name: z.string().min(1).max(1000),
  dannce_data_file: z
    .string()
    .min(1)
    .max(1000)
    .endsWith(
      'dannce.mat',
      'Filename must end with "dannce.mat (if specified)"'
    )
    .or(z.literal('')),
  com_data_file: z
    .string()
    .min(1)
    .max(1000)
    .endsWith(
      'dannce.mat',
      'Filename must end with "dannce.mat (if specified)"'
    )
    .or(z.literal('')),
});

type formType = z.infer<typeof formSchema>;

const MakeVideoFolderPage: React.FC = () => {
  const mutation = useMakeVideoFolderMutation();
  const navigate = useNavigate();

  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      path: '',
      name: '',
      com_data_file: '',
      dannce_data_file: '',
    },
  });

  const onSubmit = async (values: formType) => {
    // TODO: Handle job submission logic here
    console.log('values', values);
    await mutation.mutateAsync({
      name: values.name,
      path: values.path,
      com_data_file: values.com_data_file,
      dannce_data_file: values.dannce_data_file,
    });
    navigate(appPages.videoFolders.path);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold">Add Video (Data) Folder</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Video Folder Name</FormLabel>
                <FormControl>
                  <Input placeholder="e.g. Rat 2, Day 2 ALONE" {...field} />
                </FormControl>
                <FormDescription>
                  Helpful name to identify this folder
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="path"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Full path to folder</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g. /net/holy-nfsisilon/ifs/rc_labs..."
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  This folder should include a{' '}
                  <span className="font-mono">videos</span> folder, and should
                  be accessible from the cluster.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="dannce_data_file"
            render={({ field }) => (
              <FormItem>
                <FormLabel>COM Labels File (empty if none)</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormDescription>
                  {' '}
                  Filename of a dannce.mat file in this data folder containing
                  COM labels.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="com_data_file"
            render={({ field }) => (
              <FormItem>
                <FormLabel>DANNCE Labels File (empty if none)</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormDescription>
                  {' '}
                  FIlename of a dannce.mat file in this data folder containing
                  DANNCE labels.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit">Submit</Button>
        </form>
      </Form>
    </div>
  );
};

export default MakeVideoFolderPage;
