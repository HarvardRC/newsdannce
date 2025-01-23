import { useComPreviewQuery } from '@/hooks';
import { CartesianGrid, Label, Line, LineChart, XAxis, YAxis } from 'recharts';

type props = {
  prediction_id: number;
};

const ComTraceChart: React.FC<props> = ({ prediction_id }) => {
  const { data: data_raw, isLoading } = useComPreviewQuery(
    prediction_id,
    10000
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }
  const data = data_raw!.map((o) => ({
    t: o[0],
    x: o[1],
    y: o[2],
    z: o[3],
  }));

  return (
    <>
      <LineChart
        width={800}
        height={800}
        margin={{
          top: 20,
          right: 50,
          bottom: 20,
          left: 50,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <YAxis dataKey="y" domain={['auto', 'auto']} type="number" interval={0}>
          <Label offset={0} position="insideLeft" angle={-90}>
            y position
          </Label>
        </YAxis>
        <XAxis dataKey="x" type="number">
          <Label offset={-5} position="insideBottomRight">
            x position
          </Label>
        </XAxis>
        <Line
          strokeWidth={1.5}
          data={data}
          dataKey="y"
          dot={false}
          stroke="rgba(255,100,100,0.2)"
          isAnimationActive={false}
        />
        <Line
          strokeWidth={1.5}
          data={data}
          dataKey="y"
          dot={false}
          stroke="rgba(100,100,100,0.8)"
          animationDuration={30000}
          animationEasing="linear"
        />
      </LineChart>
    </>
  );
};

export default ComTraceChart;
