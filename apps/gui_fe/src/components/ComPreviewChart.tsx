import { useComPreviewQuery } from '@/hooks';
import { useState } from 'react';
import {
  CartesianGrid,
  Label,
  Legend,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from 'recharts';

type props = {
  prediction_id: number;
};

const ComPreviewChart: React.FC<props> = ({ prediction_id }) => {
  const [selectedAxis, setSelectedAxis] = useState<null | 'x' | 'y' | 'z'>(
    null
  );
  const { data: data_raw, isLoading } = useComPreviewQuery(prediction_id);

  if (isLoading) {
    return <div>Loading...</div>;
  }
  const data = data_raw!.map((o) => ({
    t: o[0],
    x: o[1],
    y: o[2],
    z: o[3],
  }));

  const handleLegendClick = (o: any) => {
    const { dataKey } = o;
    if (dataKey == selectedAxis) {
      setSelectedAxis(null);
      return;
    }
    if (dataKey == 'x') {
      setSelectedAxis('x');
      return;
    }
    if (dataKey == 'y') {
      setSelectedAxis('y');
      return;
    }
    if (dataKey == 'z') {
      setSelectedAxis('z');
      return;
    }
  };

  return (
    <>
      <LineChart
        width={1500}
        height={500}
        margin={{
          top: 20,
          right: 30,
          bottom: 20,
          left: 50,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <YAxis domain={['auto', 'auto']} type="number" interval={0}>
          <Label offset={0} position="insideLeft" angle={-90}>
            World position (mm)
          </Label>
        </YAxis>
        <XAxis dataKey="t" type="number">
          <Label offset={-5} position="insideBottomRight">
            Frame No.
          </Label>
        </XAxis>
        <Legend onClick={handleLegendClick} />
        <Line
          strokeWidth={1}
          isAnimationActive={false}
          data={data}
          dataKey="x"
          dot={false}
          stroke={
            selectedAxis == null || selectedAxis == 'x' ? '#ff0000' : '#ddd'
          }
        />
        <Line
          strokeWidth={1}
          isAnimationActive={false}
          data={data}
          dataKey="y"
          dot={false}
          stroke={
            selectedAxis == null || selectedAxis == 'y' ? '#00af20' : '#ddd'
          }
        />
        <Line
          strokeWidth={1}
          isAnimationActive={false}
          data={data}
          dataKey="z"
          dot={false}
          stroke={
            selectedAxis == null || selectedAxis == 'z' ? '#0000ff' : '#ddd'
          }
        />
      </LineChart>
    </>
  );
};

export default ComPreviewChart;
