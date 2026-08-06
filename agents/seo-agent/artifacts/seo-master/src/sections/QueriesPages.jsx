import React, { useMemo, useState } from 'react';
import { Section, Card, Chip, SortTH, CellDelta, Toggle, Switch, ExternalLink } from '../components/ui';
import { useSort } from '../lib/hooks';
import { num, pct, prettyUrl, isNil, DASH } from '../lib/format';

const PAGE_SIZE = 50;

function RankChange({ value }) {
  // d_position is already sign-flipped: POSITIVE = the rank improved.
  if (isNil(value)) return <span className="muted">{DASH}</span>;
  const n = Number(value);
  if (n === 0) return <span className="muted mono">0</span>;
  return (
    <span className={'cell-delta mono ' + (n > 0 ? 'good' : 'bad')} title={n > 0 ? 'moved up the SERP' : 'moved down the SERP'}>
      {n > 0 ? '▲' : '▼'} {Math.abs(n).toFixed(1)}
    </span>
  );
}

export default function QueriesPages({ gsc }) {
  const [tab, setTab] = useState('queries');
  const [brand, setBrand] = useState('nonbrand');
  const [moversOnly, setMoversOnly] = useState(false);
  const [limit, setLimit] = useState(PAGE_SIZE);
  const [q, setQ] = useState('');
  const [openPage, setOpenPage] = useState(null);

  const sort = useSort('impressions', 'desc');

  const queries = Array.isArray(gsc?.queries) ? gsc.queries : [];
  const pages = Array.isArray(gsc?.pages) ? gsc.pages : [];
  const pageQueries = gsc?.page_queries || {};
  const isQueries = tab === 'queries';
  const source = isQueries ? queries : pages;

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return source.filter((r) => {
      if (isQueries && brand !== 'all') {
        if (brand === 'brand' && !r.brand) return false;
        if (brand === 'nonbrand' && r.brand) return false;
      }
      if (moversOnly) {
        const moved = Math.abs(r.d_clicks || 0) > 0 || Math.abs(r.d_position || 0) >= 1 || r.is_new;
        if (!moved) return false;
      }
      if (!needle) return true;
      return String(isQueries ? r.query : r.page).toLowerCase().includes(needle);
    });
  }, [source, isQueries, brand, moversOnly, q]);

  const sorted = sort.sorter(filtered, {
    query: (r) => r.query,
    page: (r) => r.page,
  });
  const visible = sorted.slice(0, limit);

  const totals = useMemo(() => {
    const clicks = filtered.reduce((a, r) => a + (r.clicks || 0), 0);
    const impr = filtered.reduce((a, r) => a + (r.impressions || 0), 0);
    const dClicks = filtered.reduce((a, r) => a + (r.d_clicks || 0), 0);
    return { clicks, impr, dClicks };
  }, [filtered]);

  const ranges = gsc?.ranges || {};

  // page_key is the collector's normalised join key for page_queries
  function lookupPageQueries(row) {
    return pageQueries[row.page_key ?? String(row.page).replace(/\/$/, '')] || null;
  }

  return (
    <Section
      id="queries"
      n={6}
      title="Queries & pages"
      subtitle={
        ranges.cur
          ? `Top ${source.length} by impressions. ${ranges.cur[0]} → ${ranges.cur[1]} vs ${ranges.prev?.[0]} → ${ranges.prev?.[1]}. “Rank change” is sign-flipped: ▲ means the position improved.`
          : 'Top rows by impressions, 28 days vs prior 28.'
      }
      right={
        <Toggle
          ariaLabel="Table"
          value={tab}
          onChange={(v) => {
            setTab(v);
            setLimit(PAGE_SIZE);
            setOpenPage(null);
          }}
          options={[
            { value: 'queries', label: `Queries (${queries.length})` },
            { value: 'pages', label: `Pages (${pages.length})` },
          ]}
        />
      }
    >
      <Card pad={false}>
        <div className="table-toolbar wrap">
          <input
            className="search"
            type="search"
            placeholder={isQueries ? 'Filter queries…' : 'Filter URLs…'}
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setLimit(PAGE_SIZE);
            }}
            aria-label="Filter rows"
          />
          {isQueries ? (
            <Toggle
              ariaLabel="Brand filter"
              size="sm"
              value={brand}
              onChange={(v) => {
                setBrand(v);
                setLimit(PAGE_SIZE);
              }}
              options={[
                { value: 'nonbrand', label: 'Non-brand' },
                { value: 'brand', label: 'Brand' },
                { value: 'all', label: 'All' },
              ]}
            />
          ) : (
            <span className="muted small" title="GSC does not attach a brand flag to page rows">
              brand filter is query-only
            </span>
          )}
          <Switch checked={moversOnly} onChange={setMoversOnly} label="Movers only" />
          <span className="toolbar-totals mono muted">
            {num(totals.clicks)} clicks ({totals.dClicks >= 0 ? '+' : '−'}
            {num(Math.abs(totals.dClicks))}) · {num(totals.impr)} impressions · {sorted.length} rows
          </span>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                {!isQueries ? <th style={{ width: 22 }} aria-label="expand" scope="col" /> : null}
                <SortTH
                  label={isQueries ? 'Query' : 'Page'}
                  k={isQueries ? 'query' : 'page'}
                  sort={sort}
                  align="left"
                  preferred="asc"
                />
                <SortTH label="Clicks" k="clicks" sort={sort} />
                <SortTH label="Δ clicks" k="d_clicks" sort={sort} />
                <SortTH label="Impr" k="impressions" sort={sort} />
                <SortTH label="Δ impr" k="d_impressions" sort={sort} />
                <SortTH label="CTR" k="ctr" sort={sort} />
                <SortTH label="Pos" k="position" sort={sort} title="Average position (lower is better)" />
                <SortTH label="Rank change" k="d_position" sort={sort} title="Positive = improved (moved up)" />
                <th scope="col">Flags</th>
              </tr>
            </thead>
            <tbody>
              {visible.length === 0 ? (
                <tr>
                  <td colSpan={isQueries ? 9 : 10} className="empty-cell">
                    Nothing matches these filters.
                  </td>
                </tr>
              ) : null}
              {visible.map((r, i) => {
                const key = (isQueries ? r.query : r.page) + i;
                const url = r.page;
                const isOpen = !isQueries && openPage === url;
                const pq = !isQueries ? lookupPageQueries(r) : null;
                return (
                  <React.Fragment key={key}>
                    <tr
                      className={!isQueries ? 'row-clickable' + (isOpen ? ' open' : '') : undefined}
                      onClick={!isQueries ? () => setOpenPage(isOpen ? null : url) : undefined}
                    >
                      {!isQueries ? <td className="expander">{isOpen ? '▾' : '▸'}</td> : null}
                      <td style={{ textAlign: 'left' }} className="cell-title">
                        {isQueries ? (
                          r.query
                        ) : (
                          <ExternalLink href={url}>{prettyUrl(url)}</ExternalLink>
                        )}
                      </td>
                      <td className="mono strong">{num(r.clicks)}</td>
                      <td><CellDelta value={r.d_clicks} /></td>
                      <td className="mono">{num(r.impressions)}</td>
                      <td><CellDelta value={r.d_impressions} /></td>
                      <td className="mono">{isNil(r.ctr) ? DASH : pct(r.ctr, 2)}</td>
                      <td className="mono">{isNil(r.position) ? DASH : num(r.position, 1)}</td>
                      <td><RankChange value={r.d_position} /></td>
                      <td className="flags">
                        {r.is_new ? <Chip tone="info">new</Chip> : null}
                        {isQueries && r.brand ? <Chip tone="neutral">brand</Chip> : null}
                      </td>
                    </tr>
                    {isOpen ? (
                      <tr className="subrow">
                        <td colSpan={10}>
                          <div className="subrow-head">
                            <span>Top queries for this page</span>
                          </div>
                          {pq && pq.length ? (
                            <div className="subtable-wrap">
                              <table className="data-table sub">
                                <thead>
                                  <tr>
                                    <th style={{ textAlign: 'left' }} scope="col">Query</th>
                                    <th scope="col">Clicks</th>
                                    <th scope="col">Impr</th>
                                    <th scope="col">Pos</th>
                                    <th scope="col">Type</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {pq.map((x, j) => (
                                    <tr key={x.query + j}>
                                      <td style={{ textAlign: 'left' }}>{x.query}</td>
                                      <td className="mono">{num(x.clicks)}</td>
                                      <td className="mono">{num(x.impressions)}</td>
                                      <td className="mono">{num(x.position, 1)}</td>
                                      <td>
                                        <Chip tone={x.brand ? 'neutral' : 'info'}>{x.brand ? 'brand' : 'non-brand'}</Chip>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <div className="subtable-empty">
                              No per-query breakdown captured for this URL — the collector only stores the top ~100
                              pages’ query lists.
                            </div>
                          )}
                        </td>
                      </tr>
                    ) : null}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>

        {sorted.length > visible.length ? (
          <div className="table-more">
            <button type="button" className="btn-ghost" onClick={() => setLimit((l) => l + 100)}>
              Show 100 more ({sorted.length - visible.length} hidden)
            </button>
          </div>
        ) : null}
      </Card>
    </Section>
  );
}
