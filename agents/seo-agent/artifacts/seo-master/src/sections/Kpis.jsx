import React from 'react';
import { Section, Delta, Card } from '../components/ui';
import { Meter } from '../components/Charts';
import { num, isNil } from '../lib/format';

function decimalsFor(k) {
  return k.label === 'Avg position' || k.label === 'Domain Rating' ? 1 : 0;
}

function KpiTile({ k, hero, extra }) {
  const d = decimalsFor(k);
  const hasPrev = !isNil(k.prev);
  return (
    <div className={'kpi' + (hero ? ' kpi-hero' : '')}>
      <div className="kpi-label">
        {k.label}
        {hero ? <span className="kpi-badge">north star</span> : null}
      </div>
      <div className="kpi-value mono">
        {num(k.value, d)}
        {k.unit ? <span className="kpi-unit">{k.unit}</span> : null}
      </div>
      {extra || null}
      <div className="kpi-delta">
        {hasPrev ? (
          <Delta value={k.delta} pctValue={k.delta_pct} goodUp={k.good_up} digits={d} />
        ) : (
          <span className="delta none">no prior period</span>
        )}
      </div>
      <div className="kpi-foot">
        {hasPrev ? (
          <span className="mono">
            prev {num(k.prev, d)}
            {k.unit ? ` ${k.unit}` : ''}
          </span>
        ) : null}
        {k.hint ? <span className="kpi-hint">{k.hint}</span> : null}
      </div>
    </div>
  );
}

export function KpiRow({ kpis, ranges, refdomains }) {
  const list = Array.isArray(kpis) ? kpis : [];
  const clean = refdomains?.clean_count;
  const suspect = refdomains?.suspect_count;

  // The raw referring-domain count is misleading on its own — always pair it
  // with the clean/suspect split.
  const extraFor = (k) =>
    k.label === 'Referring domains' && !isNil(clean) && !isNil(suspect) ? (
      <div className="kpi-split mono">
        <span className="good">{num(clean)} clean</span>
        <span className="muted"> · </span>
        <span className="bad">{num(suspect)} suspect</span>
      </div>
    ) : null;
  const wk = ranges?.week;
  const pw = ranges?.prev_week;
  return (
    <Section
      id="kpis"
      n={1}
      title="Headline KPIs"
      subtitle={
        wk
          ? `Search Console tiles compare ${wk[0]} → ${wk[1]} against ${pw?.[0]} → ${pw?.[1]}. Ahrefs and outreach tiles are point-in-time snapshots (no prior period stored yet).`
          : 'Week over week.'
      }
    >
      {list.length === 0 ? (
        <Card>
          <div className="nodata">
            <div className="nodata-title">No KPIs in payload</div>
          </div>
        </Card>
      ) : (
        <div className="kpi-grid">
          {list.map((k, i) => (
            <KpiTile key={k.label} k={k} hero={i === 0} extra={extraFor(k)} />
          ))}
        </div>
      )}
      <p className="note">
        Lower is better for <strong>Avg position</strong> — a positive delta there is shown red because the rank got
        worse.
      </p>
    </Section>
  );
}

export function Targets({ targets }) {
  const list = Array.isArray(targets) ? targets : [];
  return (
    <Section id="targets" n={4} title="12-month targets" subtitle="Progress against the goals set in the July strategy plan.">
      {list.length === 0 ? (
        <Card>
          <div className="nodata">
            <div className="nodata-title">No targets configured</div>
          </div>
        </Card>
      ) : (
        <div className="meter-grid">
          {list.map((t) => (
            <Meter key={t.label} label={t.label} current={t.current} target={t.target} pctValue={t.pct} note={t.note} />
          ))}
        </div>
      )}
      <p className="note">
        “Referring domains” hits its target on the raw Ahrefs count, but only{' '}
        <strong>{list.find((t) => t.label === 'Quality refdomains')?.current ?? '—'}</strong> of those pass the spam
        filter — read the two rows together, not separately.
      </p>
    </Section>
  );
}
