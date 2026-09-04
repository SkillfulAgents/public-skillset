import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONT, theme} from './theme';

// Big hook title that slams in at the top of the frame.
export const HookTitle: React.FC<{lines: string[]; y?: number; appearAt?: number; dark?: boolean}> = ({lines, y = theme.hook.y, appearAt = 0, dark = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < 0) return null;
  const pop = spring({frame: local, fps, config: {damping: 13, stiffness: 260, mass: 0.7}});
  const scale = interpolate(pop, [0, 1], [1.25, 1]);
  const opacity = interpolate(local, [0, 4], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity}}>
      <div style={{transform: `scale(${scale})`, textAlign: 'center'}}>
        {lines.map((l, i) => (
          <div
            key={i}
            style={{
              display: 'block',
              fontFamily: FONT,
              fontWeight: theme.hook.fontWeight,
              fontSize: theme.hook.fontSize,
              lineHeight: theme.hook.lineHeight,
              color: dark ? theme.caption.darkColor : theme.hook.color,
              textShadow: dark ? 'none' : theme.hook.shadow,
              letterSpacing: theme.hook.letterSpacing,
            }}
          >
            {l}
          </div>
        ))}
      </div>
    </div>
  );
};

// Brand lockup — outro only, centered above the CTA card. Renders nothing when
// brand.json has no logo configured.
export const BrandLockup: React.FC<{
  appearAt?: number;
  y?: number;
  width?: number;
  lightRanges?: [number, number][]; // seconds where the scene bg is light → dark lockup
}> = ({appearAt = 0, y = theme.brand.y, width = theme.brand.width, lightRanges}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < 0) return null;
  const t = frame / fps;
  const onLight = lightRanges?.some(([s, e]) => t >= s && t < e) ?? false;
  const src = onLight ? theme.brand.logoDark ?? theme.brand.logo : theme.brand.logo ?? theme.brand.logoDark;
  if (!src) return null;
  const opacity = interpolate(local, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', opacity}}>
      <Img src={staticFile(src)} style={{width, display: 'block', filter: onLight ? 'none' : `drop-shadow(${theme.brand.shadow})`}} />
    </div>
  );
};

// End-card CTA: rounded-corner rectangle, multi-line text (split on \n).
export const CtaPill: React.FC<{text?: string; appearAt: number; y?: number; fontSize?: number}> = ({
  text = theme.cta.text,
  appearAt,
  y = theme.cta.y,
  fontSize = theme.cta.fontSize,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < 0) return null;
  const pop = spring({frame: local, fps, config: {damping: 12, stiffness: 280, mass: 0.8}});
  const pulse = 1 + Math.sin(Math.max(0, local / fps - 0.4) * 4.5) * 0.02;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center'}}>
      <div
        style={{
          transform: `scale(${interpolate(pop, [0, 1], [0.3, 1]) * pulse})`,
          background: theme.cta.bg,
          color: theme.cta.color,
          fontFamily: FONT,
          fontWeight: theme.cta.fontWeight,
          fontSize,
          lineHeight: theme.cta.lineHeight,
          letterSpacing: theme.cta.letterSpacing,
          textAlign: 'center',
          whiteSpace: 'pre',
          padding: `${theme.cta.paddingY}px ${theme.cta.paddingX}px`,
          borderRadius: theme.cta.radius,
          boxShadow: theme.cta.shadow,
        }}
      >
        {text}
      </div>
    </div>
  );
};

// White rounded panel that slides up from the bottom (device-panel look).
export const SlideUpPanel: React.FC<{
  appearAt: number;
  top: number;
  height: number;
  children: React.ReactNode;
  radius?: number;
}> = ({appearAt, top, height, children, radius = 40}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < -1) return null;
  const pop = spring({frame: Math.max(local, 0), fps, config: {damping: 16, stiffness: 160, mass: 0.9}});
  const ty = interpolate(pop, [0, 1], [height * 0.35 + 80, 0]);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top,
        width: 1080,
        height,
        transform: `translateY(${ty}px)`,
        opacity: interpolate(pop, [0, 0.35], [0, 1], {extrapolateRight: 'clamp'}),
        borderRadius: `${radius}px ${radius}px 0 0`,
        overflow: 'hidden',
        background: 'white',
        boxShadow: '0 -18px 60px rgba(0,0,0,0.5)',
      }}
    >
      {children}
    </div>
  );
};

