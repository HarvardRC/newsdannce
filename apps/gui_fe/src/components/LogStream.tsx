import { useGpuJobLogFile } from '@/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { RefreshCcw } from 'lucide-react';

type props = {
  gpuJobId: number;
};

function stripProgressLines(input: string) {
  // FUTURE: process lines to remove progress bars
  return input;
}

const LogStream: React.FC<props> = ({ gpuJobId }) => {
  const queryClient = useQueryClient();

  const { data: logFileData, isLoading, isError } = useGpuJobLogFile(gpuJobId);

  if (isLoading) {
    return <div>Loading</div>;
  }

  const isEmpty = isError ? true : (logFileData as string).length == 0;

  const handleRefreshButton = () => {
    queryClient.invalidateQueries({
      queryKey: ['gpuJobLogFile', gpuJobId],
    });
  };

  return (
    <div>
      <ScrollArea className="h-[500px] bg-gray-50 rounded-md border p-4 my-4">
        <pre className="text-wrap">
          {isError && 'Log file does not exist yet.'}
          {!isError && isEmpty && '<Empty file>'}
          {!isError && !isEmpty && stripProgressLines(logFileData)}
        </pre>
      </ScrollArea>
      <Button onClick={handleRefreshButton}>
        <RefreshCcw />
      </Button>
    </div>
  );
};

export default LogStream;
