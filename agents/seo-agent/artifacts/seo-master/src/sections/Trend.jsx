import React, { useState } from 'react';
import { Section, Card, Toggle } from '../components/ui';
import { TimeSeriesPanel } from '../components/Charts';
import { num, pct, signed, isNil, compact } from '../lib/format';

function PeriodRow({ label, range, cur, prev }) {
  const cells = [
    { k: 'clicks', fmt: (v) => num(v), goodUp: true },
    { k: 'impressions', fmt: (v) => num(v), goodUp: true },
    { k: 'ctr', fmt: (v) => pct(v, 2), goodUp: true },
    { k: 'position', fmt: (v) => num(v, 1), goodUp: false },
  ];
  return (
    <tr>
      <th scope="row">
        {label}
        {range ? <span className="muted mono block">{range[0]} → {range[1]}</span> : null}
      </th>
      {cells.map(({ k, fmt, goodUp }) => {
        const c = cur?.[k];
        const p = prev?.[k];
        const d = isNil(c) || isNil(p) ? null : c - p;
        const good = d === null || d === 0 ? null : (d > 0) === goodUp;
        return (
          <td key={k}>
            <span className="mono strong">{isNil(c) ? '—' : fmt(c)}</span>
            <span className={'trend-delta mono ' + (good === null ? 'muted' : good ? 'good' : 'bad')}>
              {d === null ? '—' : `${signed(d, k === 'ctr' ? 2 : k === 'position' ? 1 : 0)} vs prev`}
            </span>
          </td>
        );
      })}
    </tr>
  );
}

export default function Trend({ gsc }) {
  const [mode, setMode] = useState('nonbrand');
  const nb = mode === 'nonbrand';
  const series = nb ? gsc?.daily_nonbrand : gsc?.daily;
  const periods = gsc?.periods || {};
  const ranges = gsc?.ranges || {};

  const rows = Array.isArray(series) ? series : [];
  const totalClicks = rows.reduce((a, r) => a + (r.clicks || 0), 0);
  const totalImpr = rows.reduce((a, r) => a + (r.impressions || 0), 0);

  return (
    <Section
      id="trend"
      n={3}
      title="Search trend"
      subtitle={`Daily Google Search Console, last ${rows.length} days through ${gsc?.data_through || '—'}. Impressions and clicks are on separate panels — they differ by ~100x.`}
      right={
        <Toggle
          ariaLabel="Query filter"
          value={mode}
          onChange={setMode}
          options={[
            { value: 'nonbrand', label: 'Non-brand', title: 'Excludes queries containing the brand name' },
            { value: 'all', label: 'All queries' },
          ]}
        />
      }
    >
      <Card
        title={nb ? 'Non-brand search performance' : 'All queries'}
        sub={`${compact(totalClicks)} clicks · ${compact(totalImpr)} impressions over the window`}
      >
        <TimeSeriesPanel
          data={rows}
          yKey="impressions"
          label="Impressions / day"
          color="#818cf8"
          height={148}
          emptyDetail="GSC returned no daily rows."
        />
        <TimeSeriesPanel
          data={rows}
          yKey="clicks"
          label="Clicks / day"
          color="#38bdf8"
          height={132}
          emptyDetail="GSC returned no daily rows."
        />
        {nb ? (
          <p className="note">
            Non-brand is the growth signal: brand queries carry most of the raw click volume and
            move with paid + PR, not SEO.
          </p>
        ) : null}
      </Card>

      <Card title="Period comparison" sub={nb ? 'Non-brand queries only' : 'All queries'}>
        <div className="table-scroll">
          <table className="data-table compact">
            <thead>
              <tr>
                <th scope="col" style={{ textAlign: 'left' }}>Period</th>
                <th scope="col">Clicks</th>
                <th scope="col">Impressions</th>
                <th scope="col">CTR</th>
                <th scope="col">Avg position</th>
              </tr>
            </thead>
            <tbody>
              <PeriodRow
                label="Last 7 days"
                range={ranges.week}
                cur={nb ? periods.week?.cur_nb : periods.week?.cur}
                prev={nb ? periods.week?.prev_nb : periods.week?.prev}
              />
              <PeriodRow
                label="Last 28 days"
                range={ranges.cur}
                cur={nb ? periods.month?.cur_nb : periods.month?.cur}
                prev={nb ? periods.month?.prev_nb : periods.month?.prev}
              />
            </tbody>
          </table>
        </div>
        <p className="note">Position deltas here are raw (lower = better), unlike the query/page tables which use a sign-flipped “rank change”.</p>
      </Card>
    </Section>
  );
}
