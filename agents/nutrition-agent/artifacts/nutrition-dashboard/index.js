import { Database } from "bun:sqlite";
import { readFileSync, existsSync } from "fs";

const port = process.env.DASHBOARD_PORT || 3000;
const DB_PATH = "/workspace/nutrition/data/nutrition.db";
const GOAL_PATH = "/workspace/nutrition/data/goal.json";

const TZ = "America/Los_Angeles";

function todayLocal() {
  const fmt = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" });
  return fmt.format(new Date());
}

function loadGoal() {
  if (existsSync(GOAL_PATH)) return JSON.parse(readFileSync(GOAL_PATH, "utf8"));
  return { calories: 2200, protein_g: 160, fat_g: 70, carbs_g: 220, rationale: "default" };
}

function getData(days = 30) {
  const db = new Database(DB_PATH, { readonly: true });
  try {
    const today = todayLocal();
    // build date range
    const startDate = new Date(today + "T00:00:00");
    startDate.setDate(startDate.getDate() - (days - 1));
    const start = startDate.toISOString().slice(0, 10);

    const dayRows = db.query(
      `SELECT local_day,
              ROUND(SUM(calories),1)  AS calories,
              ROUND(SUM(protein_g),1) AS protein_g,
              ROUND(SUM(fat_g),1)     AS fat_g,
              ROUND(SUM(carbs_g),1)   AS carbs_g,
              COUNT(*)                AS meal_count
       FROM meals
       WHERE local_day >= ? AND local_day <= ?
       GROUP BY local_day
       ORDER BY local_day`
    ).all(start, today);

    const meals = db.query(
      `SELECT id, ts, local_day, name, description,
              calories, protein_g, fat_g, carbs_g
       FROM meals
       WHERE local_day >= ? AND local_day <= ?
       ORDER BY ts DESC`
    ).all(start, today);

    const weights = db.query(
      `SELECT local_day, weight_lbs, note
       FROM weights
       WHERE local_day >= ? AND local_day <= ?
       ORDER BY local_day`
    ).all(start, today);

    // fill missing days with zeros
    const byDay = new Map(dayRows.map((r) => [r.local_day, r]));
    const out = [];
    const d = new Date(start + "T00:00:00");
    const endD = new Date(today + "T00:00:00");
    while (d <= endD) {
      const key = d.toISOString().slice(0, 10);
      out.push(byDay.get(key) ?? { local_day: key, calories: 0, protein_g: 0, fat_g: 0, carbs_g: 0, meal_count: 0 });
      d.setDate(d.getDate() + 1);
    }

    return { today, goal: loadGoal(), days: out, meals, weights };
  } finally {
    db.close();
  }
}

Bun.serve({
  port,
  fetch(req) {
    const url = new URL(req.url);
    console.log(`${new Date().toISOString()} ${req.method} ${url.pathname}${url.search}`);

    if (url.pathname === "/api/data") {
      try {
        const days = parseInt(url.searchParams.get("days") || "30", 10);
        const data = getData(days);
        return Response.json(data);
      } catch (e) {
        console.error("api/data error:", e);
        return Response.json({ error: String(e) }, { status: 500 });
      }
    }

    if (url.pathname === "/" || url.pathname === "") {
      return new Response(HTML, { headers: { "Content-Type": "text/html", "Cache-Control": "no-store" } });
    }
    return new Response("Not Found", { status: 404 });
  },
});

