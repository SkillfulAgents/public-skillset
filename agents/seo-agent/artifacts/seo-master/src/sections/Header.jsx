import React from 'react';
import { Chip } from '../components/ui';
import { compact, daysSince, num, shortDateYear, timeAgo, pct } from '../lib/format';

const NAV = [
  ['kpis', 'KPIs'],
  ['trend', 'Trend'],
  ['targets', 'Targets'],
  ['content', 'Content'],
  ['queries', 'Queries'],
  ['links', 'Links'],
  ['outreach', 'Outreach'],
  ['program', 'Program'],
  ['backlog', 'Backlog'],
];

export default function Header({ data, loading, refreshing, onRefresh, lastLoaded }) {
  const through = data?.gsc_data_through;
  const lag = through ? daysSince(through) : null;
  const units = data?.units || {};
  const usedPct = units.limit ? (units.used / units.limit) * 100 : 0;

  return (
    <header className="app-header">
      <div className="header-main">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <h1>SEO Master</h1>
            <div className="brand-sub">{data?.site || '—'} · organic program console</div>
          </div>
        </div>

        <div className="header-meta">
          <Chip tone={lag !== null && lag > 3 ? 'warn' : 'info'} title="Google Search Console lags ~2 days">
            GSC data through <strong className="mono">{through || '—'}</strong>
            {lag !== null ? <span className="muted"> · {lag}d lag</span> : null}
          </Chip>
          <span className="hide-sm">
            <Chip tone="neutral" title={`Ahrefs snapshot ${data?.ahrefs_fetched_at || ''}`}>
              Ahrefs {data?.ahrefs_cached ? 'cached' : 'live'} · {timeAgo(data?.ahrefs_fetched_at)}
            </Chip>
          </span>
          <span className="hide-sm">
            <Chip tone="neutral" title={`GSC snapshot ${data?.gsc_fetched_at || ''}`}>
              GSC {data?.gsc_cached ? 'cached' : 'live'} · {timeAgo(data?.gsc_fetched_at)}
            </Chip>
          </span>
          {lastLoaded ? (
            <span className="header-loaded muted mono hide-sm">page loaded {timeAgo(lastLoaded)}</span>
          ) : null}
        </div>

        <div className="header-actions">
          <div className="budget" title={`Ahrefs units used this cycle. Resets ${units.reset || '—'}.`}>
            <div className="budget-top">
              <span>Ahrefs budget</span>
              <span className="mono">
                {compact(units.used)} / {compact(units.limit)}
              </span>
            </div>
            <div className="budget-track">
              <div
                className={'budget-fill' + (usedPct > 80 ? ' hot' : '')}
                style={{ width: `${Math.max(0.8, Math.min(100, usedPct))}%` }}
              />
            </div>
            <div className="budget-foot muted mono">
              {pct(usedPct, 1)} used · resets {units.reset ? shortDateYear(units.reset) : '—'}
              {units.spent_this_pull > 0 ? ` · last pull ${num(units.spent_this_pull)}u` : ''}
            </div>
          </div>

          <button
            type="button"
            className="btn-refresh"
            disabled={refreshing || loading}
            onClick={onRefresh}
            title="Forces a live Ahrefs + GSC pull. Costs roughly 500-600 Ahrefs units."
          >
            {refreshing ? <span className="spinner" aria-hidden="true" /> : null}
            {refreshing ? 'Refreshing…' : 'Hard refresh'}
            <span className="btn-sub">~600 units</span>
          </button>
        </div>
      </div>

      <nav className="header-nav" aria-label="Sections">
        {NAV.map(([id, label]) => (
          <a key={id} href={`#${id}`}>
            {label}
          </a>
        ))}
      </nav>
    </header>
  );
}
