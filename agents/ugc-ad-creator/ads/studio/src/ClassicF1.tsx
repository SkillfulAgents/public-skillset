import React from 'react';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {TalkingHead} from './TalkingHead';
import {WordCaptions, Word} from './Captions';
import {HookTitle, CtaPill, SlideUpPanel, BrandLockup} from './Overlays';
import {SfxTrack, MusicBed, SfxItem, MusicSpec} from './Sound';
import {Visual, VisualSpec, isLight} from './Visual';
import {W, H, FPS, Punch, Placeholder} from './lib';

// F1 "Classic" flow — the house default. Two talking-head clips (A: hook +
// setup, B: payoff + CTA), all scene times are props (derived from whisper word
// timings) so one comp serves every ad in this flow.
//
// S1 0–s2At      full TH + hook title
// S2 s2At–s3At   split: TH top / product visual slides up in a bottom panel
// S3 s3At–s4At   full-bleed product visual punch-in, VO continues from head B
// S4 s4At–endAt  full TH (head B) + brand lockup + CTA card at ctaAt (relative to s4At)
export const CLASSIC_F1_FALLBACK_FRAMES = Math.round(13.4 * FPS);

export type ClassicF1Props = {
  hookLines: string[];
  headA: string | null; // public/heads/<ad-id>-A.mp4 — spans S1+S2
  headB: string | null; // public/heads/<ad-id>-B.mp4 — spans S3+S4
  captions: Word[];
  sfx: SfxItem[];
  music: MusicSpec;
  splitVisual: VisualSpec;
  fullVisual: VisualSpec;
  fullPunch?: [number, number];
  fullOrigin?: string;
  s2At: number;
  s3At: number;
  s4At: number;
  ctaAt: number; // seconds after s4At
  endAt: number;
};

export const ClassicF1: React.FC<ClassicF1Props> = ({
  hookLines,
  headA,
  headB,
  captions,
  sfx = [],
  music = null,
  splitVisual,
  fullVisual,
  fullPunch = [1.0, 1.12],
  fullOrigin,
  s2At = 2.3,
  s3At = 6.8,
  s4At = 9.6,
  ctaAt = 1.3,
  endAt = 13.4,
}) => {
  const f = (s: number) => Math.round(s * FPS);
  const PANEL_TOP = 960;

  return (
    <AbsoluteFill style={{background: 'black'}}>
      {/* one continuous head-A video under S1+S2 so audio never cuts */}
      <Sequence from={0} durationInFrames={f(s3At)} name="head-A">
        <AbsoluteFill>
          <Sequence from={0} durationInFrames={f(s2At)} name="S1-hook">
            <Punch from={1.02} to={1.1}>
              {headA ? <TalkingHead src={staticFile(headA)} boxW={W} boxH={H} /> : <Placeholder label="talking head A" />}
            </Punch>
            <HookTitle lines={hookLines} appearAt={0.15} />
          </Sequence>
          <Sequence from={f(s2At)} durationInFrames={f(s3At - s2At)} name="S2-split">
            {headA ? <TalkingHead src={staticFile(headA)} boxW={W} boxH={1050} trimBefore={f(s2At)} zoom={1.15} /> : <Placeholder label="talking head A" />}
            <SlideUpPanel appearAt={0.12} top={PANEL_TOP} height={H - PANEL_TOP}>
              {splitVisual ? <Visual spec={splitVisual} boxW={W} boxH={H - PANEL_TOP} /> : <Placeholder label="split visual" />}
            </SlideUpPanel>
          </Sequence>
        </AbsoluteFill>
      </Sequence>

      {/* S3: full-bleed product visual, audio from head B (hidden) */}
      <Sequence from={f(s3At)} durationInFrames={f(s4At - s3At)} name="S3-fullbleed">
        <AbsoluteFill style={{background: isLight(fullVisual) ? 'white' : 'black'}}>
          <Punch from={fullPunch[0]} to={fullPunch[1]} origin={fullOrigin}>
            {fullVisual ? <Visual spec={fullVisual} boxW={W} boxH={H} /> : <Placeholder label="full-bleed visual" />}
          </Punch>
        </AbsoluteFill>
        {headB ? (
          <div style={{opacity: 0}}>
            <TalkingHead src={staticFile(headB)} boxW={1} boxH={1} />
          </div>
        ) : null}
      </Sequence>

      {/* S4: head B + lockup + CTA */}
      <Sequence from={f(s4At)} durationInFrames={f(endAt - s4At)} name="S4-outro">
        <Punch from={1.0} to={1.08}>
          {headB ? <TalkingHead src={staticFile(headB)} boxW={W} boxH={H} trimBefore={f(s4At - s3At)} /> : <Placeholder label="talking head B" />}
        </Punch>
        <BrandLockup appearAt={ctaAt} />
        <CtaPill appearAt={ctaAt} />
      </Sequence>

      <WordCaptions words={captions} lightRanges={isLight(fullVisual) ? [[s3At, s4At]] : undefined} />
      <SfxTrack items={sfx} />
      <MusicBed music={music} totalDuration={endAt} />
    </AbsoluteFill>
  );
};
