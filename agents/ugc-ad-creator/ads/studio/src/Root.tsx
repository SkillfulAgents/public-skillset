import React from 'react';
import {Composition, getInputProps} from 'remotion';
import {ClassicF1, ClassicF1Props, CLASSIC_F1_FALLBACK_FRAMES} from './ClassicF1';
import {QuickHit, QuickHitProps, QUICK_HIT_FALLBACK_FRAMES} from './QuickHit';
import {FPS, H, W} from './lib';

// Per-ad values live in props-<ad-id>-{nomusic,music}.json and are passed with
// --props at render time. Do NOT put style keys here — style lives in theme.ts.
// New flows: add a comp file + one <Composition> below.

const classicDefaults: ClassicF1Props = {
  hookLines: ['Hook line one', 'hook line two'],
  headA: null,
  headB: null,
  captions: [],
  sfx: [],
  music: null,
  splitVisual: null,
  fullVisual: null,
  s2At: 2.3,
  s3At: 6.8,
  s4At: 9.6,
  ctaAt: 1.3,
  endAt: 13.4,
};

const quickDefaults: QuickHitProps = {
  hookLines: ['Hook line one', 'hook line two'],
  comment: null,
  head: null,
  captions: [],
  sfx: [],
  music: null,
  splitVisual: null,
  fullVisual: null,
  s1At: 1.5,
  s2At: 3.5,
  s3At: 5.5,
  endAt: 8.0,
};

export const Root: React.FC = () => {
  const input = getInputProps();
  return (
    <>
      <Composition
        id="ClassicF1"
        component={ClassicF1}
        durationInFrames={CLASSIC_F1_FALLBACK_FRAMES}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{...classicDefaults, ...(input as Partial<ClassicF1Props>)}}
        calculateMetadata={({props}) => ({durationInFrames: Math.round(((props.endAt ?? 13.4) as number) * FPS)})}
      />
      <Composition
        id="QuickHit"
        component={QuickHit}
        durationInFrames={QUICK_HIT_FALLBACK_FRAMES}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{...quickDefaults, ...(input as Partial<QuickHitProps>)}}
        calculateMetadata={({props}) => ({durationInFrames: Math.round(((props.endAt ?? 8.0) as number) * FPS)})}
      />
    </>
  );
};
