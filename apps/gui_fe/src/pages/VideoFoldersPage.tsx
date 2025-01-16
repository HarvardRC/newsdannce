import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useListVideoFoldersQuery } from '@/hooks';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

const VideoFoldersPage: React.FC = () => {
  const { data, isLoading } = useListVideoFoldersQuery();
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <TooltipProvider>
        <h1 className="text-2xl font-semibold mb-4">Video Folders</h1>
        <Table className="mb-10">
          <TableCaption>
            Current Video/Data Folders. Hover over certain columns for more
            information.
          </TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[20px]">ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Folder Path</TableHead>
              <TableHead>COM Labels</TableHead>
              <TableHead>DANNCE Labels</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data!.map((x) => {
              return (
                <TableRow key={x.id}>
                  <TableCell className="font-medium">{x.id}</TableCell>
                  <TableCell>
                    <Link
                      to={`${appPages.videoFolderDetails.path.replace(
                        /:id/,
                        x.id.toString()
                      )}`}
                    >
                      {x.name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Tooltip>
                      <TooltipTrigger>
                        {`${x.path.slice(0, 10)}...${x.path.slice(-10)}`}
                      </TooltipTrigger>
                      <TooltipContent>{x.path}</TooltipContent>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    {x.com_labels_file ? (
                      <Tooltip>
                        <TooltipTrigger>YES</TooltipTrigger>
                        <TooltipContent>{x.com_labels_file}</TooltipContent>
                      </Tooltip>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    {x.dannce_labels_file ? (
                      <Tooltip>
                        <TooltipTrigger>YES</TooltipTrigger>
                        <TooltipContent>{x.dannce_labels_file}</TooltipContent>
                      </Tooltip>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(x.created_at * 1000).toLocaleString('en-US')}
                  </TableCell>
                  <TableCell>
                    <div className="cursor-pointer">Delete</div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <div className="flex flex-row gap-4">
          <Link to={appPages.importVideoFolderPage.path}>
            <Button>Import Video Folders</Button>
          </Link>
        </div>
      </TooltipProvider>
    </div>
  );
};

export default VideoFoldersPage;
