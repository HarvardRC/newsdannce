import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useListPredictionsQuery } from '@/hooks';
import { timestampString } from '@/lib/utils';
import { appPages } from '@/routes';
import { Link } from 'react-router-dom';

export default function PredictionsPage() {
  const {
    data: rawPredictions,
    isLoading,
    isError,
  } = useListPredictionsQuery();
  if (isLoading) {
    return <div>loading</div>;
  }

  const data = rawPredictions || [];

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Predictions</h1>
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
              <TableRow key={x.prediction_id}>
                <TableCell className="font-medium">{x.prediction_id}</TableCell>
                <TableCell>
                  <Link
                    to={appPages.predictionDetailsPage.path.replace(
                      /:id/,
                      `${x.prediction_id}`
                    )}
                  >
                    {x.prediction_name}
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
