import { usePreviewPredictionQuery } from '@/hooks';

import { BlurFilter, TextStyle } from 'pixi.js';
import {
  Stage,
  Container,
  Sprite,
  Text,
  SimpleMesh,
  Graphics,
} from '@pixi/react';
import { useState } from 'react';

type props = {
  predictionId: number;
  cameraName1: string;
  cameraName2: string;
  frames: number[];
};

const PreviewPrediction: React.FC<props> = ({
  predictionId,
  cameraName1,
  cameraName2,
  frames,
}) => {
  const { data, isLoading, isError } = usePreviewPredictionQuery(
    predictionId,
    frames,
    cameraName1,
    cameraName2
  );

  const [frameIdx, setFrameIdx] = useState(0);

  if (isLoading) {
    return <div>Loading</div>;
  }

  if (isError || !data) {
    return <div>Error</div>;
  }

  const nJoints = data.frames[frameIdx].pts_cam1.length;
  const nFrames = data.frames.length;

  console.log('NFRAMES', nFrames);
  const incFrameIdx = () => {
    // setFrameIdx((x) => (x + 1) % nFrames);
    setFrameIdx((x) => (x + 1) % nFrames);

    console.log('INCING FRAME INDEX');
  };
  const decFrameIdx = () => {
    setFrameIdx((x) => (x + nFrames - 1) % nFrames);
    console.log("DEC'ING");
  };

  return (
    <div>
      <div className="flex flex-row gap-4">
        <div
          onClick={decFrameIdx}
          className="cursor-pointer border-2 border-blue-500 select-none"
        >
          DEC FRAME
        </div>
        <div
          className="cursor-pointer border-2 border-blue-500 select-none"
          onClick={incFrameIdx}
        >
          INC FRAME
        </div>
        <div>current frame: {frameIdx}</div>
      </div>

      <Stage width={1920} height={1200} options={{ background: 0x656565 }}>
        <Sprite
          image={data!.frames[frameIdx].static_url_cam1}
          anchor={0}
          scale={{ x: 1, y: 1 }}
          x={0}
          y={0}
          alpha={1}
        />
        <Graphics
          draw={(g) => {
            g.beginFill(0xff0000);
            g.lineStyle(1);

            for (let i = 0; i < data.frames[frameIdx].pts_cam1.length; i++) {
              const pt = data.frames[frameIdx].pts_cam1[i];
              g.drawCircle(pt[0], pt[1], 5);
            }
          }}
        />
      </Stage>
    </div>
  );
};

export default PreviewPrediction;
