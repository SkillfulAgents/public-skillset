// Downloads built from the same review_math.py view the dashboard shows. Formatting only, no arithmetic.
import PDFDocument from 'pdfkit';

const NAMES = {wtd: 'Week to date', mtd: 'Month to date', last7: 'Last 7 days', last14: 'Last 14 days', last30: 'Last 30 days'};
const k = n => n == null ? 'unknown' : (n < 0 ? '-' : '') + '$' + (Math.abs(n) >= 1000 ? (Math.abs(n) / 1000).toFixed(Math.abs(n) >= 10000 ? 0 : 1) + 'k' : Math.round(Math.abs(n)));
const usd = n => n == null ? '' : '$' + Math.round(n).toLocaleString('en-US');
const range = (lo, hi) => lo == null || hi == null ? 'unknown' : Math.round(lo) === Math.round(hi) ? k(hi) : `${k(lo)}–${k(hi)}`;
const times = (lo, hi) => hi == null ? '–' : lo == null || lo.toFixed(1) === hi.toFixed(1) ? hi.toFixed(1) + '×' : `${lo.toFixed(1)}–${hi.toFixed(1)}×`;
const each = (lo, hi) => hi == null ? '' : lo == null || lo === hi ? usd(hi) : `${usd(lo)}–${usd(hi)}`;

function status(a, L) {
  if (a.idle) return 'idle';
  if (a.complete) return 'counted';
  if (a.flags.includes('no_access')) return 'no access';
  if (a.flags.includes('cost_unknown')) return 'cost unknown';
  return 'not fully read';
}

const delivered = a => Object.values(a.by_type).filter(r => r.count)
  .map(r => `${r.count} ${r.count === 1 && r.unit_one ? r.unit_one : r.unit} × ${each(r.unit_price_low, r.unit_price)}`);

export function fileName(view, ext) {
  const asOf = (view.numbers.leadership.freshness?.as_of || new Date().toISOString()).slice(0, 10);
  return `agent-roi-${view.period}-${asOf}.${ext}`;
}

