import React from 'react';
import {OffthreadVideo} from 'remotion';

// Talking-head video, cover-cropped into a box. src is a staticFile URL.
// startFrom/endAt are in composition frames handled by the parent <Sequence>.
export const TalkingHead: React.FC<{
  src: string;
  boxW: number;
  boxH: number;
  trimBefore?: number; // frames trimmed from the start of the source video
  focusY?: number; // 0..1, where the face sits vertically in the source
  muted?: boolean;
  zoom?: number;
}> = ({src, boxW, boxH, trimBefore = 0, focusY = 0.32, muted = false, zoom = 1}) => {
  return (
    <div style={{position: 'absolute', width: boxW, height: boxH, overflow: 'hidden', background: '#111'}}>
      <OffthreadVideo
        src={src}
        trimBefore={trimBefore}
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
};
