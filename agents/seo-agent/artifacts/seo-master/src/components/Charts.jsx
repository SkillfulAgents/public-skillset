import React, { useMemo, useState } from 'react';
import { useWidth, rollingMean } from '../lib/hooks';
import { compact, num, shortDate, isNil, DASH } from '../lib/format';

/* ------------------------------------------------------------------ scales */

/** Round a raw step up to 1/2/2.5/5 x 10^n so axis labels stay whole numbers. */
function niceStep(raw) {
  if (!isFinite(raw) || raw <= 0) return 1;
  const exp = Math.floor(Math.log10(raw));
  const base = Math.pow(10, exp);
  const f = raw / base;
  const step = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
  return step * base;
}

/** Ticks at nice round intervals covering [0, max]. Never produces 666.667. */
function ticks(max, count = 3) {
  if (!isFinite(max) || max <= 0) return { max: 1, values: [0, 1] };
  const step = niceStep(max / Math.max(1, count));
  const top = Math.ceil(max / step - 1e-9) * step;
  const values = [];
  for (let v = 0; v <= top + step * 1e-6; v += step) values.push(Number(v.toFixed(6)));
  return { max: top || 1, values };
}

/* ------------------------------------------------------------- empty state */

export function NoData({ title = 'Not enough data yet', detail, height = 120 }) {
  return (
    <div className="nodata" style={{ minHeight: height }}>
      <div className="nodata-title">{title}</div>
      {detail ? <div className="nodata-detail">{detail}</div> : null}
    </div>
  );
}

/* --------------------------------------------------------- time series panel */

/**
 * A single stacked panel of a time series. Renders an area for the raw value
 * and (optionally) a heavier line for the rolling mean.
 * Degrades: 0 points -> NoData, 1-2 points -> dots + rule, never an empty axis.
 */
