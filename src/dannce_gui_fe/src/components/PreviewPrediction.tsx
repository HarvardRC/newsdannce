import { useEffect, useRef, useState } from 'react';

import { Button } from './ui/button';
import { PixiPreview } from '@/utils/pixiFunctions';
import { PreviewPredictionType } from '@/api';
import { useDebounce, useWindowSize } from '@/hooks';

type props = {
  data: PreviewPredictionType;
};

const PreviewPrediction: React.FC<props> = ({ data }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [frameIdx, setFrameIdx] = useState(0);
  const allPreviewInstancesRef = useRef<Record<number, PixiPreview>>({});
  const _size = useWindowSize();
  const sizeDebounced = useDebounce(_size, 400);
  /** size is debounced 400 ms, so it waits until user finishes dragging window to re-render */

  const incrFrameBy = (n: number) => {
    const maxNoFrames = data.frames.length;
    setFrameIdx((frame) => (frame + maxNoFrames + n) % maxNoFrames);
  };

  useEffect(() => {
    // const mountElement = mountRef.current!;
    const previewInstance = new PixiPreview();
    // const ac = new AbortController();
    let promiseChain = previewInstance.init(mountRef, data);
    promiseChain = promiseChain.then(() => {
      allPreviewInstancesRef.current[previewInstance.id] = previewInstance;
    });
    promiseChain = promiseChain.then(() => {
      previewInstance.update(0);
    });

    return () => {
      promiseChain
        .then(() => previewInstance.destroy())
        .then(() => delete allPreviewInstancesRef.current[previewInstance.id]);
    };
  }, []);

  useEffect(() => {
    console.log(
      'Updating previewInstances because frameIdx or window size changed'
    );
    for (const [, app] of Object.entries(allPreviewInstancesRef.current)) {
      if (app.data != null) {
        app.update(frameIdx);
      }
    }
  }, [frameIdx, sizeDebounced]);

  return (
    <div className="my-8">
      <div className="flex flex-row gap-4 my-2">
        {/* BUTTON CONTAINER */}
        <Button onClick={() => incrFrameBy(-1)} variant={'default'}>
          Frame -
        </Button>
        <Button onClick={() => incrFrameBy(+1)} variant={'default'}>
          Frame +
        </Button>
      </div>

      <div>
        Frame: {data.frames[frameIdx].absolute_frameno} ({frameIdx + 1}/
        {data.n_frames})
      </div>
      <div ref={mountRef} className="border-2 h-[800px] border-red-300" />
    </div>
  );
};

export default PreviewPrediction;
