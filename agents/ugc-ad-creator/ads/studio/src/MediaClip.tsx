import React from 'react';
import {Img, OffthreadVideo, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

// Product visuals supplied by the user (screenshots, product photos, screen
// recordings) — the alternative to HtmlClip when there is an asset library.
//
// StillClip: a screenshot/photo with a slow drift (Ken Burns) so the shot is
// never static. `from`/`to` are {scale, x, y} where x/y are % offsets of the
// image center relative to the box center.
export type KenBurns = {scale: number; x?: number; y?: number};

export const StillClip: React.FC<{
  src: string; // staticFile(...) URL
  boxW: number;
  boxH: number;
  from?: KenBurns;
  to?: KenBurns;
  fit?: 'cover' | 'contain';
  background?: string;
}> = ({src, boxW, boxH, from = {scale: 1.05}, to = {scale: 1.18}, fit = 'cover', background = '#fff'}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], {extrapolateRight: 'clamp'});
  const s = from.scale + (to.scale - from.scale) * p;
  const x = (from.x ?? 0) + ((to.x ?? 0) - (from.x ?? 0)) * p;
  const y = (from.y ?? 0) + ((to.y ?? 0) - (from.y ?? 0)) * p;
  return (
    <div style={{position: 'absolute', width: boxW, height: boxH, overflow: 'hidden', background}}>
      <Img
        src={src}
        style={{
          width: '100%',
          height: '100%',
          objectFit: fit,
          transform: `translate(${x}%, ${y}%) scale(${s})`,
          transformOrigin: '50% 50%',
        }}
      />
    </div>
  );
};

// VideoClip: a screen recording or product video, cover-cropped into a box,
// muted by default (the talking head carries the audio).
export const VideoClip: React.FC<{
  src: string;
  boxW: number;
  boxH: number;
  trimBefore?: number; // frames
  playbackRate?: number;
  zoom?: number;
  focusY?: number; // 0..1
  muted?: boolean;
}> = ({src, boxW, boxH, trimBefore = 0, playbackRate = 1, zoom = 1, focusY = 0.5, muted = true}) => (
  <div style={{position: 'absolute', width: boxW, height: boxH, overflow: 'hidden', background: '#111'}}>
    <OffthreadVideo
      src={src}
      trimBefore={trimBefore}
      playbackRate={playbackRate}
      muted={muted}
      style={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: `50% ${focusY * 100}%`,
        transform: `scale(${zoom})`,
        transformOrigin: `50% ${focusY * 100}%`,
      }}
    />
  </div>
);
