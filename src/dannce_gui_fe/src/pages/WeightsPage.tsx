import {
  Table,
  TableBody,
  TableCaption,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function WeightsPage() {
  //   const {
  //     data: rawPredictions,
  //     isLoading,
  //     isError,
  //   } = useListPredictionsQuery();
  //   if (isLoading) {
  //     return <div>loading</div>;
  //   }

  //   const data = rawPredictions || [];

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
          <div>TODO CREATE TABLE</div>
        </TableBody>
      </Table>
    </div>
  );
}
