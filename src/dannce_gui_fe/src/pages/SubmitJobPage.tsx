import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { useQuery } from "@tanstack/react-query";
import { BASE_API_URL } from "@/config";

const JOB_TYPES = ["train com", "predict com", "train dannce", "predict dannce"] as const;

const formSchema = z.object({
    configPath: z.string().min(2).max(200),
    projectFolder: z.string().min(2).max(200),
    command: z.enum(JOB_TYPES)
});

export default function () {

    const navigate = useNavigate();
    const form = useForm<z.infer<typeof formSchema>>({

        resolver: zodResolver(formSchema),
        defaultValues: {
            configPath: '',
            projectFolder: '',
            command: 'train com'
        }

    })

    function onSubmit(values: z.infer<typeof formSchema>) {
        // TODO: Handle form submission
        console.log(`Submitting values ${JSON.stringify(values)}`);
        toast("Submitted job")

        navigate("/")

    }

    const { isPending, error, data } = useQuery({
        queryKey: ['submit-job'],
        queryFn: () => fetch(`${BASE_API_URL}/submit-job`).then((res) => res.json(),)
    });

    console.log("RENDERING WITH DATA", data)

    // const { register, handleSubmit, formState: { errors } } = useForm();

    // const onSubmit = (data: any) => {
    //     // TODO: Handle form submission
    //     console.log('Creating training directory:', data.directoryName);
    // };
    return (
        <div className="flex-col justify-center px-40 py-10 max-w-[800px] items-center">
            <h1 className="scroll-m-20 text-4xl font-semibold tracking-tight lg:text-4xl mb-5">Create training directory</h1>

            <Form {...form}>

                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                    <FormField
                        control={form.control}
                        name="configPath"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Config Path</FormLabel>
                                <FormControl>
                                    <Input placeholder="" {...field} />
                                </FormControl>
                                <FormDescription>
                                    Location of the config yaml file.
                                </FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="projectFolder"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Project Folder</FormLabel>
                                <FormControl>
                                    <Input placeholder="" {...field} />
                                </FormControl>
                                <FormDescription>
                                    Path of the project folder for this job.
                                </FormDescription>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="command"
                        render={({ field }) => {
                            // remove "ref" from field to avoid bugs
                            const { ref, ...restField } = field;
                            return (
                                <FormItem>
                                    <FormLabel>Type of Job</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                        {...restField}
                                    >
                                        <FormControl>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent>
                                            {
                                                JOB_TYPES.map(x => (<SelectItem key={x} value={x}>{x}</SelectItem>))
                                            }

                                        </SelectContent>
                                    </Select>
                                </FormItem>

                            )
                        }}
                    />

                    <Button type="submit">Submit</Button>
                </form>
            </Form >
        </div>
    )
}