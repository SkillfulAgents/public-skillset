import React, { useMemo, useState } from 'react';
import { Section, Card, Chip, SortTH, Stat, Switch, ExternalLink } from '../components/ui';
import { SplitBar, NoData } from '../components/Charts';
import { useSort } from '../lib/hooks';
import { num, pct, shortDateYear, isNil, DASH, compact } from '../lib/format';

const BUCKETS = [
  { key: '0-19', lo: 0, hi: 19, label: 'DR 0–19' },
  { key: '20-39', lo: 20, hi: 39, label: 'DR 20–39' },
  { key: '40-59', lo: 40, hi: 59, label: 'DR 40–59' },
  { key: '60+', lo: 60, hi: Infinity, label: 'DR 60+' },
];

function DomainTable({ rows, empty, showLost }) {
  const sort = useSort('dr', 'desc');
  const sorted = sort.sorter(rows, { domain: (r) => r.domain });
  if (rows.length === 0) return <div className="subtable-empty">{empty}</div>;
  return (
    <div className="table-scroll cap">
      <table className="data-table">
        <thead>
          <tr>
            <SortTH label="Domain" k="domain" sort={sort} align="left" preferred="asc" />
            <SortTH label="DR" k="dr" sort={sort} title="Ahrefs Domain Rating" />
            <SortTH label="Traffic" k="traffic" sort={sort} title="Estimated monthly organic traffic of the linking domain" />
            <SortTH label="Links" k="links" sort={sort} />
            <SortTH label="Dofollow" k="dofollow" sort={sort} />
            <SortTH label={showLost ? 'Last seen' : 'First seen'} k={showLost ? 'last_seen' : 'first_seen'} sort={sort} />
            <th scope="col">Quality</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((r) => (
            <tr key={r.domain}>
              <td style={{ textAlign: 'left' }} className="cell-title">
                <ExternalLink href={`https://${r.domain}`}>{r.domain}</ExternalLink>
              </td>
              <td className="mono strong">{isNil(r.dr) ? DASH : num(r.dr, 0)}</td>
              <td className="mono">{isNil(r.traffic) ? DASH : num(r.traffic)}</td>
              <td className="mono">{num(r.links)}</td>
              <td className="mono">{num(r.dofollow)}</td>
              <td className="mono nowrap">{shortDateYear(showLost ? r.last_seen : r.first_seen)}</td>
              <td>
                {r.suspect ? (
                  <Chip tone="bad" title="Spam-signature TLD, or under 10 monthly visits and DR below 15">
                    suspect
                  </Chip>
                ) : (
                  <Chip tone="good">clean</Chip>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Links({ refdomains, ahrefs }) {
  const rd = refdomains || {};
  const all = Array.isArray(rd.all) ? rd.all : [];
  const new30 = Array.isArray(rd.new_30d) ? rd.new_30d : [];
  const lost = Array.isArray(rd.lost) ? rd.lost : [];
  const [cleanOnly, setCleanOnly] = useState(false);

  const clean = rd.clean_count ?? 0;
  const suspect = rd.suspect_count ?? 0;
  const profiled = clean + suspect;
  const ahrefsLive = ahrefs?.backlinks?.live_refdomains ?? null;

  const buckets = useMemo(() => {
    const live = all.filter((r) => !r.lost);
    return BUCKETS.map((b) => {
      const inB = live.filter((r) => (Number(r.dr) || 0) >= b.lo && (Number(r.dr) || 0) <= b.hi);
      return {
        ...b,
        total: inB.length,
        clean: inB.filter((r) => !r.suspect).length,
        suspect: inB.filter((r) => r.suspect).length,
      };
    });
  }, [all]);

  const maxBucket = Math.max(1, ...buckets.map((b) => b.total));

  const newFiltered = cleanOnly ? new30.filter((r) => !r.suspect) : new30;
  const newClean = new30.filter((r) => !r.suspect).length;

  return (
    <Section
      id="links"
      n={7}
      title="Links"
      subtitle={`Referring-domain profile from the Ahrefs snapshot of ${ahrefs?.date || '—'}. The raw count is not the number that matters — the clean count is.`}
    >
      <div className="grid-2">
        <Card title="Referring-domain quality" sub="Every live domain in the profile, classified">
          <div className="quality-head">
            <div className="quality-big">
              <span className="mono good">{num(clean)}</span>
              <span className="quality-sep">/</span>
              <span className="mono bad">{num(suspect)}</span>
            </div>
            <div className="quality-legend">
              <div>
                <span className="swatch" style={{ background: 'var(--good)' }} /> clean —{' '}
                <strong>{profiled ? pct((clean / profiled) * 100, 0) : DASH}</strong> of the profile
              </div>
              <div>
                <span className="swatch" style={{ background: 'var(--bad)' }} /> suspect — spam-signature TLD, or
                &lt;10 monthly visits and DR&nbsp;&lt;&nbsp;15
              </div>
            </div>
          </div>
          <SplitBar
            parts={[
              { label: 'clean', value: clean, color: 'var(--good)' },
              { label: 'suspect', value: suspect, color: 'var(--bad)' },
            ]}
            height={30}
          />
          <div className="quality-stats">
            <Stat label="Live refdomains (Ahrefs)" value={num(ahrefsLive)} sub="the headline number" />
            <Stat label="Classified here" value={num(profiled)} sub={`${num(all.length)} rows pulled`} />
            <Stat label="New in 30d" value={num(rd.new_30d_count)} sub={`${num(rd.new_30d_suspect)} of them suspect`} tone="warn" />
            <Stat label="Lost in 30d" value={num(lost.length)} sub="dropped off the profile" />
          </div>
          {ahrefsLive && profiled && ahrefsLive !== profiled ? (
            <p className="note">
              Ahrefs' headline count is <strong>{num(ahrefsLive)}</strong> live referring domains; classifying the full{' '}
              {num(all.length)}-row profile gives <strong>{num(profiled)}</strong> live ({num(lost.length)} lost). The
              small gap is Ahrefs' own live/lost accounting — the quality split below is computed on all{' '}
              {num(profiled)}.
            </p>
          ) : null}
        </Card>

        <Card title="Authority distribution" sub="Live referring domains by Domain Rating, split by quality">
          {buckets.every((b) => b.total === 0) ? (
            <NoData detail="No referring-domain rows in the payload." />
          ) : (
            <div className="bucket-list">
              {buckets.map((b) => (
                <div className="bucket" key={b.key}>
                  <div className="bucket-label">{b.label}</div>
                  <div className="bucket-bar">
                    <div className="bucket-seg good" style={{ width: `${(b.clean / maxBucket) * 100}%` }} title={`${b.clean} clean`} />
                    <div className="bucket-seg bad" style={{ width: `${(b.suspect / maxBucket) * 100}%` }} title={`${b.suspect} suspect`} />
                  </div>
                  <div className="bucket-nums mono">
                    <span className="good">{b.clean}</span>
                    <span className="muted">/</span>
                    <span className="bad">{b.suspect}</span>
                    <span className="muted"> of {b.total}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="mini-stats">
            <Stat label="Domain Rating" value={num(ahrefs?.domain_rating, 1)} />
            <Stat label="Live backlinks" value={compact(ahrefs?.backlinks?.live)} sub={`${compact(ahrefs?.backlinks?.all_time)} all-time`} />
            <Stat label="All-time refdomains" value={num(ahrefs?.backlinks?.all_time_refdomains)} />
          </div>
        </Card>
      </div>

      <Card
        title={`New referring domains — last 30 days (${num(new30.length)})`}
        sub={`${num(newClean)} clean · ${num(rd.new_30d_suspect)} suspect. The suspect wave is what pushed the raw count from 9 to ${num(ahrefsLive)}.`}
        right={<Switch checked={cleanOnly} onChange={setCleanOnly} label="Clean only" />}
        pad={false}
      >
        <DomainTable rows={newFiltered} empty="No new referring domains in the last 30 days." />
      </Card>

      <Card title={`Lost referring domains (${num(lost.length)})`} sub="Dropped out of the live profile" pad={false}>
        <DomainTable rows={lost} empty="No domains lost recently." showLost />
      </Card>
    </Section>
  );
}
