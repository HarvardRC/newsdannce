import { useComHistogramQuery } from '@/hooks';
import { Bar, BarChart, CartesianGrid, Label, XAxis, YAxis } from 'recharts';

type props = {
  prediction_id: number;
};

const ComHistogramChart: React.FC<props> = ({ prediction_id }) => {
  const { data: data_raw, isLoading } = useComHistogramQuery(prediction_id);

  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (!data_raw) {
    return <div>Error data missing</div>;
  }
  const labels = data_raw.bin_edges;
  const data = data_raw.hist.map((x, i) => ({
    name: `${labels[i].toFixed(2)}`,
    x: x,
  }));

  console.log('DATA:', data);
  return (
    <>
      <BarChart
        width={800}
        height={500}
        data={data}
        margin={{ top: 5, right: 30, left: 50, bottom: 40 }}
        barSize={20}
      >
        <XAxis dataKey="name" scale="band" padding={{ left: 10, right: 10 }}>
          <Label position={'bottom'}>
            eucl. distance delta between frames (mm)
          </Label>
        </XAxis>
        <YAxis scale="log" domain={[0.5, 'auto']}>
          <Label position="insideLeft" offset={-10} angle={-90}>
            # frames
          </Label>
        </YAxis>
        <CartesianGrid strokeDasharray="3 3" />
        <Bar
          isAnimationActive={false}
          dataKey="x"
          fill="#8884d8"
          background={{ fill: '#eee' }}
        />
      </BarChart>
    </>
  );
};

export default ComHistogramChart;
