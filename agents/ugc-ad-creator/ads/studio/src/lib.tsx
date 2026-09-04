import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

// House format: vertical TikTok/Reels
export const W = 1080;
export const H = 1920;
export const FPS = 30;

export const secToFrames = (s: number) => Math.round(s * FPS);

// Slight continuous punch-zoom keeps shots alive — wrap every scene in one.
export const Punch: React.FC<{from?: number; to?: number; origin?: string; children: React.ReactNode}> = ({from = 1, to = 1.06, origin, children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const s = interpolate(frame, [0, durationInFrames], [from, to]);
  return <AbsoluteFill style={{transform: `scale(${s})`, ...(origin ? {transformOrigin: origin} : {})}}>{children}</AbsoluteFill>;
};

export const Placeholder: React.FC<{label: string}> = ({label}) => (
  <AbsoluteFill style={{background: 'linear-gradient(160deg,#1b1035,#3d1257)', alignItems: 'center', justifyContent: 'center'}}>
    <div style={{color: 'rgba(255,255,255,0.5)', fontFamily: 'Inter, sans-serif', fontWeight: 700, fontSize: 44}}>{label}</div>
  </AbsoluteFill>
);

// staticFile() percent-encodes '?' — split off the query string so
// parameterized animation clips (…html?foo=bar) resolve correctly.
import {staticFile as _staticFile} from 'remotion';
export const staticSrc = (s: string) => {
  const i = s.indexOf('?');
  return i < 0 ? _staticFile(s) : _staticFile(s.slice(0, i)) + s.slice(i);
};
