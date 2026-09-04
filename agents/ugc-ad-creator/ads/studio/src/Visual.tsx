import React from 'react';
import {staticFile} from 'remotion';
import {HtmlClip} from './HtmlClip';
import {StillClip, VideoClip} from './MediaClip';
import {staticSrc} from './lib';

// One prop shape for "the product visual in this scene", whichever kind it is.
// Comps take a VisualSpec and render it with <Visual>, so the same flow works
// for an HTML animation, a screenshot with drift, or a screen recording.
export type VisualSpec =
  | {kind: 'html'; src: string; startFrom?: number; speed?: number; fit?: 'cover' | 'contain' | 'width'; designW?: number; designH?: number; offsetX?: number}
  | {kind: 'still'; src: string; from?: {scale: number; x?: number; y?: number}; to?: {scale: number; x?: number; y?: number}; fit?: 'cover' | 'contain'; background?: string}
  | {kind: 'video'; src: string; trimBefore?: number; playbackRate?: number; zoom?: number; focusY?: number}
  | null;

export const Visual: React.FC<{spec: VisualSpec; boxW: number; boxH: number}> = ({spec, boxW, boxH}) => {
  if (!spec) return null;
  if (spec.kind === 'html') {
    const {kind, src, fit = 'width', ...rest} = spec;
    return <HtmlClip src={staticSrc(src)} boxW={boxW} boxH={boxH} fit={fit} {...rest} />;
  }
  if (spec.kind === 'still') {
    const {kind, src, ...rest} = spec;
    return <StillClip src={staticFile(src)} boxW={boxW} boxH={boxH} {...rest} />;
  }
  const {kind, src, ...rest} = spec;
  return <VideoClip src={staticFile(src)} boxW={boxW} boxH={boxH} {...rest} />;
};

// Light scenes (white UI screenshots, white-background animations) need dark
// captions — comps pass the relevant time ranges to WordCaptions.
export const isLight = (spec: VisualSpec) => !!spec && (spec.kind === 'still' ? (spec.background ?? '#fff') !== '#000' : spec.kind === 'html');