const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Nutrition Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.2.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
  :root {
    --bg: #0f1115;
    --panel: #181b22;
    --panel-2: #1f232c;
    --fg: #e8e9ec;
    --dim: #8a8f99;
    --accent-cal: #ff4b5f;
    --accent-pro: #78e682;
    --accent-fat: #ffc850;
    --accent-carb: #5ab4ff;
    --border: #262a33;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif;
    line-height: 1.4;
  }
  header {
    padding: 24px 32px;
    border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }
  header h1 { margin: 0; font-size: 22px; letter-spacing: -0.01em; }
  header .meta { color: var(--dim); font-size: 14px; }
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px 32px 64px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
  }
  .card h2 { margin: 0 0 16px; font-size: 14px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }
  .col-span { grid-column: span 2; }
  .today-grid { display: grid; grid-template-columns: auto 1fr; gap: 24px; align-items: center; }
  .rings { width: 200px; height: 200px; }
  .totals { display: grid; gap: 8px; }
  .totals .row { display: grid; grid-template-columns: 8px 90px 1fr auto; gap: 10px; align-items: center; }
  .swatch { width: 8px; height: 24px; border-radius: 2px; }
  .label { color: var(--dim); font-size: 13px; }
  .value { font-weight: 600; font-variant-numeric: tabular-nums; }
  .goal { color: var(--dim); font-size: 12px; font-variant-numeric: tabular-nums; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--border); }
  th { color: var(--dim); font-weight: 500; text-transform: uppercase; font-size: 11px; letter-spacing: 0.08em; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  .pill { display: inline-block; padding: 2px 8px; border-radius: 999px; background: var(--panel-2); font-size: 11px; color: var(--dim); text-transform: capitalize; }
  .chart-wrap { position: relative; height: 280px; }
  select { background: var(--panel-2); color: var(--fg); border: 1px solid var(--border); padding: 6px 10px; border-radius: 8px; font-size: 13px; }
  .empty { color: var(--dim); padding: 16px; text-align: center; font-size: 13px; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Nutrition</h1>
    <div class="meta" id="today-label">—</div>
  </div>
  <div style="display:flex; gap:10px; align-items:center;">
    <span class="label" id="updated">—</span>
    <button id="refresh" style="background:var(--panel-2); color:var(--fg); border:1px solid var(--border); padding:6px 12px; border-radius:8px; font-size:13px; cursor:pointer;">Refresh</button>
    <label class="label" for="range">Range </label>
    <select id="range">
      <option value="7">7 days</option>
      <option value="14">14 days</option>
      <option value="30" selected>30 days</option>
      <option value="90">90 days</option>
    </select>
  </div>
</header>
<div id="error" style="display:none; margin:16px 32px; padding:12px 16px; background:#3a1a1f; border:1px solid #ff4b5f; border-radius:8px; color:#ffb4be; font-family:monospace; font-size:12px;"></div>
<main>
  <section class="card">
    <h2>Today</h2>
    <div class="today-grid">
      <canvas class="rings" id="rings" width="200" height="200"></canvas>
      <div class="totals" id="today-totals"></div>
    </div>
  </section>

  <section class="card">
    <h2>Goal</h2>
    <div id="goal-info"></div>
  </section>

  <section class="card col-span">
    <h2>Daily Calories</h2>
    <div class="chart-wrap"><canvas id="cal-chart"></canvas></div>
  </section>

  <section class="card col-span">
    <h2>Macros (g) by day</h2>
    <div class="chart-wrap"><canvas id="macro-chart"></canvas></div>
  </section>

  <section class="card col-span">
    <h2>Weight (lbs)</h2>
    <div id="weight-summary" style="margin-bottom:12px"></div>
    <div class="chart-wrap" style="height:220px"><canvas id="weight-chart"></canvas></div>
    <div id="weight-table" style="margin-top:16px"></div>
  </section>

  <section class="card col-span">
    <h2>Meal History</h2>
    <div id="meals-table"></div>
  </section>
</main>

<script>
const COLORS = { cal: "#ff4b5f", pro: "#78e682", fat: "#ffc850", carb: "#5ab4ff", dim: "#8a8f99", track: "#262a33" };
let calChart, macroChart, weightChart;

function fmt(n, d = 0) { return Number(n || 0).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d }); }

function drawRings(canvas, calProg, proProg) {
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const size = 200;
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = size + "px";
  canvas.style.height = size + "px";
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, size, size);
  const cx = size / 2, cy = size / 2;
  const ring = (r, w, p, color) => {
    ctx.lineWidth = w;
    ctx.strokeStyle = COLORS.track;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    if (p > 0) {
      ctx.strokeStyle = color;
      ctx.lineCap = "round";
      ctx.beginPath();
      const end = -Math.PI / 2 + Math.min(p, 1) * Math.PI * 2;
      ctx.arc(cx, cy, r, -Math.PI / 2, end);
      ctx.stroke();
    }
  };
  ring(78, 18, calProg, COLORS.cal);
  ring(54, 18, proProg, COLORS.pro);
  ctx.fillStyle = COLORS.cal;
  ctx.font = "600 18px system-ui";
  ctx.textAlign = "center";
  ctx.fillText(Math.round(calProg * 100) + "%", cx, cy - 6);
  ctx.fillStyle = COLORS.pro;
  ctx.font = "600 14px system-ui";
  ctx.fillText(Math.round(proProg * 100) + "%", cx, cy + 14);
}

