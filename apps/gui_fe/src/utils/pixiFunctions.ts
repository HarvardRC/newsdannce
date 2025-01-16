import { PreviewPredictionType } from '@/api';
import * as PIXI from 'pixi.js';
import { RefObject } from 'react';

export class PixiPreview {
  id: number;
  data: PreviewPredictionType | null = null;
  app: PIXI.Application | null = null;
  inited: boolean = false;
  currentFrame: number = -1;
  frameTextures: PIXI.Texture[] = [];
  frameSprites: PIXI.Sprite[] = [];
  currentSpriteRef1: PIXI.Sprite | null = null;
  currentSpriteRef2: PIXI.Sprite | null = null;

  // specific elements for this frame
  frameContainer1: PIXI.Container | null = null;
  frameContainer2: PIXI.Container | null = null;
  graphics1: PIXI.Graphics | null = null;
  graphics2: PIXI.Graphics | null = null;

  constructor() {
    this.id = Math.floor(Math.random() * 1000);
    console.log('CONSTRUCTED', this.id);
    this.app = new PIXI.Application();
  }

  public async init(
    mountRef: RefObject<HTMLDivElement>,
    data: PreviewPredictionType
    // signal: AbortSignal
  ) {
    if (this.inited === true) {
      throw Error(
        `Trying to re-initialize a PixiPreview (inited=true): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to initialize deleted PixiPreview (app=null): ${this.id}`
      );
    }

    await this.app.init({
      background: `0xfff`,
      // hello: true,
      // width: 600,
      // height: 400,
      resizeTo: mountRef.current || undefined,
      // preference: 'webgpu',
    });
    this.inited = true;
    mountRef.current!.appendChild(this.app.canvas);
    this.data = data;
    this.currentFrame = 0;

    // load textures from the web
    for (let i = 0; i < data.n_frames; i++) {
      const thisTexture1 = await PIXI.Assets.load(
        data.frames[i].static_url_cam1
      );
      this.frameSprites[i] = new PIXI.Sprite(thisTexture1);

      const thisTexture2 = await PIXI.Assets.load(
        data.frames[i].static_url_cam2
      );
      this.frameSprites[i + data.n_frames] = new PIXI.Sprite(thisTexture2);
    }

    this.frameContainer1 = new PIXI.Container();
    this.frameContainer2 = new PIXI.Container();

    // Initiliaze graphics
    this.graphics1 = new PIXI.Graphics();
    this.graphics1.zIndex = 1;

    this.graphics2 = new PIXI.Graphics();
    this.graphics2.zIndex = 1;

    // Create sprites
    this.currentSpriteRef1 = this.frameSprites[0];
    this.frameContainer1.addChild(this.currentSpriteRef1);
    this.frameContainer1.addChild(this.graphics1);

    this.currentSpriteRef2 = this.frameSprites[0 + this.data.n_frames];
    this.frameContainer2.addChild(this.currentSpriteRef2);
    this.frameContainer2.addChild(this.graphics2);

    this.app.stage.addChild(this.frameContainer1);
    this.app.stage.addChild(this.frameContainer2);

    // console.log('DONE LOADING ALL', this.id);
  }

