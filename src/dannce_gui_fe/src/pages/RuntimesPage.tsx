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
import { useListRuntimesQuery } from '@/hooks';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

export default function RuntimesPage() {
  const { data, isLoading } = useListRuntimesQuery();
  if (isLoading) {
    return <div>Loading...</div>;
  }
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Runtimes</h1>
      <Table>
        <TableCaption>Currently Running DANNCE Jobs</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[20px]">ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Partitions</TableHead>
            <TableHead>Memory (GB)</TableHead>
            <TableHead>Time (h)</TableHead>
            <TableHead>CPUS</TableHead>
            <TableHead>Actions </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data!.map((x) => {
            return (
              <TableRow key={x.id}>
                <TableCell className="font-medium">{x.id}</TableCell>
                <TableCell>{x.name}</TableCell>
                <TableCell>{x.partition_list}</TableCell>
                <TableCell>{x.memory_gb}</TableCell>
                <TableCell>{x.time_hrs}</TableCell>
                <TableCell>{x.n_cpus}</TableCell>
                <TableCell>
                  {/* <div className="font-semibold cursor-pointer">Cancel</div> */}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Link to={appPages.makeRuntime.path}>
        <Button>Create New Runtime</Button>
      </Link>
    </div>
  );
}
