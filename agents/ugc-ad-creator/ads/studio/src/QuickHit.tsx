import React from 'react';
import {AbsoluteFill, Sequence, staticFile} from 'remotion';
import {TalkingHead} from './TalkingHead';
import {WordCaptions, Word} from './Captions';
import {HookTitle, CtaPill, SlideUpPanel, BrandLockup, CommentCard} from './Overlays';
import {SfxTrack, MusicBed, SfxItem, MusicSpec} from './Sound';
import {Visual, VisualSpec, isLight} from './Visual';
import {W, H, FPS, Punch, Placeholder} from './lib';

// "Quick hit" flow — ONE head clip (8–11s), fast cuts. Best for Gen-Z-energy
// presenters and short punchy scripts. Scene times are props.
//
// S1 0–s1At      TH + hook title (or comment card)
// S2 s1At–s2At   split: TH / product visual panel
// S3 s2At–s3At   full-bleed product visual (VO continues)
// S4 s3At–endAt  TH; lockup + CTA at ctaAt (absolute seconds)
export const QUICK_HIT_FALLBACK_FRAMES = Math.round(10.5 * FPS);

export type QuickHitProps = {
  hookLines: string[];
  comment?: {user: string; text: string} | null; // reply-to-comment hook skin instead of the title
  head: string | null;
  captions: Word[];
  sfx: SfxItem[];
  music: MusicSpec;
  splitVisual: VisualSpec;
  fullVisual: VisualSpec;
  fullPunch?: [number, number];
  s1At?: number;
  s2At?: number;
  s3At?: number;
  ctaAt?: number;
  endAt: number;
};

export const QuickHit: React.FC<QuickHitProps> = ({
  hookLines,
  comment = null,
  head,
  captions,
  sfx = [],
  music = null,
  splitVisual,
  fullVisual,
  fullPunch = [1.0, 1.15],
  s1At = 1.5,
  s2At = 3.5,
  s3At = 5.5,
  ctaAt,
  endAt = 8.0,
}) => {
  const f = (s: number) => Math.round(s * FPS);
  const CTA = ctaAt ?? s3At + 0.25;
  const PANEL_TOP = 960;

  return (
    <AbsoluteFill style={{background: 'black'}}>
      <Sequence from={0} durationInFrames={f(endAt)} name="head-video">
        <AbsoluteFill>
          <Sequence from={0} durationInFrames={f(s1At)} name="S1-hook">
            <Punch from={1.02} to={1.12}>
              {head ? <TalkingHead src={staticFile(head)} boxW={W} boxH={H} /> : <Placeholder label="talking head" />}
            </Punch>
            {comment ? <CommentCard user={comment.user} text={comment.text} appearAt={0.1} /> : <HookTitle lines={hookLines} appearAt={0.12} />}
          </Sequence>
          <Sequence from={f(s1At)} durationInFrames={f(s2At - s1At)} name="S2-split">
            {head ? <TalkingHead src={staticFile(head)} boxW={W} boxH={1050} trimBefore={f(s1At)} zoom={1.15} /> : <Placeholder label="talking head" />}
            <SlideUpPanel appearAt={0.1} top={PANEL_TOP} height={H - PANEL_TOP}>
              {splitVisual ? <Visual spec={splitVisual} boxW={W} boxH={H - PANEL_TOP} /> : <Placeholder label="split visual" />}
            </SlideUpPanel>
          </Sequence>
          <Sequence from={f(s2At)} durationInFrames={f(s3At - s2At)} name="S3-fullbleed">
            <AbsoluteFill style={{background: isLight(fullVisual) ? '#fff' : '#000'}}>
              <Punch from={fullPunch[0]} to={fullPunch[1]}>
                {fullVisual ? <Visual spec={fullVisual} boxW={W} boxH={H} /> : <Placeholder label="full-bleed visual" />}
              </Punch>
            </AbsoluteFill>
            {head ? (
              <div style={{opacity: 0}}>
                <TalkingHead src={staticFile(head)} boxW={1} boxH={1} trimBefore={f(s2At)} />
              </div>
            ) : null}
          </Sequence>
          <Sequence from={f(s3At)} durationInFrames={f(endAt - s3At)} name="S4-outro">
            <Punch from={1.0} to={1.1}>
              {head ? <TalkingHead src={staticFile(head)} boxW={W} boxH={H} trimBefore={f(s3At)} /> : <Placeholder label="talking head" />}
            </Punch>
            <BrandLockup appearAt={CTA - s3At} />
            <CtaPill appearAt={CTA - s3At} />
          </Sequence>
        </AbsoluteFill>
      </Sequence>

      <WordCaptions words={captions} lightRanges={isLight(fullVisual) ? [[s2At, s3At]] : undefined} />
      <SfxTrack items={sfx} />
      <MusicBed music={music} totalDuration={endAt} />
    </AbsoluteFill>
  );
};
