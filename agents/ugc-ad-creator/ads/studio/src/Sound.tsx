import React from 'react';
import {Audio, Sequence, interpolate, staticFile, useVideoConfig} from 'remotion';
import catalog from '../public/sounds/catalog.json';

export type SfxItem = {sound: string; at: number; gainDb?: number}; // at = composition seconds
export type MusicSpec = {file: string; gainDb?: number; outAt?: number} | null; // file relative to public/sounds/

const dbToLinear = (db: number) => Math.pow(10, db / 20);

// SFX from the shared library catalog (id -> {file, gain_db}).
export const SfxTrack: React.FC<{items: SfxItem[]}> = ({items}) => {
  const {fps} = useVideoConfig();
  return (
    <>
      {items.map((it, i) => {
        const entry = (catalog as any).sounds[it.sound];
        if (!entry) {
          console.warn(`SfxTrack: unknown catalog sound "${it.sound}"`);
          return null;
        }
        const vol = dbToLinear(it.gainDb ?? entry.gain_db ?? -14);
        // sync_s = transient position inside the file; schedule so it lands exactly at `at`
        const from = Math.max(0, Math.round((it.at - (entry.sync_s ?? 0)) * fps));
        return (
          <Sequence key={`${it.sound}-${i}`} from={from} name={`sfx:${it.sound}`}>
            <Audio src={staticFile(`sounds/${entry.file}`)} volume={vol} />
          </Sequence>
        );
      })}
    </>
  );
};

// Music bed: fade in over the first 0.5s, duck constant (gainDb), fade out
// over 12 frames ending at outAt (seconds) — CTA/closer lands nearly dry.
export const MusicBed: React.FC<{music: MusicSpec; totalDuration: number}> = ({music, totalDuration}) => {
  const {fps} = useVideoConfig();
  if (!music) return null;
  const gain = dbToLinear(music.gainDb ?? -12);
  const outAt = music.outAt ?? totalDuration;
  const outFrame = Math.round(outAt * fps);
  return (
    <Audio
      src={staticFile(`sounds/${music.file}`)}
      loop
      volume={(f) =>
        gain *
        interpolate(f, [0, Math.round(0.5 * fps), outFrame - 12, outFrame], [0, 1, 1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })
      }
    />
  );
};
