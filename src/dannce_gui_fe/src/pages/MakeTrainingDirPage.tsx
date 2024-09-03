
import { useForm } from 'react-hook-form';
const SubmitJob: React.FC = () => {
    const { register, handleSubmit, formState: { errors } } = useForm();

    const onSubmit = (data: any) => {
        // TODO: Handle job submission logic here
        console.log('Job submitted:', data.jobName);
    };

    return (
        <div className='flex justify-center flex-col items-center'>
            <h1 className="text-2xl font-bold">Submit Job</h1>
            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                <label className=''>
                    Project folder:
                    <input
                        type="text"
                        {...register('projectFolder', { required: true })}
                        className="border border-gray-300 rounded px-2 py-1 ml-2"
                    />
                </label>
                <label>
                    Config file:
                    <input
                        type="text"
                        {...register('configFile', { required: true })}
                        className="border border-gray-300 rounded px-2 py-1 ml-2"
                    />
                </label>

                {errors.jobName && <span className="text-red-500">This field is required</span>}
                <label>
                    Select Job Type:
                    <select {...register('jobType', { required: true })} className="border border-gray-300 rounded px-2 py-1 ml-2">
                        <option value="">Select...</option>
                        <option value="train com">Train COM</option>
                        <option value="train dannce">Train DANNCE</option>
                        <option value="predict com">Predict COM</option>
                        <option value="predict dannce">Predict DANNCE</option>
                    </select>
                </label>
                {errors.jobType && <span className="text-red-500">This field is required</span>}
                <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">Submit</button>
            </form>
        </div>
    );
};

export default SubmitJob;