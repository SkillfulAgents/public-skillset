import React, { useCallback, useEffect, useState } from 'react';
import Header from './sections/Header';
import { KpiRow, Targets } from './sections/Kpis';
import Trend from './sections/Trend';
import Content from './sections/Content';
import QueriesPages from './sections/QueriesPages';
import Links from './sections/Links';
import Outreach from './sections/Outreach';
import Program from './sections/Program';
import Backlog from './sections/Backlog';
import { SnapshotHistory, WeeklyHistory } from './sections/History';
import { OrganicVsPaid, OrganicFootprint } from './sections/Ahrefs';
import { Section } from './components/ui';
import { shortDateYear } from './lib/format';

function Skeleton() {
  return (
    <div className="skeleton">
      <div className="sk-line" style={{ width: '40%' }} />
      <div className="sk-grid">
        {Array.from({ length: 8 }).map((_, i) => (
          <div className="sk-card" key={i} />
        ))}
      </div>
      <div className="sk-card tall" />
      <p className="sk-msg">
        Running the collector… Search Console is cached for 15 minutes and Ahrefs for 6 hours, so this is usually under
        a second — up to ~15s when the cache is cold.
      </p>
    </div>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [fatal, setFatal] = useState(null);
  const [loadedAt, setLoadedAt] = useState(null);
  const [, tick] = useState(0);

  const load = useCallback(async (hard = false) => {
    if (hard) setRefreshing(true);
    else setLoading(true);
    setFatal(null);
    try {
      const res = await fetch(hard ? 'api/refresh' : 'api/data', {
        method: hard ? 'POST' : 'GET',
        headers: { Accept: 'application/json' },
      });
      const json = await res.json().catch(() => null);
      if (!res.ok || !json || json.fatal) {
        setFatal(
          (json && (json.error || json.collector_stderr)) ||
            `Request failed with HTTP ${res.status}. The collector may not be able to reach GSC or Ahrefs.`,
        );
        if (json && json.kpis) setData(json);
      } else {
        setData(json);
        setLoadedAt(new Date().toISOString());
      }
    } catch (err) {
      setFatal(`Could not reach the dashboard server: ${String((err && err.message) || err)}`);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(false);
  }, [load]);

  // keep the "x ago" chips honest
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 30000);
    return () => clearInterval(t);
  }, []);

  const onRefresh = useCallback(() => {
    const ok = window.confirm(
      'Hard refresh forces a live Ahrefs + Search Console pull.\n\nThis spends roughly 500-600 Ahrefs units from the monthly budget and takes ~15 seconds.\n\nContinue?',
    );
    if (ok) load(true);
  }, [load]);

  const showBody = !!data;

  return (
    <div className="app">
      <Header data={data} loading={loading} refreshing={refreshing} onRefresh={onRefresh} lastLoaded={loadedAt} />

      <main>
        {fatal ? (
          <div className="banner banner-error" role="alert">
            <strong>Collector error.</strong> {fatal}
            <button type="button" className="btn-ghost" onClick={() => load(false)}>
              Retry
            </button>
          </div>
        ) : null}

        {data?.stale && data?.error ? (
          <div className="banner banner-warn" role="status">
            <strong>Showing the last good snapshot.</strong> {data.error}
          </div>
        ) : null}

        {loading && !showBody ? <Skeleton /> : null}

        {showBody ? (
          <>
            <KpiRow kpis={data.kpis} ranges={data.gsc?.ranges} refdomains={data.refdomains} />

            <Section
              id="history"
              n={2}
              title="History"
              subtitle="Two separate histories: Ahrefs snapshots recorded by this collector, and the weekly checkpoints written into STATE.md."
            >
              <div className="grid-2">
                <SnapshotHistory kpiHistory={data.kpi_history} />
                <WeeklyHistory rows={data.kpi_history_state} />
              </div>
            </Section>

            <Trend gsc={data.gsc} />

            <Targets targets={data.targets} />

            <Content articles={data.articles} />

            <Section
              id="ahrefs"
              title="Third-party read (Ahrefs)"
              subtitle="Ahrefs' own view of the site — useful for link and SERP context, not for traffic truth."
            >
              <div className="grid-2">
                <OrganicVsPaid ahrefs={data.ahrefs} />
                <OrganicFootprint ahrefs={data.ahrefs} />
              </div>
            </Section>

            <QueriesPages gsc={data.gsc} />

            <Links refdomains={data.refdomains} ahrefs={data.ahrefs} />

            <Outreach outreach={data.outreach} />

            <Program velocity={data.velocity} activity={data.activity} />

            <Backlog backlog={data.backlog} />

            <footer className="app-footer">
              <span>
                Payload generated {data.generated_at ? new Date(data.generated_at).toLocaleString() : '—'} · GSC through{' '}
                {shortDateYear(data.gsc_data_through)} · Ahrefs snapshot {shortDateYear(data.ahrefs?.date)}
              </span>
              <span className="muted">
                Sources: Google Search Console API, Ahrefs v3, /workspace/seo backlogs + CRM. Nothing on this page is
                estimated by the dashboard itself.
              </span>
            </footer>
          </>
        ) : null}
      </main>
    </div>
  );
}
