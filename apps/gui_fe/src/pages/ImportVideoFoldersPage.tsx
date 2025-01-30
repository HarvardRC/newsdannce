import { AutosizeTextarea } from '@/components/ui/autosize-textarea';
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
import { useImportVideoFoldersMutation } from '@/hooks';
import { appPages } from '@/routes';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

const transformInput = (x: string) => {
  return x
    .split('\n')
    .map((x) => x.trim())
    .filter((x) => x);
};

const formSchema = z.object({
  paths: z
    .string()
    .min(1)
    .max(3000)
    .transform(transformInput)
    .pipe(z.array(z.string()).min(1, 'Enter at least one path')),
});

type formType = z.infer<typeof formSchema>;

export default function ImportVideoFoldersPage() {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      paths: [],
    },
  });

  const mutation = useImportVideoFoldersMutation();

  // const mutation = useMakeRuntimeMutation();
  const navigate = useNavigate();

  const onSubmit = async (values: formType) => {
    // TODO: Handle import video folders logic here
    // console.log('Create Runtime Submission. Values=', values);
    // await mutation.mutateAsync({
    // ...values,
    // });
    // let result =;
    try {
      await mutation.mutateAsync(values);
      navigate(appPages.videoFolders.path);
    } catch (error) {
      form.setError('paths', {
        type: 'string',
        message:
          'Unable to import video folders. Perhaps folder does not exist or src folder has already been imported? Check logs for more details.',
      });
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold">Import Video Folders</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="paths"
            render={({ field }) => (
              <FormItem>
                <FormLabel></FormLabel>
                <FormControl>
                  <AutosizeTextarea {...field} />
                </FormControl>
                <FormDescription>
                  Enter one path for a video folder on each line
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <div>Note: this may take a few minutes per directory.</div>
          <Button type="submit">Import All</Button>
        </form>
      </Form>
    </div>
  );
}