function row(label, color, val, goal, unit) {
  const pct = goal ? (val / goal) * 100 : 0;
  return \`
    <div class="row">
      <div class="swatch" style="background:\${color}"></div>
      <div class="label">\${label}</div>
      <div class="value">\${fmt(val)}\${unit}</div>
      <div class="goal">/ \${fmt(goal)}\${unit} · \${pct.toFixed(0)}%</div>
    </div>\`;
}

async function load() {
  const errBox = document.getElementById("error");
  errBox.style.display = "none";
  try {
    const days = document.getElementById("range").value;
    // Use path-relative URL (no leading slash) so it works when the dashboard
    // is reverse-proxied under a path prefix by the Superagent UI.
    const apiUrl = new URL("api/data?days=" + days, document.baseURI);
    const res = await fetch(apiUrl.toString(), { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status + " " + (await res.text()));
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    renderAll(data);
    document.getElementById("updated").textContent = "Updated " + new Date().toLocaleTimeString();
  } catch (e) {
    errBox.style.display = "block";
    errBox.textContent = "Load failed: " + (e && e.message ? e.message : String(e));
    console.error(e);
  }
}

function renderAll(data) {

  document.getElementById("today-label").textContent = data.today;

  const todayRow = data.days[data.days.length - 1] || { calories: 0, protein_g: 0, fat_g: 0, carbs_g: 0 };
  const g = data.goal;
  const calProg = todayRow.calories / g.calories;
  const proProg = todayRow.protein_g / g.protein_g;
  drawRings(document.getElementById("rings"), calProg || 0, proProg || 0);

  document.getElementById("today-totals").innerHTML =
    row("Calories", COLORS.cal, todayRow.calories, g.calories, " kcal") +
    row("Protein", COLORS.pro, todayRow.protein_g, g.protein_g, " g") +
    row("Fat", COLORS.fat, todayRow.fat_g, g.fat_g, " g") +
    row("Carbs", COLORS.carb, todayRow.carbs_g, g.carbs_g, " g");

  document.getElementById("goal-info").innerHTML = \`
    <div class="totals">
      \${row("Calories", COLORS.cal, g.calories, g.calories, " kcal")}
      \${row("Protein", COLORS.pro, g.protein_g, g.protein_g, " g")}
      \${row("Fat", COLORS.fat, g.fat_g, g.fat_g, " g")}
      \${row("Carbs", COLORS.carb, g.carbs_g, g.carbs_g, " g")}
    </div>
    <p class="label" style="margin-top:14px">\${g.rationale ? g.rationale : "No rationale recorded."}</p>
  \`;

  // Charts
  const labels = data.days.map((d) => d.local_day.slice(5));
  const calData = data.days.map((d) => d.calories);

  const calColors = calData.map((c) => c > g.calories ? COLORS.fat : COLORS.pro);
  const calAvg7 = calData.map((_, i) => {
    const w = calData.slice(Math.max(0, i - 6), i + 1);
    return Math.round(w.reduce((a, b) => a + b, 0) / w.length);
  });

  if (calChart) calChart.destroy();
  calChart = new Chart(document.getElementById("cal-chart"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Calories", data: calData, backgroundColor: calColors, borderRadius: 4 },
        { label: "7-day avg", data: calAvg7, type: "line", borderColor: "#f5a623", backgroundColor: "transparent", borderWidth: 2, pointRadius: 0, tension: 0.4, order: -1 },
      ],
    },
    options: chartOpts(g.calories),
  });

  if (macroChart) macroChart.destroy();
  macroChart = new Chart(document.getElementById("macro-chart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Protein", data: data.days.map((d) => d.protein_g), borderColor: COLORS.pro, backgroundColor: COLORS.pro, tension: 0.3 },
        { label: "Fat", data: data.days.map((d) => d.fat_g), borderColor: COLORS.fat, backgroundColor: COLORS.fat, tension: 0.3 },
        { label: "Carbs", data: data.days.map((d) => d.carbs_g), borderColor: COLORS.carb, backgroundColor: COLORS.carb, tension: 0.3 },
      ],
    },
    options: chartOpts(),
  });

  // Weight section
  renderWeights(data.weights || []);

  // Meals table
  const meals = data.meals;
  if (!meals.length) {
    document.getElementById("meals-table").innerHTML = '<div class="empty">No meals logged yet.</div>';
  } else {
    const rows = meals.map((m) => {
      // Python isoformat() emits microseconds; trim to milliseconds for Date()
      const tsClean = m.ts.replace(/(\.\d{3})\d+/, "$1");
      const t = new Date(tsClean);
      const time = isNaN(t) ? m.ts : t.toLocaleString("en-US", { timeZone: "America/Los_Angeles", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
      return \`<tr>
        <td>\${time}</td>
        <td><span class="pill">\${m.name}</span></td>
        <td>\${m.description}</td>
        <td class="num">\${fmt(m.calories)}</td>
        <td class="num">\${fmt(m.protein_g)}g</td>
        <td class="num">\${fmt(m.fat_g)}g</td>
        <td class="num">\${fmt(m.carbs_g)}g</td>
      </tr>\`;
    }).join("");
    document.getElementById("meals-table").innerHTML = \`
      <table>
        <thead><tr><th>When (PST)</th><th>Meal</th><th>Description</th><th class="num">kcal</th><th class="num">P</th><th class="num">F</th><th class="num">C</th></tr></thead>
        <tbody>\${rows}</tbody>
      </table>\`;
  }
}

function renderWeights(weights) {
  const summary = document.getElementById("weight-summary");
  const tableEl = document.getElementById("weight-table");

  if (!weights.length) {
    summary.innerHTML = '<div class="empty">No weight entries yet.</div>';
    tableEl.innerHTML = "";
    if (weightChart) { weightChart.destroy(); weightChart = null; }
    return;
  }

  const latest = weights[weights.length - 1];
  const first = weights[0];
  const delta = latest.weight_lbs - first.weight_lbs;
  const deltaSign = delta > 0 ? "+" : "";
  const deltaColor = delta > 0 ? COLORS.fat : delta < 0 ? COLORS.pro : COLORS.dim;
  summary.innerHTML = \`
    <div style="display:flex; gap:24px; align-items:baseline; flex-wrap:wrap;">
      <div><span class="label">Latest </span><span class="value" style="font-size:18px">\${fmt(latest.weight_lbs, 1)} lbs</span> <span class="label">(\${latest.local_day})</span></div>
      <div><span class="label">Range Δ </span><span class="value" style="color:\${deltaColor}">\${deltaSign}\${fmt(delta, 1)} lbs</span> <span class="label">over \${weights.length} entries</span></div>
    </div>\`;

  const labels = weights.map((w) => w.local_day.slice(5));
  const vals = weights.map((w) => w.weight_lbs);
  const rollingAvg = (arr, k) => arr.map((_, i) => {
    const w = arr.slice(Math.max(0, i - k + 1), i + 1);
    return w.reduce((a, b) => a + b, 0) / w.length;
  });
  const avg3 = rollingAvg(vals, 3);
  const avg7 = rollingAvg(vals, 7);

  if (weightChart) weightChart.destroy();
  const opts = chartOpts();
  opts.scales.y.beginAtZero = false;
  opts.plugins.tooltip = {
    backgroundColor: "#181b22", borderColor: "#262a33", borderWidth: 1,
    mode: "index", intersect: false,
    callbacks: {
      label: (ctx) => \` \${ctx.dataset.label}: \${ctx.parsed.y.toFixed(1)} lbs\`,
    },
  };
  opts.interaction = { mode: "index", intersect: false };
  weightChart = new Chart(document.getElementById("weight-chart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Weight",
        data: vals,
        borderColor: COLORS.carb,
        backgroundColor: COLORS.carb,
        tension: 0.3,
        pointRadius: 4,
      }, {
        label: "3-day avg",
        data: avg3,
        borderColor: "rgba(90, 180, 255, 0.3)",
        backgroundColor: "transparent",
        borderDash: [4, 3],
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 1.5,
      }, {
        label: "7-day avg",
        data: avg7,
        borderColor: "#f5a623",
        backgroundColor: "transparent",
        borderDash: [6, 3],
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      }],
    },
    options: opts,
  });

  const rows = weights.slice().reverse().map((w) => \`
    <tr>
      <td>\${w.local_day}</td>
      <td class="num">\${fmt(w.weight_lbs, 1)}</td>
      <td>\${w.note || ""}</td>
    </tr>\`).join("");
  tableEl.innerHTML = \`
    <table>
      <thead><tr><th>Date</th><th class="num">Weight (lbs)</th><th>Note</th></tr></thead>
      <tbody>\${rows}</tbody>
    </table>\`;
}

function chartOpts(targetLine) {
  const opts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: COLORS.dim, font: { size: 11 } } },
      tooltip: { backgroundColor: "#181b22", borderColor: "#262a33", borderWidth: 1, mode: "index", intersect: false },
    },
    interaction: { mode: "index", intersect: false },
    scales: {
      x: { ticks: { color: COLORS.dim, font: { size: 11 } }, grid: { color: "#1f232c" } },
      y: { ticks: { color: COLORS.dim, font: { size: 11 } }, grid: { color: "#1f232c" }, beginAtZero: true },
    },
  };
  if (targetLine) {
    opts.plugins.annotation = {
      annotations: {
        target: {
          type: "line",
          yMin: targetLine,
          yMax: targetLine,
          borderColor: "rgba(255,255,255,0.35)",
          borderWidth: 1.5,
          borderDash: [6, 4],
          label: {
            display: true,
            content: \`Goal: \${targetLine} kcal\`,
            position: "start",
            color: COLORS.dim,
            font: { size: 11 },
            backgroundColor: "transparent",
          },
        },
      },
    };
  }
  return opts;
}

document.getElementById("range").addEventListener("change", load);
document.getElementById("refresh").addEventListener("click", load);
load();
setInterval(load, 30000);
</script>
</body>
</html>`;

console.log(`Nutrition dashboard on http://localhost:${port}`);
