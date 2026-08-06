import React, { useMemo, useState } from 'react';
import { Section, Card, Chip, SortTH, CellDelta, Toggle, ExternalLink } from '../components/ui';
import { useSort } from '../lib/hooks';
import { num, pct, shortDateYear, isNil, DASH } from '../lib/format';

function statusOf(a) {
  if ((a.age_days ?? 999) <= 21) return { key: 'new', label: 'new', tone: 'info' };
  if ((a.d_clicks ?? 0) < 0) return { key: 'decay', label: 'decaying', tone: 'bad' };
  if ((a.d_clicks ?? 0) > 0) return { key: 'rising', label: 'rising', tone: 'good' };
  if ((a.d_impressions ?? 0) > 0) return { key: 'rising', label: 'impr. up', tone: 'good' };
  return { key: 'flat', label: 'flat', tone: 'neutral' };
}

function QueryRows({ queries }) {
  if (!queries || queries.length === 0) {
    return (
      <div className="subtable-empty">No queries recorded for this URL in the last 28 days.</div>
    );
  }
  return (
    <div className="subtable-wrap">
      <table className="data-table sub">
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }} scope="col">Query</th>
            <th scope="col">Clicks</th>
            <th scope="col">Impr</th>
            <th scope="col">Position</th>
            <th scope="col">Type</th>
          </tr>
        </thead>
        <tbody>
          {queries.map((q, i) => (
            <tr key={q.query + i}>
              <td style={{ textAlign: 'left' }}>{q.query}</td>
              <td className="mono">{num(q.clicks)}</td>
              <td className="mono">{num(q.impressions)}</td>
              <td className="mono">{num(q.position, 1)}</td>
              <td>
                <Chip tone={q.brand ? 'neutral' : 'info'}>{q.brand ? 'brand' : 'non-brand'}</Chip>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Content({ articles }) {
  const rows = Array.isArray(articles) ? articles : [];
  const sort = useSort('impressions', 'desc');
  const [filter, setFilter] = useState('all');
  const [q, setQ] = useState('');
  const [open, setOpen] = useState(() => new Set());

  const enriched = useMemo(
    () => rows.map((a) => ({ ...a, _status: statusOf(a), _kw: a.primary_kw || a.top_query || null })),
    [rows],
  );

  const counts = useMemo(() => {
    const c = { all: enriched.length, rising: 0, decay: 0, new: 0 };
    enriched.forEach((a) => {
      if (a._status.key === 'rising') c.rising++;
      if (a._status.key === 'decay') c.decay++;
      if (a._status.key === 'new') c.new++;
    });
    return c;
  }, [enriched]);

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return enriched.filter((a) => {
      if (filter !== 'all' && a._status.key !== filter) return false;
      if (!needle) return true;
      return (
        (a.title || '').toLowerCase().includes(needle) ||
        (a._kw || '').toLowerCase().includes(needle) ||
        (a.slug || '').toLowerCase().includes(needle)
      );
    });
  }, [enriched, filter, q]);

  const sorted = sort.sorter(filtered, {
    title: (a) => a.title,
    published_at: (a) => a.published_at,
    _kw: (a) => a._kw,
    best_rank: (a) => a.best_rank,
  });

  function toggleRow(slug) {
    setOpen((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  }

  return (
    <Section
      id="content"
      n={5}
      title="Content performance"
      subtitle={`${rows.length} published posts, GSC last 28 days vs the prior 28. Click a row to see the queries it actually ranks for.`}
      right={
        <Toggle
          ariaLabel="Article filter"
          size="sm"
          value={filter}
          onChange={setFilter}
          options={[
            { value: 'all', label: `All ${counts.all}` },
            { value: 'rising', label: `Rising ${counts.rising}` },
            { value: 'decay', label: `Decaying ${counts.decay}` },
            { value: 'new', label: `New ${counts.new}` },
          ]}
        />
      }
    >
      <Card pad={false}>
        <div className="table-toolbar">
          <input
            className="search"
            type="search"
            placeholder="Filter by title, slug or keyword…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            aria-label="Filter articles"
          />
          <span className="muted mono">{sorted.length} shown</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 22 }} scope="col" aria-label="expand" />
                <SortTH label="Post" k="title" sort={sort} align="left" preferred="asc" />
                <SortTH label="Published" k="published_at" sort={sort} align="right" />
                <SortTH label="Age" k="age_days" sort={sort} title="Days since publication" />
                <SortTH label="Target / top keyword" k="_kw" sort={sort} align="left" preferred="asc" />
                <SortTH label="Vol" k="volume" sort={sort} title="Ahrefs monthly search volume for the target keyword" />
                <SortTH label="KD" k="kd" sort={sort} title="Ahrefs keyword difficulty" />
                <SortTH label="Clicks" k="clicks" sort={sort} />
                <SortTH label="Δ" k="d_clicks" sort={sort} title="Click change vs prior 28 days" />
                <SortTH label="Impr" k="impressions" sort={sort} />
                <SortTH label="Δ" k="d_impressions" sort={sort} title="Impression change vs prior 28 days" />
                <SortTH label="CTR" k="ctr" sort={sort} />
                <SortTH label="Pos" k="position" sort={sort} title="Average GSC position (lower is better)" />
                <SortTH label="Ahrefs best" k="best_rank" sort={sort} title="Best Ahrefs organic rank for this URL" />
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {sorted.length === 0 ? (
                <tr>
                  <td colSpan={15} className="empty-cell">
                    No posts match this filter.
                  </td>
                </tr>
              ) : null}
              {sorted.map((a) => {
                const isOpen = open.has(a.slug);
                return (
                  <React.Fragment key={a.slug}>
                    <tr className={'row-clickable' + (isOpen ? ' open' : '')} onClick={() => toggleRow(a.slug)}>
                      <td className="expander" aria-hidden="true">{isOpen ? '▾' : '▸'}</td>
                      <td style={{ textAlign: 'left' }} className="cell-title">
                        <ExternalLink href={a.url}>{a.title}</ExternalLink>
                      </td>
                      <td className="mono nowrap">{a.published_at ? shortDateYear(a.published_at) : DASH}</td>
                      <td className="mono">{isNil(a.age_days) ? DASH : `${num(a.age_days)}d`}</td>
                      <td style={{ textAlign: 'left' }} className="cell-kw">
                        {a._kw ? (
                          <>
                            {a._kw}
                            {!a.primary_kw ? (
                              <span className="kw-fallback" title="No target keyword in the backlog — showing the top GSC query instead">
                                top query
                              </span>
                            ) : null}
                          </>
                        ) : (
                          <span className="muted">{DASH}</span>
                        )}
                      </td>
                      <td className="mono">{isNil(a.volume) ? DASH : num(a.volume)}</td>
                      <td className="mono">{isNil(a.kd) ? DASH : num(a.kd)}</td>
                      <td className="mono strong">{num(a.clicks)}</td>
                      <td><CellDelta value={a.d_clicks} /></td>
                      <td className="mono">{num(a.impressions)}</td>
                      <td><CellDelta value={a.d_impressions} /></td>
                      <td className="mono">{isNil(a.ctr) ? DASH : pct(a.ctr, 2)}</td>
                      <td className="mono">{isNil(a.position) ? DASH : num(a.position, 1)}</td>
                      <td className="mono">
                        {isNil(a.best_rank) ? (
                          <span className="muted" title="Not in Ahrefs' organic keyword set">{DASH}</span>
                        ) : (
                          <span title={a.best_rank_kw || ''}>#{num(a.best_rank)}</span>
                        )}
                      </td>
                      <td>
                        <Chip tone={a._status.tone}>{a._status.label}</Chip>
                      </td>
                    </tr>
                    {isOpen ? (
                      <tr className="subrow">
                        <td colSpan={15}>
                          <div className="subrow-head">
                            <span>
                              Queries for <span className="mono">/{a.slug}</span>
                            </span>
                            <span className="muted">
                              {isNil(a.ranking_keywords) ? '' : `${num(a.ranking_keywords)} Ahrefs ranking keywords`}
                            </span>
                          </div>
                          <QueryRows queries={a.queries} />
                        </td>
                      </tr>
                    ) : null}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
      <p className="note">
        “Decaying” = a post older than 21 days that lost clicks vs the prior 28 days. Posts with no backlog entry show
        their top GSC query in place of a target keyword.
      </p>
    </Section>
  );
}
