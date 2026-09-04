// Locked overlay style for UGC ads. Iterate HERE (not per ad):
// white-only text, Inter 500, sentence case, subtle drop shadows (no strokes,
// no accent colors), outro-only brand lockup stacked above a rounded CTA card.
// Brand-specific values (CTA copy, logo files) come from ../brand.json, which
// agent-onboarding writes.
import brand from '../brand.json';

export const FONT = 'Inter, -apple-system, sans-serif';

export const theme = {
  caption: {
    fontWeight: 500,
    color: '#ffffff',
    emphasisColor: '#ffffff',
    // scene-aware: dark text during light full-bleed scenes (white bg)
    darkColor: '#111111',
    // white rounded pill behind dark text on light scenes (readability over busy UI)
    lightBox: {
      bg: '#ffffff',
      radius: 18,
      paddingY: 12,
      paddingX: 30,
      shadow: '0 2px 10px rgba(0,0,0,0.12)',
    },
    fontSize: 62,
    shadow: '0 2px 12px rgba(0,0,0,0.35)',
    letterSpacing: '-0.01em',
    lineHeight: 1.1,
    y: 720,
  },
  hook: {
    fontWeight: 500,
    color: '#ffffff',
    fontSize: 74,
    shadow: '0 2px 14px rgba(0,0,0,0.38)',
    letterSpacing: '-0.02em',
    lineHeight: 1.06,
    y: 210,
  },
  // Outro-only lockup, centered above the CTA card. A persistent top watermark
  // collides with TikTok's top nav — don't add one.
  brand: {
    logo: brand.logoWhite as string | null,
    logoDark: brand.logoDark as string | null,
    width: brand.logoWidth ?? 240,
    y: 1190,
    shadow: '0 1px 6px rgba(0,0,0,0.20)',
  },
  cta: {
    fontWeight: 500,
    bg: '#ffffff',
    color: '#000000',
    fontSize: 46,
    radius: 24,
    paddingY: 26,
    paddingX: 64,
    shadow: '0 2px 14px rgba(0,0,0,0.30)',
    letterSpacing: '-0.01em',
    lineHeight: 1.25,
    y: 1330,
    text: brand.ctaText as string,
  },
} as const;