export function TimeSeriesPanel({
  data,
  xKey = 'date',
  yKey,
  label,
  color = '#38bdf8',
  height = 150,
  ma = 7,
  formatValue = compact,
  formatTooltip = num,
  emptyDetail,
}) {
  const [ref, width] = useWidth(680);
  const [hover, setHover] = useState(null);

  const rows = Array.isArray(data) ? data : [];
  const values = rows.map((r) => Number(r[yKey]) || 0);
  const allZero = values.length > 0 && values.every((v) => v === 0);

  const maSeries = useMemo(
    () => (rows.length >= ma ? rollingMean(values, ma) : []),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [rows, ma, yKey],
  );

  if (rows.length === 0) {
    return (
      <div className="panel-chart">
        <ChartHeading label={label} color={color} />
        <NoData detail={emptyDetail || 'No rows returned for this range.'} height={height} />
      </div>
    );
  }

  const padL = 54;
  const padR = 10;
  const padT = 12;
  const padB = 22;
  const w = Math.max(240, width);
  const innerW = Math.max(10, w - padL - padR);
  const innerH = Math.max(10, height - padT - padB);

  const maxV = Math.max(...values, 0);
  const t = ticks(allZero ? 1 : maxV, 3);
  const yOf = (v) => padT + innerH - (Math.max(0, Number(v) || 0) / t.max) * innerH;
  const xOf = (i) => (rows.length === 1 ? padL + innerW / 2 : padL + (i / (rows.length - 1)) * innerW);

  const areaPath =
    rows.length > 1
      ? `M ${xOf(0)} ${yOf(values[0])} ` +
        values.map((v, i) => `L ${xOf(i)} ${yOf(v)}`).join(' ') +
        ` L ${xOf(rows.length - 1)} ${padT + innerH} L ${xOf(0)} ${padT + innerH} Z`
      : null;

  const linePath =
    rows.length > 1 ? values.map((v, i) => `${i ? 'L' : 'M'} ${xOf(i)} ${yOf(v)}`).join(' ') : null;

  const maPath =
    maSeries.length > 1
      ? maSeries
          .map((v, i) => (isNil(v) ? null : `${i && !isNil(maSeries[i - 1]) ? 'L' : 'M'} ${xOf(i)} ${yOf(v)}`))
          .filter(Boolean)
          .join(' ')
      : null;

  const tickIdx = [];
  const nTicks = Math.min(6, rows.length);
  for (let i = 0; i < nTicks; i++) {
    tickIdx.push(Math.round((i / Math.max(1, nTicks - 1)) * (rows.length - 1)));
  }

  const gid = `grad-${yKey}-${label}`.replace(/\W/g, '');

  function onMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const rel = (x - padL) / innerW;
    const i = Math.round(rel * (rows.length - 1));
    if (i >= 0 && i < rows.length) setHover(i);
    else setHover(null);
  }

  const hoverRow = hover !== null ? rows[hover] : null;

  return (
    <div className="panel-chart" ref={ref}>
      <ChartHeading
        label={label}
        color={color}
        right={
          hoverRow ? (
            <span className="chart-hoverval">
              <span className="mono">{shortDate(hoverRow[xKey])}</span>{' '}
              <strong className="mono">{formatTooltip(hoverRow[yKey])}</strong>
            </span>
          ) : (
            <span className="chart-hoverval muted">
              {ma && maSeries.length ? `${ma}-day avg overlaid` : ''}
            </span>
          )
        }
      />
      <div className="chart-wrap">
        <svg
          width={w}
          height={height}
          role="img"
          aria-label={`${label} time series`}
          onMouseMove={onMove}
          onMouseLeave={() => setHover(null)}
        >
          <defs>
            <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.38" />
              <stop offset="100%" stopColor={color} stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {t.values.map((v, i) => (
            <g key={i}>
              <line
                x1={padL}
                x2={w - padR}
                y1={yOf(v)}
                y2={yOf(v)}
                stroke="var(--grid)"
                strokeWidth="1"
                shapeRendering="crispEdges"
              />
              <text x={padL - 8} y={yOf(v) + 3.5} textAnchor="end" className="axis-label">
                {allZero && v === 0 ? '0' : formatValue(v)}
              </text>
            </g>
          ))}

          {areaPath ? <path d={areaPath} fill={`url(#${gid})`} /> : null}
          {linePath ? (
            <path d={linePath} fill="none" stroke={color} strokeWidth={maPath ? 1 : 1.8} opacity={maPath ? 0.55 : 1} />
          ) : null}
          {maPath ? <path d={maPath} fill="none" stroke={color} strokeWidth="2" /> : null}

          {rows.length <= 2
            ? values.map((v, i) => <circle key={i} cx={xOf(i)} cy={yOf(v)} r="3.5" fill={color} />)
            : null}

          {tickIdx.map((i, n) => (
            <text
              key={i}
              x={xOf(i)}
              y={height - 6}
              textAnchor={n === 0 ? 'start' : n === tickIdx.length - 1 ? 'end' : 'middle'}
              className="axis-label"
            >
              {shortDate(rows[i][xKey])}
            </text>
          ))}

          {hover !== null ? (
            <g>
              <line
                x1={xOf(hover)}
                x2={xOf(hover)}
                y1={padT}
                y2={padT + innerH}
                stroke="var(--fg-dim)"
                strokeDasharray="3 3"
              />
              <circle cx={xOf(hover)} cy={yOf(values[hover])} r="3.5" fill={color} stroke="var(--bg)" strokeWidth="1.5" />
            </g>
          ) : null}
        </svg>
      </div>
      {allZero ? (
        <div className="chart-note">All values are zero across this range — nothing recorded yet.</div>
      ) : null}
    </div>
  );
}

function ChartHeading({ label, color, right }) {
  return (
    <div className="chart-heading">
      <span className="chart-label">
        <span className="swatch" style={{ background: color }} aria-hidden="true" />
        {label}
      </span>
      {right}
    </div>
  );
}

/* ----------------------------------------------------------- category bars */

/**
 * Grouped vertical bars over categories. series: [{key,label,color}]
 */
