import { Button } from '@/components/ui/button';

import { PixiPreview, PixiPreviewVideo } from '@/utils/pixiFunctions';
import { PreviewPredictionType } from '@/api';
import { useDebounce, useWindowSize } from '@/hooks';
import { useEffect, useReducer, useRef, useState } from 'react';
import { Application, Assets, Graphics, Sprite, Texture } from 'pixi.js';

export default function TestPage() {
  const ref = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [listenRerender, forceRerender] = useReducer((x) => x + 1, 0);

  const handlePlay = () => {
    console.log('Played!!');
  };

  useEffect(() => {
    const asyncFunction = async () => {
      if (ref.current != null && videoRef.current != null) {
        ref.current.width = 640; //videoRef.current.width;
        ref.current.height = 480;
        videoRef.current.height;
        const ctx = ref.current.getContext('2d')!;
        console.log('Canvas context is ', ctx);
        ctx.drawImage(videoRef.current, 0, 0);
        // do something with the context

        const app = new Application();
        await app.init({ resizeTo: window });
        document.body.appendChild(app.canvas);
        // Create play button that can be used to trigger the video
        const button = new Graphics()
          .roundRect(0, 0, 100, 100, 10)
          .fill(0xffffff, 0.5)
          .beginPath()
          .moveTo(36, 30)
          .lineTo(36, 70)
          .lineTo(70, 50)
          .closePath()
          .fill(0xffffff);

        // Position the button
        button.x = (app.screen.width - button.width) / 2;
        button.y = (app.screen.height - button.height) / 2;

        // Enable interactivity on the button
        button.eventMode = 'static';
        button.cursor = 'pointer';

        // Add to the stage
        app.stage.addChild(button);
        const texture = Texture.from(videoRef.current);

        // Listen for a click/tap event to start playing the video
        // this is useful for some mobile platforms. For example:
        // ios9 and under cannot render videos in PIXI without a
        // polyfill - https://github.com/bfred-it/iphone-inline-video
        // ios10 and above require a click/tap event to render videos
        // that contain audio in PIXI. Videos with no audio track do
        // not have this requirement
        button.on('pointertap', () => {
          // Don't need the button anymore
          button.destroy();

          // Create a new Sprite using the video texture (yes it's that easy)
          const videoSprite = new Sprite(texture);

          // Stretch to fill the whole screen
          videoSprite.width = app.screen.width;
          videoSprite.height = app.screen.height;

          app.stage.addChild(videoSprite);
        });
      } else {
        console.log('canvasRef or videoRef is unset');
      }
    };
    asyncFunction();
  }, [listenRerender]);

  return (
    <div>
      <div>Hello world</div>
      <Button onClick={forceRerender}>Redraw</Button>
      <video
        ref={videoRef}
        onPlay={handlePlay}
        id="tmp-canvas"
        controls
        autoPlay
        muted
        style={{
          display: 'none',
        }}
      >
        <source
          src="http://localhost:7901/v1/video_folder/2/stream?camera_name=Camera1"
          type="video/mp4"
        />
      </video>
      <canvas ref={ref} />
    </div>
  );
}
