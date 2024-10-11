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
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const formSchema = z.object({
  mode: z.enum(['COM', 'DANNCE']),
  path: z.string().min(2).max(1000),
  name: z.string().min(1).max(1000),
});

type formType = z.infer<typeof formSchema>;

const MakeTrainDirPage: React.FC = () => {
  const form = useForm<formType>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      path: '',
      name: '',
    },
  });

  const onSubmit = (values: formType) => {
    // TODO: Handle job submission logic here
    console.log('values', values);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold">Create Training Folder</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Training Folder Name</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormDescription>
                  Human-identifiable name for training folder
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="mode"
            render={({ field }) => (
              <FormItem className="space-y-3">
                <FormLabel>Training Mode</FormLabel>
                <FormControl>
                  <RadioGroup
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    className="flex flex-col space-y-1"
                  >
                    <FormItem className="flex items-center space-x-3 space-y-0">
                      <FormControl>
                        <RadioGroupItem value="COM" />
                      </FormControl>
                      <FormLabel className="font-normal">COM</FormLabel>
                    </FormItem>
                    <FormItem className="flex items-center space-x-3 space-y-0">
                      <FormControl>
                        <RadioGroupItem value="DANNCE" />
                      </FormControl>
                      <FormLabel className="font-normal">DANNCE</FormLabel>
                    </FormItem>
                    <FormItem className="flex items-center space-x-3 space-y-0">
                      <FormControl>
                        <RadioGroupItem value="SDANNCE" disabled />
                      </FormControl>
                      <FormLabel className="font-normal">
                        SDANNCE (not supported yet)
                      </FormLabel>
                    </FormItem>
                  </RadioGroup>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="path"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Path to training folder</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
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

export default MakeTrainDirPage;