// TikTok-style comment card (reply-to-comment hook skin) — replaces the hook title on frame 1.
export const CommentCard: React.FC<{user: string; text: string; appearAt?: number; y?: number; hideAt?: number}> = ({
  user,
  text,
  appearAt = 0,
  y = 190,
  hideAt,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < 0) return null;
  if (hideAt !== undefined && frame / fps >= hideAt) return null;
  const pop = spring({frame: local, fps, config: {damping: 13, stiffness: 240, mass: 0.8}});
  const scale = interpolate(pop, [0, 1], [0.7, 1]);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center'}}>
      <div
        style={{
          transform: `scale(${scale})`,
          display: 'flex',
          gap: 22,
          alignItems: 'flex-start',
          background: '#ffffff',
          borderRadius: 30,
          padding: '26px 36px',
          maxWidth: 900,
          boxShadow: '0 6px 30px rgba(0,0,0,0.30)',
          fontFamily: FONT,
        }}
      >
        <div style={{width: 74, height: 74, borderRadius: 37, background: '#D9D9DE', flex: '0 0 74px'}} />
        <div>
          <div style={{fontSize: 30, fontWeight: 500, color: '#6b6b70', lineHeight: 1.2}}>{user}</div>
          <div style={{fontSize: 44, fontWeight: 500, color: '#111', lineHeight: 1.18, letterSpacing: '-0.01em', marginTop: 6}}>{text}</div>
          <div style={{fontSize: 26, fontWeight: 500, color: '#9a9aa0', marginTop: 12}}>Reply</div>
        </div>
      </div>
    </div>
  );
};

// Numbered tutorial step pill (white pill, dark text) — pops in over light UI scenes.
export const StepPop: React.FC<{n: number; label: string; appearAt: number; y?: number; hideAt?: number}> = ({n, label, appearAt, y = 150, hideAt}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - appearAt * fps;
  if (local < 0) return null;
  if (hideAt !== undefined && frame / fps >= hideAt) return null;
  const pop = spring({frame: local, fps, config: {damping: 12, stiffness: 280, mass: 0.8}});
  return (
    <div style={{position: 'absolute', left: 40, top: y, display: 'flex', justifyContent: 'flex-start'}}>
      <div
        style={{
          transformOrigin: 'left center',
          transform: `scale(${interpolate(pop, [0, 1], [0.4, 1])})`,
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          background: theme.caption.lightBox.bg,
          color: theme.caption.darkColor,
          fontFamily: FONT,
          fontWeight: 500,
          fontSize: 50,
          letterSpacing: '-0.01em',
          padding: '18px 40px 18px 22px',
          borderRadius: 999,
          boxShadow: '0 4px 20px rgba(0,0,0,0.18)',
        }}
      >
        <div style={{width: 70, height: 70, borderRadius: 35, background: '#111', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 40}}>{n}</div>
        {label}
      </div>
    </div>
  );
};

// Image badges (e.g. integration/partner logos from public/assets/logos/) that
// pop in one after another. Use sparingly — the locked house style treats
// chips/badges as clutter; reserve for "works with X, Y, Z" beats.
export const ImageBadges: React.FC<{
  files: string[]; // paths relative to public/
  appearAt: number; // seconds
  stagger?: number;
  y?: number;
}> = ({files, appearAt, stagger = 0.14, y = 1050}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const n = files.length;
  const size = 148;
  const gap = 42;
  const totalW = n * size + (n - 1) * gap;
  return (
    <AbsoluteFill>
      {files.map((file, i) => {
        const local = frame - (appearAt + i * stagger) * fps;
        if (local < 0) return null;
        const pop = spring({frame: local, fps, config: {damping: 11, stiffness: 300, mass: 0.7}});
        const scale = interpolate(pop, [0, 1], [0.2, 1]);
        const wob = Math.sin((i * 1.7 + frame / fps) * 2.2) * 4;
        return (
          <div
            key={file}
            style={{
              position: 'absolute',
              left: (1080 - totalW) / 2 + i * (size + gap),
              top: y + wob,
              width: size,
              height: size,
              borderRadius: 36,
              background: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 14px 40px rgba(0,0,0,0.35)',
              transform: `scale(${scale}) rotate(${(i % 2 ? 1 : -1) * (1 - pop) * 14}deg)`,
            }}
          >
            <Img src={staticFile(file)} style={{width: 92, height: 92, objectFit: 'contain'}} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
