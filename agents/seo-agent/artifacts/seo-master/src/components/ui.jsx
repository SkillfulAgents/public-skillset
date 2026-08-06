import React from 'react';
import { isNil, signed, DASH } from '../lib/format';

export function Section({ id, n, title, subtitle, right, children }) {
  return (
    <section className="section" id={id}>
      <header className="section-head">
        <div>
          <h2>
            {n ? <span className="section-n mono">{String(n).padStart(2, '0')}</span> : null}
            {title}
          </h2>
          {subtitle ? <p className="section-sub">{subtitle}</p> : null}
        </div>
        {right ? <div className="section-right">{right}</div> : null}
      </header>
      {children}
    </section>
  );
}

export function Card({ title, sub, right, children, className = '', pad = true }) {
  return (
    <div className={`card ${className}`}>
      {title || right ? (
        <div className="card-head">
          <div>
            <div className="card-title">{title}</div>
            {sub ? <div className="card-sub">{sub}</div> : null}
          </div>
          {right ? <div className="card-right">{right}</div> : null}
        </div>
      ) : null}
      <div className={pad ? 'card-body' : 'card-body flush'}>{children}</div>
    </div>
  );
}

export function Chip({ children, tone = 'neutral', title }) {
  return (
    <span className={`chip chip-${tone}`} title={title}>
      {children}
    </span>
  );
}

export function Toggle({ options, value, onChange, size = 'md', ariaLabel }) {
  return (
    <div className={`toggle toggle-${size}`} role="group" aria-label={ariaLabel}>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          className={value === o.value ? 'on' : ''}
          aria-pressed={value === o.value}
          onClick={() => onChange(o.value)}
          title={o.title}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Switch({ checked, onChange, label }) {
  return (
    <label className="switch">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="switch-box" aria-hidden="true" />
      <span>{label}</span>
    </label>
  );
}

export function SortTH({ label, k, sort, align = 'right', width, title, preferred = 'desc' }) {
  const active = sort.key === k;
  return (
    <th
      style={{ textAlign: align, width }}
      className={'sortable' + (active ? ' active' : '')}
      onClick={() => sort.toggle(k, preferred)}
      title={title || `Sort by ${label}`}
      scope="col"
    >
      <span className="th-inner">
        {label}
        <span className="sort-arrow">{active ? (sort.dir === 'asc' ? '▲' : '▼') : ''}</span>
      </span>
    </th>
  );
}

/**
 * Delta pill. goodUp=false inverts the colour (used by Avg position, where a
 * positive delta means the rank got WORSE).
 */
export function Delta({ value, pctValue, goodUp = true, digits = 0, showWord = true, suffix }) {
  if (isNil(value)) return <span className="delta none">no prior period</span>;
  const n = Number(value);
  if (n === 0) return <span className="delta flat mono">0 · flat</span>;
  const good = n > 0 === !!goodUp;
  const word = good ? 'better' : 'worse';
  return (
    <span className={`delta ${good ? 'good' : 'bad'} mono`}>
      <span aria-hidden="true">{n > 0 ? '▲' : '▼'}</span> {signed(n, digits)}
      {suffix || ''}
      {!isNil(pctValue) ? <span className="delta-pct"> {signed(pctValue, 1)}%</span> : null}
      {showWord ? <span className="delta-word"> {word}</span> : null}
    </span>
  );
}

/** Small inline numeric delta for table cells. */
export function CellDelta({ value, goodUp = true, digits = 0 }) {
  if (isNil(value)) return <span className="muted">{DASH}</span>;
  const n = Number(value);
  if (n === 0) return <span className="muted mono">0</span>;
  const good = n > 0 === !!goodUp;
  return <span className={`cell-delta ${good ? 'good' : 'bad'} mono`}>{signed(n, digits)}</span>;
}

export function Stat({ label, value, tone = 'neutral', sub, big }) {
  return (
    <div className={`stat stat-${tone}` + (big ? ' big' : '')}>
      <div className="stat-value mono">{value}</div>
      <div className="stat-label">{label}</div>
      {sub ? <div className="stat-sub">{sub}</div> : null}
    </div>
  );
}

/**
 * Minimal inline renderer for the run-log text, which is written in markdown-ish
 * shorthand (**bold**, `code`, bare URLs). No HTML is ever injected.
 */
export function RichText({ text }) {
  if (!text) return null;
  const parts = String(text).split(/(\*\*[^*]+\*\*|`[^`]+`|https?:\/\/[^\s)]+)/g);
  return (
    <>
      {parts.map((p, i) => {
        if (!p) return null;
        if (p.startsWith('**') && p.endsWith('**')) return <strong key={i}>{p.slice(2, -2)}</strong>;
        if (p.startsWith('`') && p.endsWith('`')) return <code key={i} className="inline-code">{p.slice(1, -1)}</code>;
        if (/^https?:\/\//.test(p))
          return (
            <a key={i} href={p} target="_blank" rel="noreferrer noopener">
              {p.replace(/^https?:\/\/(www\.)?/, '')}
            </a>
          );
        return <React.Fragment key={i}>{p}</React.Fragment>;
      })}
    </>
  );
}

export function ExternalLink({ href, children, title }) {
  if (!href) return <span className="muted">{DASH}</span>;
  return (
    <a href={href} target="_blank" rel="noreferrer noopener" title={title || href}>
      {children}
    </a>
  );
}
