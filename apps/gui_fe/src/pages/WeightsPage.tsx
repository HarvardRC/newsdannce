import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useListWeightsQuery } from '@/hooks';
import { timestampString } from '@/lib/utils';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

export default function WeightsPage() {
  const { data: rawWeights, isLoading } = useListWeightsQuery();
  if (isLoading) {
    return <div>Loading...</div>;
  }

  const data = rawWeights || [];

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Model Weights</h1>
      <Table className="mb-4">
        <TableCaption>
          Predictions from COM and DANNCE models. Click on name for more
          details.
        </TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[20px]">ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Mode</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Actions </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((x) => {
            return (
              <TableRow key={x.id}>
                <TableCell className="font-medium">{x.id}</TableCell>
                <TableCell>
                  <Link
                    to={appPages.weightsDetailsPage.path.replace(
                      /:id/,
                      `${x.id}`
                    )}
                  >
                    {x.name}
                  </Link>
                </TableCell>
                <TableCell>{x.mode}</TableCell>
                <TableCell>{x.status}</TableCell>
                <TableCell>{timestampString(x.created_at)}</TableCell>
                <TableCell>
                  {/* <div className="font-semibold cursor-pointer">Actions</div> */}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
