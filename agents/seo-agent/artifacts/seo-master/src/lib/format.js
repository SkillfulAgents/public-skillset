export const DASH = '—';

export function isNil(v) {
  return v === null || v === undefined || (typeof v === 'number' && Number.isNaN(v));
}

export function num(v, digits = 0) {
  if (isNil(v)) return DASH;
  return Number(v).toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function compact(v) {
  if (isNil(v)) return DASH;
  const n = Number(v);
  const a = Math.abs(n);
  if (a >= 1_000_000) return (n / 1_000_000).toFixed(a >= 10_000_000 ? 0 : 1) + 'M';
  if (a >= 10_000) return (n / 1000).toFixed(a >= 100_000 ? 0 : 1) + 'k';
  return n.toLocaleString('en-US');
}

export function signed(v, digits = 0) {
  if (isNil(v)) return DASH;
  const n = Number(v);
  const s = Math.abs(n).toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  if (n > 0) return '+' + s;
  if (n < 0) return '−' + s; // true minus sign
  return '0';
}

export function pct(v, digits = 1) {
  if (isNil(v)) return DASH;
  return Number(v).toFixed(digits) + '%';
}

/** Ahrefs org_cost / paid_cost are in CENTS. */
export function centsToUsd(v) {
  if (isNil(v)) return DASH;
  const d = Number(v) / 100;
  if (d >= 10_000) return '$' + compact(Math.round(d));
  return '$' + d.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

export function shortDate(d) {
  if (!d) return DASH;
  const dt = new Date(String(d).length <= 10 ? d + 'T00:00:00Z' : d);
  if (Number.isNaN(+dt)) return String(d);
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
}

export function shortDateYear(d) {
  if (!d) return DASH;
  const dt = new Date(String(d).length <= 10 ? d + 'T00:00:00Z' : d);
  if (Number.isNaN(+dt)) return String(d);
  return dt.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

export function timeAgo(iso) {
  if (!iso) return DASH;
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return DASH;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

export function daysSince(dateStr) {
  if (!dateStr) return null;
  const t = new Date(String(dateStr).length <= 10 ? dateStr + 'T00:00:00Z' : dateStr).getTime();
  if (Number.isNaN(t)) return null;
  return Math.floor((Date.now() - t) / 86400000);
}

export function prettyUrl(u) {
  if (!u) return DASH;
  try {
    const url = new URL(u);
    const p = url.pathname === '/' ? '/' : url.pathname.replace(/\/$/, '');
    return p;
  } catch {
    return u;
  }
}

export function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

/** Parse loose numbers out of STATE.md strings: "~15.7k/wk", "12,674/wk", "—" */
export function loose(v) {
  if (isNil(v)) return null;
  if (typeof v === 'number') return v;
  const s = String(v).replace(/[,~\s]/g, '');
  const m = s.match(/^(-?\d+(?:\.\d+)?)([kKmM])?/);
  if (!m) return null;
  let n = parseFloat(m[1]);
  if (m[2]) n *= m[2].toLowerCase() === 'k' ? 1000 : 1_000_000;
  return n;
}