// Spreadsheet cells that start with = + - @ run as formulas; prefix them so agent text can't.
const cell = v => {
  let s = v == null ? '' : String(v);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
const csv = rows => rows.map(r => r.map(cell).join(',')).join('\n') + '\n';

export function agentsCsv(view) {
  const L = view.numbers.leadership;
  const head = ['agent', 'owner', 'status', 'delivered', 'worth_low_usd', 'worth_usd', 'cash_usd', 'cost_ai_usd', 'cost_tools_usd',
    'people_time_usd', 'cost_total_usd', 'return_low', 'return_high', 'sessions_read', 'receipts', 'receipts_checked', 'range', 'from', 'to'];
  const rows = view.numbers.agents.map(a => [a.agent_name, a.owner, status(a, L), delivered(a).join('; '), a.value_low, a.total_value,
    a.hard_value, a.cost.ai, a.cost.tools, a.cost.people, a.cost.total, a.return_low, a.return_high, a.sessions_read, a.receipts,
    a.receipts_checked, NAMES[view.period] || view.period, L.window?.start?.slice(0, 10), L.window?.end ? new Date(new Date(L.window.end) - 1).toLocaleDateString('en-CA', {timeZone: L.window.timezone}) : '']);
  return csv([head, ...rows]);
}

export function outcomesCsv(view) {
  const name = Object.fromEntries(view.cards.map(c => [c.agent_id, c.agent_name]));
  const type = Object.fromEntries(view.cards.flatMap(c => c.outcome_types.map(t => [c.agent_id + '/' + t.id, t.name])));
  const head = ['agent', 'outcome', 'delivered_at', 'receipt', 'checked', 'worth_low_usd', 'worth_usd', 'price_source', 'session'];
  const rows = [...view.outcomes].sort((p, q) => (p.delivered_at < q.delivered_at ? 1 : -1)).map(o => [name[o.agent] || o.agent,
    type[o.agent + '/' + o.type] || o.type, o.delivered_at, o.receipt, o.status === 'verified' ? 'yes' : 'no', o.value_low, o.value,
    o.price_anchor, o.session]);
  return csv([head, ...rows]);
}

export function reportPdf(view) {
  const L = view.numbers.leadership, T = L.trust, F = L.freshness || {};
  const doc = new PDFDocument({size: 'LETTER', margin: 40, info: {Title: `Agent ROI: ${NAMES[view.period]}`}});
  const chunks = [];
  doc.on('data', c => chunks.push(c));
  const done = new Promise(r => doc.on('end', () => r(Buffer.concat(chunks))));
  const W = doc.page.width - 80, X = 40, ink = '#111', mut = '#666', line = '#ddd';
  const asOf = F.as_of ? new Date(F.as_of).toLocaleString('en-US', {timeZone: L.window.timezone, dateStyle: 'medium', timeStyle: 'short'}) + ' ' + new Intl.DateTimeFormat('en-US', {timeZone: L.window.timezone, timeZoneName: 'short'}).formatToParts(new Date(F.as_of)).find(p => p.type === 'timeZoneName').value : 'not read yet';

  doc.font('Helvetica-Bold').fontSize(16).fillColor(ink).text('Agent ROI', X, 40);
  doc.font('Helvetica').fontSize(9).fillColor(mut).text(`${NAMES[view.period]} · ${L.window?.label || ''} · as of ${asOf}`, X, 60);

  const tiles = [['Cost', k(L.total_cost), L.total_cost == null ? '' : L.people_in_cost ? `AI ${k(L.cost_parts.ai)} · tools ${k(L.cost_parts.tools)} · people's time ${k(L.cost_parts.people)} (estimate)` : `AI ${k(L.cost_parts.ai)} · tools ${k(L.cost_parts.tools)}`],
    ['Worth', range(L.counted_value_low, L.counted_value), `cash ${k(L.counted_hard_value)} · time freed ${range(L.counted_time_low, L.counted_soft_value)}`],
    ['Return', times(L.return_low, L.return_high), L.net_value != null ? `net (worth minus cost) ${range(L.net_value_low, L.net_value)}` : '']];
  const tw = (W - 16) / 3;
  tiles.forEach(([t, v, s], i) => {
    const x = X + i * (tw + 8);
    doc.roundedRect(x, 80, tw, 56, 4).strokeColor(line).stroke();
    doc.fontSize(8).fillColor(mut).text(t, x + 8, 87);
    doc.font('Helvetica-Bold').fontSize(15).fillColor(ink).text(v, x + 8, 99);
    doc.font('Helvetica').fontSize(7).fillColor(mut).text(s, x + 8, 120, {width: tw - 16});
  });
  doc.fontSize(7).fillColor(mut).text(`Totals cover fully counted agents, including any idle ones. Cost is Gamut usage spend (AI and tools)${L.people_in_cost ? ' plus people\'s time, an estimate from session message timing' : ''}.`, X, 140);

  const cols = [['Agent', 120], ['Delivered', W - 120 - 70 - 55 - 60], ['Worth', 70], ['Cost', 55], ['Return', 60]];
  let y = 158;
  const row = (cells, opts = {}) => {
    let x = X, h = 0;
    cells.forEach((c, i) => {
      const w = cols[i][1], right = i >= 2;
      if (i === 0 && opts.owner != null) {
        doc.font('Helvetica-Bold').fontSize(8).fillColor(ink).text(c, x, y, {width: w - 6});
        let hh = doc.heightOfString(c, {width: w - 6});
        if (opts.owner) { doc.font('Helvetica').fontSize(7).fillColor(mut).text(opts.owner, x, y + hh, {width: w - 6}); hh += doc.heightOfString(opts.owner, {width: w - 6}); }
        h = Math.max(h, hh); x += w; return;
      }
      doc.font(opts.bold && i === 0 ? 'Helvetica-Bold' : 'Helvetica').fontSize(opts.head ? 7 : 8).fillColor(opts.head || opts.muted ? mut : ink);
      doc.text(c, x + (right ? 0 : 0), y, {width: w - 6, align: right ? 'right' : 'left'});
      h = Math.max(h, doc.heightOfString(c, {width: w - 6}));
      x += w;
    });
    y += h + 5;
    doc.moveTo(X, y - 2).lineTo(X + W, y - 2).strokeColor(line).lineWidth(0.5).stroke();
  };
  row(cols.map(c => c[0]), {head: true});
  const A = view.numbers.agents, idle = A.filter(a => status(a, L) === 'idle');
  const bandRow = t => { doc.font('Helvetica-Bold').fontSize(7).fillColor(mut).text(t.toUpperCase(), X, y + 4); y += 16; };
  const active = A.filter(a => status(a, L) !== 'idle').sort((p, q) => q.total_value - p.total_value);
  [['Fully counted', active.filter(a => a.complete)], ['Incomplete', active.filter(a => !a.complete)]].forEach(([t, list]) => { if (!list.length) return; bandRow(`${t} (${list.length})`); list
    .forEach(a => row([a.agent_name, delivered(a).join('\n') || 'nothing counted',
      a.total_value ? range(a.value_low, a.total_value) : '–', k(a.cost.total), a.return_high != null ? times(a.return_low, a.return_high) : status(a, L)], {owner: a.owner || ''})); });
  if (idle.length) row([`Idle (${idle.length})`, idle.map(a => a.agent_name).join(', '), '', '', ''], {muted: true});

  y += 8;
  doc.font('Helvetica-Bold').fontSize(8).fillColor(ink).text('How far to trust this', X, y); y += 12;
  const pct = (a, b) => b ? Math.round(a / b * 100) + '%' : '–';
  const est = T.value_by_anchor.estimate || 0, tot = T.value_checked + T.value_unchecked;
  doc.font('Helvetica').fontSize(8).fillColor(ink).text(
    `Sessions read in this range: ${T.sessions_read.toLocaleString('en-US')}. Sessions not yet read in ${L.window.months.length > 1 ? 'these months' : 'this month'}: ${T.sessions_unread.toLocaleString('en-US')}. ` +
    `Agents fully counted: ${T.agents.counted}, not fully read: ${T.agents.partial}, cost unknown: ${T.agents.cost_unknown}, idle: ${T.agents.idle}. ` +
    `Worth with a checked receipt: ${k(T.value_checked)} of ${k(tot)} seen across all agents (${pct(T.value_checked, tot)}). Worth priced by review estimates rather than an owner or market rate: ${pct(est, tot)}.`, X, y, {width: W});
  y = doc.y + 6;
  const costUp = [], worthUp = [];
  L.left_out.forEach(x => { if (/cost unknown/.test(x.label)) costUp.push(x.label.split(':')[0] + "'s cost"); else if (/tied to no agent/.test(x.label)) costUp.push(`spend tied to no agent (${x.amount})`); });
  L.excludes.forEach(x => { if (/subscriptions or API keys/.test(x)) costUp.push("use on people's own subscriptions or keys"); else if (/outside its sessions/.test(x)) costUp.push("people's time outside sessions"); });
  if (T.partial_agents.length) worthUp.push(`${T.partial_agents.length} agents not fully read`);
  doc.fillColor(mut).text(`Not counted. Would raise cost: ${costUp.join(', ') || 'nothing'}. Would raise worth: ${worthUp.join(', ') || 'nothing'}. Left out by design: people's private agents.`, X, y, {width: W});
  doc.end();
  return done;
}