export function GroupedBars({ data, xKey, series, height = 170, minPointsNote }) {
  const [ref, width] = useWidth(560);
  const [hover, setHover] = useState(null);
  const rows = Array.isArray(data) ? data : [];

  if (rows.length === 0) {
    return <NoData detail="No weeks recorded yet." height={height} />;
  }

  const padL = 34;
  const padR = 8;
  const padT = 10;
  const padB = 24;
  const w = Math.max(240, width);
  const innerW = Math.max(10, w - padL - padR);
  const innerH = Math.max(10, height - padT - padB);

  const maxV = Math.max(1, ...rows.flatMap((r) => series.map((s) => Number(r[s.key]) || 0)));
  const t = ticks(maxV, 2);
  const yOf = (v) => padT + innerH - (v / t.max) * innerH;

  const slot = innerW / rows.length;
  const groupW = Math.min(slot * 0.72, 120);
  const barW = Math.max(3, (groupW - (series.length - 1) * 3) / series.length);

  return (
    <div ref={ref}>
      <svg width={w} height={height} role="img" aria-label="Weekly activity bars">
        {t.values.map((v, i) => (
          <g key={i}>
            <line x1={padL} x2={w - padR} y1={yOf(v)} y2={yOf(v)} stroke="var(--grid)" shapeRendering="crispEdges" />
            <text x={padL - 6} y={yOf(v) + 3.5} textAnchor="end" className="axis-label">
              {compact(v)}
            </text>
          </g>
        ))}
        {rows.map((r, ri) => {
          const cx = padL + slot * ri + slot / 2;
          const start = cx - groupW / 2;
          return (
            <g key={ri} onMouseEnter={() => setHover(ri)} onMouseLeave={() => setHover(null)}>
              <rect x={padL + slot * ri} y={padT} width={slot} height={innerH} fill={hover === ri ? 'var(--hover)' : 'transparent'} />
              {series.map((s, si) => {
                const v = Number(r[s.key]) || 0;
                const h = Math.max(v > 0 ? 2 : 0, padT + innerH - yOf(v));
                return (
                  <rect
                    key={s.key}
                    x={start + si * (barW + 3)}
                    y={padT + innerH - h}
                    width={barW}
                    height={h}
                    fill={s.color}
                    rx="1.5"
                  >
                    <title>{`${r[xKey]} · ${s.label}: ${v}`}</title>
                  </rect>
                );
              })}
              <text x={cx} y={height - 7} textAnchor="middle" className="axis-label">
                {shortDate(r[xKey])}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="legend">
        {series.map((s) => (
          <span key={s.key} className="legend-item">
            <span className="swatch" style={{ background: s.color }} /> {s.label}
          </span>
        ))}
      </div>
      {minPointsNote && rows.length < 4 ? <div className="chart-note">{minPointsNote}</div> : null}
    </div>
  );
}

/** Simple single-series vertical bars (e.g. outreach sends per day). */
export function MiniBars({ data, xKey = 'date', yKey = 'touches', height = 90, color = '#a78bfa', label }) {
  const [ref, width] = useWidth(520);
  const rows = Array.isArray(data) ? data : [];
  if (rows.length === 0) return <NoData detail="No sends recorded." height={height} />;

  const padL = 28;
  const padR = 6;
  const padT = 8;
  const padB = 18;
  const w = Math.max(200, width);
  const innerW = Math.max(10, w - padL - padR);
  const innerH = Math.max(8, height - padT - padB);
  const maxV = Math.max(1, ...rows.map((r) => Number(r[yKey]) || 0));
  const t = ticks(maxV, 1);
  const slot = innerW / rows.length;
  const barW = Math.max(2, slot * 0.62);

  return (
    <div ref={ref}>
      <svg width={w} height={height} role="img" aria-label={label || 'bars'}>
        {t.values.map((v, i) => (
          <g key={i}>
            <line x1={padL} x2={w - padR} y1={padT + innerH - (v / t.max) * innerH} y2={padT + innerH - (v / t.max) * innerH} stroke="var(--grid)" shapeRendering="crispEdges" />
            <text x={padL - 6} y={padT + innerH - (v / t.max) * innerH + 3.5} textAnchor="end" className="axis-label">
              {compact(v)}
            </text>
          </g>
        ))}
        {rows.map((r, i) => {
          const v = Number(r[yKey]) || 0;
          const h = (v / t.max) * innerH;
          return (
            <rect key={i} x={padL + slot * i + (slot - barW) / 2} y={padT + innerH - h} width={barW} height={Math.max(v > 0 ? 2 : 0, h)} fill={color} rx="1.5">
              <title>{`${shortDate(r[xKey])}: ${v}`}</title>
            </rect>
          );
        })}
        {[0, rows.length - 1].map((i, k) => (
          <text key={k} x={padL + slot * i + slot / 2} y={height - 5} textAnchor={k === 0 ? 'start' : 'end'} className="axis-label">
            {shortDate(rows[i][xKey])}
          </text>
        ))}
      </svg>
    </div>
  );
}

/* ---------------------------------------------------------- horizontal bar */

export function HBar({ label, value, total, color = '#38bdf8', right, sub }) {
  const p = total > 0 ? (value / total) * 100 : 0;
  return (
    <div className="hbar-row">
      <div className="hbar-label">{label}</div>
      <div className="hbar-track" role="img" aria-label={`${label}: ${value} of ${total}`}>
        <div className="hbar-fill" style={{ width: `${Math.max(p, value > 0 ? 1.5 : 0)}%`, background: color }} />
      </div>
      <div className="hbar-value mono">{right !== undefined ? right : num(value)}</div>
      {sub ? <div className="hbar-sub">{sub}</div> : null}
    </div>
  );
}

/** Two-part split bar — used for clean vs suspect refdomains. */
export function SplitBar({ parts, height = 26 }) {
  const total = parts.reduce((a, p) => a + p.value, 0) || 1;
  return (
    <div className="splitbar" style={{ height }} role="img" aria-label={parts.map((p) => `${p.label} ${p.value}`).join(', ')}>
      {parts.map((p) => (
        <div
          key={p.label}
          className="splitbar-seg"
          style={{ width: `${(p.value / total) * 100}%`, background: p.color }}
          title={`${p.label}: ${p.value}`}
        >
          {p.value / total > 0.12 ? <span className="mono">{p.value}</span> : null}
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ funnel */

export function Funnel({ steps }) {
  const top = Math.max(1, steps[0]?.value || 1);
  return (
    <div className="funnel">
      {steps.map((s, i) => {
        const p = (s.value / top) * 100;
        const prev = i > 0 ? steps[i - 1].value : null;
        const conv = prev ? (prev > 0 ? (s.value / prev) * 100 : 0) : null;
        const zero = s.value === 0;
        return (
          <div className="funnel-step" key={s.label}>
            <div className="funnel-top">
              <span className="funnel-label">{s.label}</span>
              <span className={'funnel-value mono' + (zero ? ' zero' : '')}>{s.value}</span>
            </div>
            <div className="funnel-track">
              <div
                className={'funnel-fill' + (zero ? ' empty' : '')}
                style={{ width: zero ? '100%' : `${Math.max(p, 2)}%`, background: zero ? undefined : s.color }}
              >
                {zero ? <span className="funnel-empty-text">none yet</span> : null}
              </div>
            </div>
            {conv !== null ? (
              <div className="funnel-conv mono">
                {conv.toFixed(conv < 10 ? 1 : 0)}% of {steps[i - 1].label.toLowerCase()}
              </div>
            ) : (
              <div className="funnel-conv mono muted">start of funnel</div>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------- meter */

export function Meter({ label, current, target, pctValue, note, format = num }) {
  const p = isNil(pctValue) ? (target ? (current / target) * 100 : 0) : Number(pctValue);
  const capped = Math.max(0, Math.min(100, p));
  const hit = p >= 100;
  return (
    <div className="meter">
      <div className="meter-head">
        <span className="meter-label">{label}</span>
        <span className="meter-nums mono">
          <strong>{format(current)}</strong>
          <span className="muted"> / {format(target)}</span>
        </span>
      </div>
      <div className="meter-track" role="img" aria-label={`${label}: ${p.toFixed(0)}% of target`}>
        <div
          className={'meter-fill' + (hit ? ' hit' : '')}
          style={{ width: capped > 0 ? `${Math.max(capped, 0.8)}%` : 0 }}
        />
      </div>
      <div className="meter-foot">
        <span className={'meter-pct mono' + (hit ? ' hit' : '') + (p === 0 ? ' zero' : '')}>
          {hit ? 'target hit' : p === 0 ? 'not started' : `${p.toFixed(p < 10 ? 1 : 0)}%`}
        </span>
        {note ? <span className="meter-note">{note}</span> : null}
      </div>
    </div>
  );
}

/* --------------------------------------------------------------- sparkline */

export function Sparkline({ values, width = 90, height = 24, color = '#38bdf8' }) {
  const vals = (values || []).filter((v) => !isNil(v)).map(Number);
  if (vals.length === 0) return <span className="muted mono">{DASH}</span>;
  const max = Math.max(...vals);
  const min = Math.min(...vals);
  const flat = max === min;
  if (vals.length === 1 || flat) {
    return (
      <svg width={width} height={height} aria-hidden="true">
        <line
          x1="1"
          x2={width - 1}
          y1={height / 2}
          y2={height / 2}
          stroke={vals.length === 1 ? 'var(--grid)' : color}
          strokeWidth={vals.length === 1 ? 1 : 1.6}
          strokeDasharray={vals.length === 1 ? '2 3' : undefined}
        />
        {vals.length === 1 ? <circle cx={width / 2} cy={height / 2} r="3" fill={color} /> : null}
      </svg>
    );
  }
  const span = max - min || 1;
  const x = (i) => (i / (vals.length - 1)) * (width - 2) + 1;
  const y = (v) => height - 2 - ((v - min) / span) * (height - 4);
  const d = vals.map((v, i) => `${i ? 'L' : 'M'} ${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join(' ');
  return (
    <svg width={width} height={height} aria-hidden="true">
      <path d={d} fill="none" stroke={color} strokeWidth="1.6" />
      <circle cx={x(vals.length - 1)} cy={y(vals[vals.length - 1])} r="2.2" fill={color} />
    </svg>
  );
}
