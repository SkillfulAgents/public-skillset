import React, { useState } from 'react';
import { Section, Card, Chip, Stat, ExternalLink } from '../components/ui';
import { num, DASH, isNil } from '../lib/format';

function TodoList({ items, empty, limit, onMore, total }) {
  if (items.length === 0) return <div className="subtable-empty">{empty}</div>;
  return (
    <>
      <ul className="todos">
        {items.map((c, i) => (
          <li key={(c.title || '') + i}>
            <div className="todo-main">
              <span className="todo-title">{c.title}</span>
              {c.primary_kw ? (
                <span className="todo-kw mono">
                  {c.primary_kw}
                  {!isNil(c.volume) ? ` · ${num(c.volume)}/mo` : ''}
                  {!isNil(c.kd) ? ` · KD ${num(c.kd)}` : ''}
                </span>
              ) : null}
            </div>
            {c.section ? <div className="todo-section">{c.section}</div> : null}
            {c.url ? (
              <div className="todo-url">
                <ExternalLink href={c.url}>{c.url}</ExternalLink>
              </div>
            ) : null}
          </li>
        ))}
      </ul>
      {total > limit ? (
        <div className="table-more">
          <button type="button" className="btn-ghost" onClick={onMore}>
            Show more ({total - limit} remaining)
          </button>
        </div>
      ) : null}
    </>
  );
}

export default function Backlog({ backlog }) {
  const b = backlog || {};
  const cc = b.content_counts || {};
  const lc = b.link_counts || {};
  const content = Array.isArray(b.content) ? b.content : [];
  const links = Array.isArray(b.links) ? b.links : [];

  const [cLimit, setCLimit] = useState(6);
  const [lLimit, setLLimit] = useState(6);

  // The backlog has three states: done, todo and "later" (parked, needs prerequisites).
  // content_counts only counts todo/done, so keep "later" out of the runway numbers.
  const articleTodos = content.filter((c) => c.type === 'article' && c.status === 'todo');
  const surfaceTodos = content.filter((c) => c.type !== 'article' && c.status === 'todo');
  const laterItems = content.filter((c) => c.status === 'later');
  const openLinks = links.filter((l) => !l.done);
  const needsOwner = links.filter((l) => l.needs_owner);

  const daysOfRunway = cc.article_todo ?? 0; // ~1 article per weekday

  return (
    <Section
      id="backlog"
      n={10}
      title="Backlog & runway"
      subtitle="What is queued, and what is blocked on the owner."
    >
      <div className="stat-strip">
        <Stat label="Articles queued" value={num(cc.article_todo)} sub={`${num(cc.article_done)} shipped · ~${num(daysOfRunway)} weekdays of runway`} big />
        <Stat label="Surface tasks queued" value={num(cc.surface_todo)} sub={`${num(cc.surface_done)} done`} big />
        <Stat label="Link items open" value={num(lc.open)} sub={`${num(lc.done)} done`} big />
        <Stat label="Needs owner" value={num(lc.needs_owner)} tone={(lc.needs_owner ?? 0) > 0 ? 'warn' : 'neutral'} sub="blocked on the owner" big />
      </div>

      <div className="grid-2">
        <Card title={`Next up — articles (${articleTodos.length})`} sub="In backlog priority order" pad={false}>
          <TodoList
            items={articleTodos.slice(0, cLimit)}
            total={articleTodos.length}
            limit={cLimit}
            onMore={() => setCLimit((l) => l + 10)}
            empty="No articles queued — the content backlog needs replenishing."
          />
        </Card>

        <Card title={`Next up — link work (${openLinks.length})`} sub="Open items from the link backlog" pad={false}>
          <TodoList
            items={openLinks.slice(0, lLimit)}
            total={openLinks.length}
            limit={lLimit}
            onMore={() => setLLimit((l) => l + 10)}
            empty="No open link items."
          />
        </Card>
      </div>

      {laterItems.length ? (
        <p className="note">
          {laterItems.length} further item{laterItems.length === 1 ? '' : 's'} are parked as “later / needs
          prerequisites” and are excluded from the runway counts above:{' '}
          {laterItems.map((c) => c.title).join(' · ')}
        </p>
      ) : null}

      <div className="grid-2">
        <Card title={`Blocked on owner (${needsOwner.length})`} sub="Owner-only actions: launches, press pitches, spend">
          {needsOwner.length === 0 ? (
            <div className="subtable-empty">Nothing waiting on you.</div>
          ) : (
            <ul className="todos alert">
              {needsOwner.map((l, i) => (
                <li key={i}>
                  <div className="todo-main">
                    <span className="todo-title">{l.title}</span>
                    <Chip tone={l.done ? 'good' : 'warn'}>{l.done ? 'done' : 'open'}</Chip>
                  </div>
                  {l.section ? <div className="todo-section">{l.section}</div> : null}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title={`Surface work queued (${surfaceTodos.length})`} sub="Non-article SEO surfaces (hubs, templates, technical)">
          {surfaceTodos.length === 0 ? (
            <div className="subtable-empty">No surface work queued.</div>
          ) : (
            <ul className="todos">
              {surfaceTodos.slice(0, 8).map((c, i) => (
                <li key={i}>
                  <div className="todo-main">
                    <span className="todo-title">{c.title || DASH}</span>
                  </div>
                  {c.section ? <div className="todo-section">{c.section}</div> : null}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </Section>
  );
}
