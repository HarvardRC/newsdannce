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
import { useMakeRuntimeMutation } from '@/hooks';
import { appPages } from '@/routes';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

const formSchema = z.object({
  name: z.string().min(1).max(1000),
  partition_list: z
    .string()
    .min(1, 'Must specify at least one slurm partition')
    .max(1000, 'Specify a shorter string')
    .regex(/^\w+(?:,\s?\w+)*$/, 'Invalid format'),
  memory_gb: z.coerce
    .number()
    .int()
    .min(1, 'Must allocate at least 1 GB of RAM')
    .max(2048, 'Cannot allocate more than 2048 GB of RAM'),
  time_hrs: z.coerce
    .number()
    .int()
    .min(1, 'Runtime must be at least one hour')
    .max(14 * 24, 'Cannot run for more than 14 days'),
  n_cpus: z.coerce
    .number()
    .int()
    .min(1, 'Must allocate at least one CPU')
    .max(1024, 'Cannot allocate more than 1024 CPUs'),
});

type formType = z.infer<typeof formSchema>;

const CreateRuntimePage: React.FC = () => {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      partition_list: '',
      memory_gb: 0,
      time_hrs: 0,
      n_cpus: 0,
    },
  });

  const mutation = useMakeRuntimeMutation();
  const navigate = useNavigate();

  const onSubmit = async (values: formType) => {
    // TODO: Handle job submission logic here
    console.log('Create Runtime Submission. Values=', values);
    await mutation.mutateAsync({
      ...values,
    });
    navigate(appPages.runtimes.path);
  };
  return (
    <div>
      <h1 className="text-2xl font-bold">Define a Runtime</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Runtime Name</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormDescription></FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="partition_list"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  List of SLURM partitions to use (seperated by commas)
                </FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="memory_gb"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Memory to allocate (GB)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="time_hrs"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Job Max Runtime (hrs)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="n_cpus"
            render={({ field }) => (
              <FormItem>
                <FormLabel># of CPUs to allocate</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit">Save Runtime Configuration</Button>
        </form>
      </Form>
    </div>
  );
};

export default CreateRuntimePage;
