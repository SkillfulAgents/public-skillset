import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT, theme} from './theme';

export type Word = {text: string; start: number; end: number; emphasis?: boolean};

// TikTok-style word-pop captions: one word/phrase at a time, popping in with
// a spring. Style locked in theme.ts (white Inter 500, subtle shadow).
export const WordCaptions: React.FC<{
  words: Word[];
  y?: number; // vertical center of caption line, composition px
  fontSize?: number;
  color?: string;
  emphasisColor?: string;
  lightRanges?: [number, number][]; // [start,end) seconds where the scene bg is light → dark text in white pill
  yOverrides?: [number, number, number][]; // [start,end,y) seconds → move caption line for that window
}> = ({
  words,
  y = theme.caption.y,
  fontSize = theme.caption.fontSize,
  color = theme.caption.color,
  emphasisColor = theme.caption.emphasisColor,
  lightRanges,
  yOverrides,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const active = words.find((w) => t >= w.start && t < w.end);
  if (!active) return null;

  const onLight = lightRanges?.some(([s, e]) => t >= s && t < e) ?? false;
  const yNow = yOverrides?.find(([s, e]) => t >= s && t < e)?.[2] ?? y;
  const box = theme.caption.lightBox;
  const local = (t - active.start) * fps;
  const pop = spring({frame: local, fps, config: {damping: 14, stiffness: 320, mass: 0.6}});
  const scale = interpolate(pop, [0, 1], [0.82, 1]);

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: yNow,
        display: 'flex',
        justifyContent: 'center',
        transform: `translateY(-50%)`,
      }}
    >
      <div
        style={{
          fontFamily: FONT,
          fontWeight: theme.caption.fontWeight,
          fontSize,
          lineHeight: theme.caption.lineHeight,
          textAlign: 'center',
          color: onLight ? theme.caption.darkColor : active.emphasis ? emphasisColor : color,
          textShadow: onLight ? 'none' : theme.caption.shadow,
          background: onLight ? box.bg : 'none',
          borderRadius: onLight ? box.radius : 0,
          boxShadow: onLight ? box.shadow : 'none',
          transform: `scale(${scale})`,
          whiteSpace: 'pre-wrap',
          padding: onLight ? `${box.paddingY}px ${box.paddingX}px` : '0 60px',
          margin: onLight ? '0 60px' : 0,
          letterSpacing: theme.caption.letterSpacing,
        }}
      >
        {active.text}
      </div>
    </div>
  );
};

// Evenly distribute phrase timings across a time range (fallback when no
// word-level transcript timestamps are available).
export const spreadWords = (phrases: string[], start: number, end: number, emphasisLast = false): Word[] => {
  const weights = phrases.map((p) => Math.max(p.length, 4));
  const total = weights.reduce((a, b) => a + b, 0);
  const out: Word[] = [];
  let t = start;
  phrases.forEach((p, i) => {
    const d = ((end - start) * weights[i]) / total;
    out.push({text: p, start: t, end: t + d, emphasis: emphasisLast && i === phrases.length - 1});
    t += d;
  });
  return out;
};
