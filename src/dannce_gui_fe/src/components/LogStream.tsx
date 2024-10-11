import { useSlurmLogfileQuery } from '@/hooks';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { RefreshCcw } from 'lucide-react';

type props = {
  slurmJobId: number;
};

function stripProgressLines(input: string) {
  // FUTURE: process lines to remove progress bars
  return input;
}

const LogStream: React.FC<props> = ({ slurmJobId }) => {
  const queryClient = useQueryClient();

  const {
    data: logFileData,
    isLoading,
    isError,
  } = useSlurmLogfileQuery(slurmJobId);

  if (isLoading || slurmJobId == undefined) {
    return <div>Loading</div>;
  }

  const isEmpty = isError ? true : (logFileData as string).length == 0;

  const handleRefreshButton = () => {
    queryClient.invalidateQueries({
      queryKey: ['SlurmLogfile', slurmJobId],
    });
  };

  return (
    <div>
      <ScrollArea className="h-[500px] bg-gray-50 rounded-md border p-4 my-4">
        <pre>
          {isError && 'Error fetching file. Perhaps it does not exist.'}
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
