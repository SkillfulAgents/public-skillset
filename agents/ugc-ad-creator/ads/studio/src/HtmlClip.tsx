import React, {useEffect, useRef, useState} from 'react';
import {continueRender, delayRender, useCurrentFrame, useVideoConfig} from 'remotion';

// Renders a self-contained HTML animation clip (window.ANIM + window.seek(t)
// contract — see the build-product-visual skill) inside an iframe, driven
// deterministically frame by frame.
//
// The iframe is laid out at the clip's design size (designW x designH) and
// CSS-scaled to cover/contain the container box, so output stays crisp.
export const HtmlClip: React.FC<{
  src: string; // URL (staticSrc(...) + optional ?params)
  designW?: number;
  designH?: number;
  boxW: number; // container box in composition px
  boxH: number;
  fit?: 'cover' | 'contain' | 'width';
  align?: 'center' | 'top' | 'bottom';
  offsetX?: number; // design px: horizontal shift of the view center (+ = look right)
  startFrom?: number; // seconds into the clip at local frame 0
  speed?: number; // clip-seconds per composition-second
}> = ({src, designW = 960, designH = 540, boxW, boxH, fit = 'cover', align = 'center', offsetX = 0, startFrom = 0, speed = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ref = useRef<HTMLIFrameElement>(null);
  const [handle] = useState(() => delayRender('html-clip load'));
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const w = ref.current?.contentWindow as any;
    if (!ready || !w?.seek) return;
    const t = startFrom + (frame / fps) * speed;
    const dur = w.ANIM?.duration ?? Infinity;
    w.seek(Math.min(Math.max(t, 0), dur - 1 / (w.ANIM?.fps ?? 30)));
  }, [frame, fps, ready, startFrom, speed]);

  const scale = fit === 'cover' ? Math.max(boxW / designW, boxH / designH) : fit === 'width' ? boxW / designW : Math.min(boxW / designW, boxH / designH);
  const w = designW * scale;
  const h = designH * scale;
  const left = (boxW - w) / 2 - offsetX * scale;
  const top = align === 'top' ? 0 : align === 'bottom' ? boxH - h : (boxH - h) / 2;

  return (
    <div style={{position: 'absolute', width: boxW, height: boxH, overflow: 'hidden'}}>
      <iframe
        ref={ref}
        src={src}
        style={{
          border: 0,
          width: designW,
          height: designH,
          position: 'absolute',
          left,
          top,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
        }}
        onLoad={() => {
          const win = ref.current!.contentWindow as any;
          const done = () => {
            setReady(true);
            continueRender(handle);
          };
          // Some clips install a placeholder no-arg seek() and swap in the real
          // seek(t) after an async boot. Wait for the real one (arity >= 1).
          const waitForSeek = () => {
            const t0 = Date.now();
            const poll = () => {
              if (typeof win.seek === 'function' && win.seek.length >= 1) return done();
              if (Date.now() - t0 > 8000) return done();
              setTimeout(poll, 40);
            };
            poll();
          };
          try {
            win.document.fonts.ready.then(waitForSeek);
          } catch {
            waitForSeek();
          }
        }}
      />
    </div>
  );
};