  public async update(newFrame: number) {
    if (this.inited === false) {
      throw Error(
        `Trying to update a non-init'd a SlowResrouce (inited=false): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to update a destoryed SlowResrouce (app=null): ${this.id}`
      );
    }
    this.currentFrame = newFrame;

    // Swap frame sprites
    this.frameContainer1!.removeChild(this.currentSpriteRef1!);
    this.frameContainer2!.removeChild(this.currentSpriteRef2!);
    this.currentSpriteRef1 = this.frameSprites[newFrame];
    this.currentSpriteRef2 = this.frameSprites[newFrame + this.data!.n_frames];
    this.frameContainer1!.addChild(this.currentSpriteRef1);
    this.frameContainer2!.addChild(this.currentSpriteRef2);

    // Reset keypoints
    this.graphics1!.clear();
    this.graphics2!.clear();

    // draw the keypoints for each camera frame
    for (let i = 0; i < this.data!.n_joints; i++) {
      const this_pt1 = this.data!.frames[this.currentFrame].pts_cam1[i];
      this.graphics1!.circle(this_pt1[0], this_pt1[1], 5);
      this.graphics1!.fill(0xff00ff);

      const this_pt2 = this.data!.frames[this.currentFrame].pts_cam2[i];
      this.graphics2!.circle(this_pt2[0], this_pt2[1], 5);
      this.graphics2!.fill(0xff00ff);
    }

    // Update transform in case screen size has changeda
    // MAYBE: memoize(size) to avoid rerunning unnecessarily(?)
    const dpiHeight = this.data!.frame_height / this.app.screen.height;
    const dpiWidth = (this.data!.frame_width * 2) / this.app.screen.width;
    // dpi is min dpiWidth, dpiHeight
    const dpi = dpiHeight > dpiWidth ? dpiHeight : dpiWidth;

    this.frameContainer1!.updateTransform({
      scaleX: 1 / dpi,
      scaleY: 1 / dpi,
    });

    this.frameContainer2!.updateTransform({
      scaleX: 1 / dpi,
      scaleY: 1 / dpi,
      // offset the 2nd to be halfway across the page
      x: this.app.screen.width / 2,
    });
  }

  public destroy() {
    // console.log('DESTROYED', this.id);
    if (this.inited === false) {
      throw Error(
        `Trying to destroy a non-init'd a SlowResrouce (inited=false): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to destroy an already destoryed SlowResrouce (app=null): ${this.id}`
      );
    }
    this.app.destroy(
      {
        removeView: true,
      },
      {
        children: true,
        texture: true,
        context: true,
        style: true,
        // textureSource: true, // don't unload the textures so other canvases can use them
      }
    );
    this.app = null;
  }
}

// TESTING -- TODO: REMOVE
// ###########################################################################################

export class PixiPreviewVideo {
  id: number;
  data: PreviewPredictionType | null = null;
  app: PIXI.Application | null = null;
  inited: boolean = false;
  currentFrame: number = -1;
  frameTextures: PIXI.Texture[] = [];
  frameSprites: PIXI.Sprite[] = [];
  currentSpriteRef1: PIXI.Sprite | null = null;
  currentSpriteRef2: PIXI.Sprite | null = null;

  // specific elements for this frame
  frameContainer1: PIXI.Container | null = null;
  frameContainer2: PIXI.Container | null = null;
  graphics1: PIXI.Graphics | null = null;
  graphics2: PIXI.Graphics | null = null;

  constructor() {
    this.id = Math.floor(Math.random() * 1000);
    console.log('CONSTRUCTED', this.id);
    this.app = new PIXI.Application();
  }

