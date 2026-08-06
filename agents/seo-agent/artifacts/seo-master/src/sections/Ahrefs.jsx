import React from 'react';
import { Card, Stat, ExternalLink, Chip } from '../components/ui';
import { HBar, NoData } from '../components/Charts';
import { centsToUsd, num, prettyUrl, shortDateYear, isNil, DASH } from '../lib/format';

/** Small aside: Ahrefs' organic estimate next to the paid (SEM) footprint. */
export function OrganicVsPaid({ ahrefs }) {
  const m = ahrefs?.metrics || {};
  const hist = Array.isArray(ahrefs?.history) ? ahrefs.history : [];
  const org = m.org_traffic || 0;
  const paid = m.paid_traffic || 0;
  const total = org + paid || 1;

  return (
    <Card
      title="Ahrefs estimate — organic vs paid"
      sub={`Snapshot ${ahrefs?.date || '—'}. Paid traffic is the SEM buy; it is kept out of every organic chart above.`}
    >
      <div className="hbars">
        <HBar label="Organic traffic / mo" value={org} total={total} color="var(--good)" right={num(org)} />
        <HBar label="Paid traffic / mo" value={paid} total={total} color="var(--warn)" right={num(paid)} />
      </div>
      <div className="mini-stats">
        <Stat label="Organic traffic value" value={centsToUsd(m.org_cost)} sub="per month, Ahrefs estimate" />
        <Stat label="Paid traffic value" value={centsToUsd(m.paid_cost)} sub={`${num(m.paid_keywords)} paid keywords`} tone="warn" />
        <Stat label="Organic keywords" value={num(m.org_keywords)} sub={`${num(m.org_keywords_1_3)} in the top 3`} />
      </div>
      {hist.length >= 2 ? (
        <div className="hist-strip">
          {hist.map((h) => (
            <div className="hist-cell" key={h.date}>
              <div className="hist-date mono">{shortDateYear(h.date)}</div>
              <div className="hist-row">
                <span className="good mono">{num(h.org_traffic)}</span> organic ·{' '}
                <span className="warn mono">{num(h.paid_traffic)}</span> paid
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="note">Only {hist.length} monthly history point from Ahrefs — not enough for a trend line.</p>
      )}
      <p className="note">
        Ahrefs sees just <strong>{num(org)}</strong> organic visits/mo against <strong>{num(m.org_keywords)}</strong>{' '}
        ranking keywords. Search Console is the ground truth for traffic; treat these as a directional third-party read.
      </p>
    </Card>
  );
}

/** The handful of keywords/pages Ahrefs actually credits us with. */
export function OrganicFootprint({ ahrefs }) {
  const kws = Array.isArray(ahrefs?.organic_keywords) ? ahrefs.organic_keywords : [];
  const pages = Array.isArray(ahrefs?.top_pages) ? ahrefs.top_pages : [];

  // The collector already rolls Ahrefs' per-locale rows up to one row per keyword+URL
  // (best position, highest volume, summed traffic) and reports how many locales merged.
  const uniq = kws;
  const multiLocale = uniq.filter((k) => (k.locales || 1) > 1);

  return (
    <Card
      title="Ahrefs organic footprint"
      sub={`${uniq.length} distinct keyword/URL pairs across ${pages.length} pages Ahrefs credits with traffic`}
    >
      {uniq.length === 0 ? (
        <NoData detail="Ahrefs credits no organic keywords yet." />
      ) : (
        <div className="table-scroll cap-sm">
          <table className="data-table compact">
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }} scope="col">Keyword</th>
                <th scope="col">Pos</th>
                <th scope="col">Volume</th>
                <th scope="col">KD</th>
                <th scope="col">Traffic</th>
                <th style={{ textAlign: 'left' }} scope="col">URL</th>
              </tr>
            </thead>
            <tbody>
              {uniq.map((k, i) => (
                <tr key={i}>
                  <td style={{ textAlign: 'left' }}>{k.keyword}</td>
                  <td className="mono strong">{isNil(k.best_position) ? DASH : `#${num(k.best_position)}`}</td>
                  <td className="mono">{num(k.volume)}</td>
                  <td className="mono">{num(k.keyword_difficulty)}</td>
                  <td className="mono">{num(k.sum_traffic)}</td>
                  <td style={{ textAlign: 'left' }} className="cell-title">
                    <ExternalLink href={k.best_position_url}>{prettyUrl(k.best_position_url)}</ExternalLink>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {multiLocale.length ? (
        <p className="note">
          {multiLocale.map((k) => `“${k.keyword}” (${k.locales})`).join(', ')} rank in multiple locales; each is shown
          as best position, highest reported volume and summed traffic across them.
        </p>
      ) : null}
      <div className="footprint-pages">
        {pages.map((p) => (
          <div className="fp-page" key={p.url}>
            <ExternalLink href={p.url}>{prettyUrl(p.url)}</ExternalLink>
            <span className="fp-meta mono">
              {num(p.sum_traffic)} visits · {num(p.keywords)} kw
            </span>
            {p.top_keyword ? (
              <Chip tone="neutral">
                {p.top_keyword} #{num(p.top_keyword_best_position)}
              </Chip>
            ) : null}
          </div>
        ))}
      </div>
    </Card>
  );
}
