import React, { useState } from 'react';
import { Section, Card, Chip, Stat, ExternalLink, RichText } from '../components/ui';
import { GroupedBars, NoData } from '../components/Charts';
import { num, shortDateYear, prettyUrl } from '../lib/format';

const TYPE_TONE = {
  content: 'info',
  links: 'violet',
  weekly: 'good',
  setup: 'neutral',
  technical: 'warn',
  other: 'neutral',
};

function ActivityItem({ a }) {
  const [open, setOpen] = useState(false);
  const bullets = Array.isArray(a.bullets) ? a.bullets : [];
  const summary = a.summary || '';
  const long = summary.length > 220 || bullets.length > 1;

  return (
    <li className="feed-item">
      <div className="feed-meta">
        <span className="mono feed-date">{shortDateYear(a.date)}</span>
        <Chip tone={TYPE_TONE[a.type] || 'neutral'}>{a.type}</Chip>
        {a.label && a.label !== a.type ? <span className="feed-label">{a.label}</span> : null}
        {a.followups_sent ? <span className="feed-stat mono">{a.followups_sent} follow-ups</span> : null}
        {a.new_sends ? <span className="feed-stat mono">{a.new_sends} new sends</span> : null}
      </div>
      {a.article_title ? <div className="feed-title">{a.article_title}</div> : null}
      <div className={'feed-summary' + (open ? '' : ' clamp')}>
        <RichText text={summary} />
      </div>
      {open && bullets.length > 1 ? (
        <ul className="feed-bullets">
          {bullets.slice(1).map((b, i) => (
            <li key={i}>
              <RichText text={b} />
            </li>
          ))}
        </ul>
      ) : null}
      <div className="feed-foot">
        {Array.isArray(a.published) && a.published.length
          ? a.published.map((u) => (
              <ExternalLink key={u} href={u}>
                {prettyUrl(u)}
              </ExternalLink>
            ))
          : null}
        {long ? (
          <button type="button" className="btn-link" onClick={() => setOpen((v) => !v)}>
            {open ? 'less' : 'more'}
          </button>
        ) : null}
      </div>
    </li>
  );
}

export default function Program({ velocity, activity }) {
  const weeks = Array.isArray(velocity) ? velocity : [];
  const feed = Array.isArray(activity) ? activity : [];
  const [limit, setLimit] = useState(15);

  const totals = weeks.reduce(
    (acc, w) => ({
      articles: acc.articles + (w.articles || 0),
      link_runs: acc.link_runs + (w.link_runs || 0),
      touches: acc.touches + (w.touches || 0),
    }),
    { articles: 0, link_runs: 0, touches: 0 },
  );

  return (
    <Section
      id="program"
      n={9}
      title="Program activity"
      subtitle="What the SEO agent actually shipped, week by week and run by run."
    >
      <div className="grid-2">
        <Card
          title="Weekly velocity"
          sub={weeks.length < 4 ? `Only ${weeks.length} weeks logged so far — trend lines come later` : 'Runs per week'}
        >
          {weeks.length === 0 ? (
            <NoData detail="No weekly rollups yet." />
          ) : (
            <GroupedBars
              data={weeks}
              xKey="week"
              height={180}
              minPointsNote="Three weeks of history — read these as counts, not a trend."
              series={[
                { key: 'articles', label: 'Articles published', color: '#38bdf8' },
                { key: 'content_runs', label: 'Content runs', color: '#818cf8' },
                { key: 'link_runs', label: 'Link runs', color: '#f472b6' },
                { key: 'touches', label: 'Outreach touches', color: '#34d399' },
              ]}
            />
          )}
          <div className="mini-stats">
            <Stat label="Articles shipped" value={num(totals.articles)} sub={`across ${weeks.length} weeks`} />
            <Stat label="Link runs" value={num(totals.link_runs)} />
            <Stat label="Outreach touches" value={num(totals.touches)} />
          </div>
        </Card>

        <Card title="Run mix" sub="Every logged run by type">
          {feed.length === 0 ? (
            <NoData detail="No activity entries." />
          ) : (
            <div className="mix">
              {Object.entries(
                feed.reduce((acc, a) => {
                  acc[a.type] = (acc[a.type] || 0) + 1;
                  return acc;
                }, {}),
              )
                .sort((a, b) => b[1] - a[1])
                .map(([t, n]) => (
                  <div className="mix-row" key={t}>
                    <Chip tone={TYPE_TONE[t] || 'neutral'}>{t}</Chip>
                    <div className="mix-track">
                      <div className="mix-fill" style={{ width: `${(n / feed.length) * 100}%` }} />
                    </div>
                    <span className="mono">{n}</span>
                  </div>
                ))}
            </div>
          )}
          <p className="note">
            {num(feed.length)} runs logged, newest {feed[0] ? shortDateYear(feed[0].date) : '—'}.
          </p>
        </Card>
      </div>

      <Card title="Run log" sub={`${feed.length} entries, newest first`} pad={false}>
        {feed.length === 0 ? (
          <div className="subtable-empty">No runs logged yet.</div>
        ) : (
          <>
            <ul className="feed">
              {feed.slice(0, limit).map((a, i) => (
                <ActivityItem key={a.date + a.type + i} a={a} />
              ))}
            </ul>
            {feed.length > limit ? (
              <div className="table-more">
                <button type="button" className="btn-ghost" onClick={() => setLimit((l) => l + 15)}>
                  Show more ({feed.length - limit} older)
                </button>
              </div>
            ) : null}
          </>
        )}
      </Card>
    </Section>
  );
}
