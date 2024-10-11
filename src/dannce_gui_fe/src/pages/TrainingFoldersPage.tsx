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
import { useListTrainingFoldersQuery } from '@/hooks';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

const TrainingFoldersPage: React.FC = () => {
  const { data, isLoading } = useListTrainingFoldersQuery();
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Training Folders</h1>
      <Table>
        <TableCaption>Current Training Folders</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[20px]">ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Folder Path</TableHead>
            <TableHead>Has Model</TableHead>
            <TableHead>Mode</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data!.map((x) => {
            return (
              <TableRow key={x.id}>
                <TableCell className="font-medium">{x.id}</TableCell>
                <TableCell>{x.name}</TableCell>
                <TableCell>{x.path}</TableCell>
                <TableCell>{x.has_model ? 'Yes' : 'No'}</TableCell>
                <TableCell>{x.mode}</TableCell>
                <TableCell>
                  {new Date(x.created_at * 1000).toLocaleString('en-US')}
                </TableCell>
                <TableCell>
                  <div className="cursor-pointer">Edit | Delete</div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Link to={appPages.makeTrainingFolder.path}>
        <Button>Create Training Folder</Button>
      </Link>
    </div>
  );
};

export default TrainingFoldersPage;
