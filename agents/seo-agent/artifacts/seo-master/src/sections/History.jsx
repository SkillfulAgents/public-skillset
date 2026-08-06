import React from 'react';
import { Card, Chip } from '../components/ui';
import { TimeSeriesPanel, NoData, Sparkline } from '../components/Charts';
import { loose, num, shortDateYear, isNil, DASH } from '../lib/format';

/** Ahrefs snapshot history — usually 1 row on a fresh install. Must not draw an empty axis. */
export function SnapshotHistory({ kpiHistory }) {
  const rows = Array.isArray(kpiHistory) ? kpiHistory : [];

  if (rows.length < 3) {
    const latest = rows[rows.length - 1];
    return (
      <Card
        title="Ahrefs snapshot history"
        sub="Accumulates one row per Ahrefs pull — a trend appears once there are at least three"
      >
        <div className="nodata">
          <div className="nodata-title">
            {rows.length === 0 ? 'No snapshots stored yet' : `Only ${rows.length} snapshot${rows.length > 1 ? 's' : ''} so far`}
          </div>
          <div className="nodata-detail">
            {latest ? (
              <>
                First point recorded <strong>{shortDateYear(latest.date)}</strong>. Nothing to trend against until the
                next pull.
              </>
            ) : (
              'Run a refresh to record the first point.'
            )}
          </div>
        </div>
        {latest ? (
          <div className="snapshot-row">
            {[
              ['DR', latest.dr, 1],
              ['Refdomains', latest.refdomains, 0],
              ['Backlinks', latest.backlinks, 0],
              ['Organic keywords', latest.org_keywords, 0],
              ['Top-3 keywords', latest.org_keywords_1_3, 0],
              ['Est. organic traffic', latest.org_traffic, 0],
            ].map(([label, v, d]) => (
              <div className="snapshot-cell" key={label}>
                <div className="snapshot-value mono">{num(v, d)}</div>
                <div className="snapshot-label">{label}</div>
                <Sparkline values={[v]} width={64} height={18} />
              </div>
            ))}
          </div>
        ) : null}
      </Card>
    );
  }

  return (
    <Card title="Ahrefs snapshot history" sub={`${rows.length} pulls recorded`}>
      <TimeSeriesPanel data={rows} yKey="refdomains" label="Referring domains" color="#a78bfa" height={130} ma={0} />
      <TimeSeriesPanel data={rows} yKey="org_keywords" label="Ranking keywords" color="#34d399" height={120} ma={0} />
    </Card>
  );
}

const STATE_COLS = [
  ['DR', 'DR', 0],
  ['Refdoms', 'Refdomains', 0],
  ['GSC clicks', 'Clicks / wk', 0],
  ['GSC imp', 'Impressions / wk', 0],
  ['NB clicks', 'Non-brand clicks / wk', 0],
  ['NB imp', 'Non-brand impr / wk', 0],
  ['Ahrefs org kw', 'Ahrefs org kw', 0],
  ['Sitemap URLs', 'Sitemap URLs', 0],
];

/** Weekly rows parsed out of STATE.md — the only real WoW history we have today. */
export function WeeklyHistory({ rows }) {
  const list = Array.isArray(rows) ? rows : [];
  if (list.length === 0) {
    return (
      <Card title="Weekly history (STATE.md)" sub="Parsed from the operating doc">
        <NoData detail="No weekly rows parsed from STATE.md." />
      </Card>
    );
  }

  return (
    <Card
      title="Weekly history (STATE.md)"
      sub={`${list.length} weekly checkpoints since ${list[0]?.Date || '—'} — values are as recorded in the operating doc`}
      pad={false}
    >
      <div className="table-scroll">
        <table className="data-table compact">
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }} scope="col">Metric</th>
              {list.map((r) => (
                <th key={r.Date} scope="col" className="mono">
                  {shortDateYear(r.Date)}
                </th>
              ))}
              <th scope="col" style={{ width: 100 }}>Trend</th>
            </tr>
          </thead>
          <tbody>
            {STATE_COLS.map(([key, label]) => {
              const vals = list.map((r) => (isNil(r._num?.[key]) ? loose(r[key]) : r._num[key]));
              const known = vals.filter((v) => !isNil(v));
              return (
                <tr key={key}>
                  <th scope="row" style={{ textAlign: 'left' }}>{label}</th>
                  {list.map((r, i) => (
                    <td key={i} className="mono">
                      {r[key] && r[key] !== '—' ? r[key] : <span className="muted">{DASH}</span>}
                    </td>
                  ))}
                  <td>
                    {known.length >= 2 ? (
                      <Sparkline values={vals.map((v) => (isNil(v) ? null : v))} width={90} height={22} />
                    ) : (
                      <span className="muted small">need 2+</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="week-notes">
        {list
          .slice()
          .reverse()
          .map((r) => (
            <div className="week-note" key={r.Date}>
              <Chip tone="neutral">{shortDateYear(r.Date)}</Chip>
              <span>{r.Notes || '—'}</span>
            </div>
          ))}
      </div>
    </Card>
  );
}
