import React from 'react';
import { Section, Card, Chip, Stat, ExternalLink } from '../components/ui';
import { Funnel, HBar, MiniBars, NoData } from '../components/Charts';
import { num, pct, shortDateYear, daysSince, DASH, isNil } from '../lib/format';

const STATUS_TONE = {
  replied: '#34d399',
  closed_paid: '#fbbf24',
  sent: '#38bdf8',
  followed_up: '#818cf8',
  bounced: '#f87171',
  closed_no_response: '#64748b',
};

const STATUS_LABEL = {
  replied: 'Replied',
  closed_paid: 'Closed — wanted payment',
  sent: 'Sent, awaiting reply',
  followed_up: 'Followed up',
  bounced: 'Bounced',
  closed_no_response: 'Closed — no response',
};

export default function Outreach({ outreach }) {
  const o = outreach || {};
  const f = o.funnel || {};
  const byStatus = o.by_status || {};
  const active = Array.isArray(o.active) ? o.active : [];
  const due = Array.isArray(o.followups_due) ? o.followups_due : [];
  const won = Array.isArray(o.won) ? o.won : [];
  const timeline = Array.isArray(o.send_timeline) ? o.send_timeline : [];
  const cfg = o.config || {};

  const statusRows = Object.entries(byStatus).sort((a, b) => b[1] - a[1]);
  const statusTotal = statusRows.reduce((a, [, v]) => a + v, 0) || 1;
  const overdue = due.filter((d) => d.overdue);
  const highBounce = (o.bounce_rate ?? 0) >= 10;

  return (
    <Section
      id="outreach"
      n={8}
      title="Outreach"
      subtitle={
        cfg.inbox
          ? `Founder-voiced sends from ${cfg.inbox} · cap ${cfg.daily_limit}/day · follow-ups at day ${(
              cfg.followup_days || []
            ).join(' and ')} · max ${cfg.max_touches} touches · started ${cfg.first_send_date}.`
          : 'Link outreach pipeline.'
      }
    >
      <div className="grid-2">
        <Card title="Funnel" sub={`${num(o.total)} prospects since ${cfg.first_send_date || '—'}`}>
          <Funnel
            steps={[
              { label: 'Prospected', value: f.prospected ?? 0, color: '#64748b' },
              { label: 'Delivered', value: f.delivered ?? 0, color: '#38bdf8' },
              { label: 'Replied', value: f.replied ?? 0, color: '#34d399' },
              { label: 'Won (link placed)', value: f.won ?? 0, color: '#fbbf24' },
            ]}
          />
          <div className="mini-stats">
            <Stat
              label="Response rate"
              value={pct(o.response_rate, 1)}
              sub={`${num(f.replied)} replies of ${num(o.total)} prospects (${
                f.delivered ? ((f.replied / f.delivered) * 100).toFixed(1) : '—'
              }% of delivered)`}
            />
            <Stat
              label="Bounce rate"
              value={pct(o.bounce_rate, 1)}
              tone={highBounce ? 'warn' : 'neutral'}
              sub={highBounce ? `${num(o.bounced)} bounced — prospect list needs cleaning` : `${num(o.bounced)} bounced`}
            />
            <Stat label="Links won" value={num(f.won)} tone={(f.won ?? 0) === 0 ? 'muted' : 'good'} sub="no placements yet" />
          </div>
        </Card>

        <Card title="Prospect status" sub="Current state of every prospect in the CRM">
          {statusRows.length === 0 ? (
            <NoData detail="No prospects recorded." />
          ) : (
            <div className="hbars">
              {statusRows.map(([k, v]) => (
                <HBar
                  key={k}
                  label={STATUS_LABEL[k] || k.replace(/_/g, ' ')}
                  value={v}
                  total={statusTotal}
                  color={STATUS_TONE[k] || '#64748b'}
                />
              ))}
            </div>
          )}
          <div className="chart-heading spaced">
            <span className="chart-label">Touches sent per day</span>
            <span className="muted mono small">{num(timeline.reduce((a, r) => a + (r.touches || 0), 0))} total</span>
          </div>
          <MiniBars data={timeline} xKey="date" yKey="touches" label="Touches per day" />
        </Card>
      </div>

      <div className="grid-2">
        <Card
          title={`Live opportunities (${active.length})`}
          sub="Prospects that replied and are still in play"
        >
          {active.length === 0 ? (
            <NoData title="Nothing live right now" detail="No prospect is mid-conversation." />
          ) : (
            <div className="opps">
              {active.map((a) => (
                <div className="opp" key={a.domain}>
                  <div className="opp-head">
                    <ExternalLink href={`https://${a.domain}`}>{a.domain}</ExternalLink>
                    <span className="opp-tags">
                      <Chip tone="info">DR {num(a.dr)}</Chip>
                      <Chip tone="good">{a.status}</Chip>
                    </span>
                  </div>
                  {a.contact ? <div className="opp-contact">{a.contact}</div> : null}
                  <p className="opp-note">{a.note || 'No note recorded.'}</p>
                </div>
              ))}
            </div>
          )}
          {won.length === 0 ? (
            <p className="note">
              <strong>0 links won so far.</strong> Replies are converting to conversation, not placements — the funnel’s
              bottom step is empty by design of the data, not a rendering gap.
            </p>
          ) : null}
        </Card>

        <Card
          title={`Follow-ups due (${due.length})`}
          sub={overdue.length ? `${overdue.length} overdue` : 'All on schedule'}
          right={overdue.length ? <Chip tone="bad">{overdue.length} overdue</Chip> : null}
          pad={false}
        >
          {due.length === 0 ? (
            <div className="subtable-empty">Nothing due — the sequence is caught up.</div>
          ) : (
            <div className="table-scroll cap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left' }} scope="col">Domain</th>
                    <th scope="col">DR</th>
                    <th style={{ textAlign: 'left' }} scope="col">Contact</th>
                    <th style={{ textAlign: 'left' }} scope="col">Touch</th>
                    <th scope="col">Due</th>
                  </tr>
                </thead>
                <tbody>
                  {due.map((d) => {
                    const late = daysSince(d.due);
                    return (
                      <tr key={d.domain + d.touch} className={d.overdue ? 'row-alert' : ''}>
                        <td style={{ textAlign: 'left' }} className="cell-title">{d.domain}</td>
                        <td className="mono strong">{isNil(d.dr) ? DASH : num(d.dr)}</td>
                        <td style={{ textAlign: 'left' }}>{d.contact || <span className="muted">{DASH}</span>}</td>
                        <td style={{ textAlign: 'left' }} className="mono">{String(d.touch).replace('_', ' ')}</td>
                        <td className="mono nowrap">
                          {shortDateYear(d.due)}
                          {d.overdue ? (
                            <span className="bad"> · {late > 0 ? `${late}d late` : 'due'}</span>
                          ) : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </Section>
  );
}