  public async init(
    mountRef: RefObject<HTMLDivElement>,
    data: PreviewPredictionType
    // signal: AbortSignal
  ) {
    if (this.inited === true) {
      throw Error(
        `Trying to re-initialize a PixiPreview (inited=true): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to initialize deleted PixiPreview (app=null): ${this.id}`
      );
    }

    await this.app.init({
      background: `0xfff`,
      // hello: true,
      // width: 600,
      // height: 400,
      resizeTo: mountRef.current || undefined,
      // preference: 'webgpu',
    });
    this.inited = true;
    mountRef.current!.appendChild(this.app.canvas);
    this.data = data;
    this.currentFrame = 0;

    // load textures from the web
    for (let i = 0; i < data.n_frames; i++) {
      const thisTexture1 = await PIXI.Assets.load(
        data.frames[i].static_url_cam1
      );
      this.frameSprites[i] = new PIXI.Sprite(thisTexture1);

      const thisTexture2 = await PIXI.Assets.load(
        data.frames[i].static_url_cam2
      );
      this.frameSprites[i + data.n_frames] = new PIXI.Sprite(thisTexture2);
    }

    this.frameContainer1 = new PIXI.Container();
    this.frameContainer2 = new PIXI.Container();

    // Initiliaze graphics
    this.graphics1 = new PIXI.Graphics();
    this.graphics1.zIndex = 1;

    this.graphics2 = new PIXI.Graphics();
    this.graphics2.zIndex = 1;

    // Create sprites
    this.currentSpriteRef1 = this.frameSprites[0];
    this.frameContainer1.addChild(this.currentSpriteRef1);
    this.frameContainer1.addChild(this.graphics1);

    this.currentSpriteRef2 = this.frameSprites[0 + this.data.n_frames];
    this.frameContainer2.addChild(this.currentSpriteRef2);
    this.frameContainer2.addChild(this.graphics2);

    this.app.stage.addChild(this.frameContainer1);
    this.app.stage.addChild(this.frameContainer2);

    // console.log('DONE LOADING ALL', this.id);
  }

  public async update(newFrame: number) {
    if (this.inited === false) {
      throw Error(
        `Trying to update a non-init'd a SlowResrouce (inited=false): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to update a destoryed SlowResrouce (app=null): ${this.id}`
      );
    }
    this.currentFrame = newFrame;

    // Swap frame sprites
    this.frameContainer1!.removeChild(this.currentSpriteRef1!);
    this.frameContainer2!.removeChild(this.currentSpriteRef2!);
    this.currentSpriteRef1 = this.frameSprites[newFrame];
    this.currentSpriteRef2 = this.frameSprites[newFrame + this.data!.n_frames];
    this.frameContainer1!.addChild(this.currentSpriteRef1);
    this.frameContainer2!.addChild(this.currentSpriteRef2);

    // Reset keypoints
    this.graphics1!.clear();
    this.graphics2!.clear();

    // draw the keypoints for each camera frame
    for (let i = 0; i < this.data!.n_joints; i++) {
      const this_pt1 = this.data!.frames[this.currentFrame].pts_cam1[i];
      this.graphics1!.circle(this_pt1[0], this_pt1[1], 5);
      this.graphics1!.fill(0xff00ff);

      const this_pt2 = this.data!.frames[this.currentFrame].pts_cam2[i];
      this.graphics2!.circle(this_pt2[0], this_pt2[1], 5);
      this.graphics2!.fill(0xff00ff);
    }

    // Update transform in case screen size has changeda
    // MAYBE: memoize(size) to avoid rerunning unnecessarily(?)
    const dpiHeight = this.data!.frame_height / this.app.screen.height;
    const dpiWidth = (this.data!.frame_width * 2) / this.app.screen.width;
    // dpi is min dpiWidth, dpiHeight
    const dpi = dpiHeight > dpiWidth ? dpiHeight : dpiWidth;

    this.frameContainer1!.updateTransform({
      scaleX: 1 / dpi,
      scaleY: 1 / dpi,
    });

    this.frameContainer2!.updateTransform({
      scaleX: 1 / dpi,
      scaleY: 1 / dpi,
      // offset the 2nd to be halfway across the page
      x: this.app.screen.width / 2,
    });
  }

  public destroy() {
    // console.log('DESTROYED', this.id);
    if (this.inited === false) {
      throw Error(
        `Trying to destroy a non-init'd a SlowResrouce (inited=false): ${this.id}`
      );
    }
    if (this.app === null) {
      throw Error(
        `Trying to destroy an already destoryed SlowResrouce (app=null): ${this.id}`
      );
    }
    this.app.destroy(
      {
        removeView: true,
      },
      {
        children: true,
        texture: true,
        context: true,
        style: true,
        // textureSource: true, // don't unload the textures so other canvases can use them
      }
    );
    this.app = null;
  }
}
