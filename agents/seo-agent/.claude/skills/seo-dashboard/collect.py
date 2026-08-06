#!/usr/bin/env python3
"""Collect the SEO master dashboard snapshot: Ahrefs + GSC + program activity.

  uv run --env-file .env --with google-auth,requests \
    .claude/skills/seo-dashboard/collect.py [--refresh-ahrefs] [--refresh-gsc] [-o FILE]

Ahrefs is cached (default 6h TTL, ~1150 units per full pull); GSC is free and cached
15 min. Every Ahrefs pull appends a row to history.jsonl so long-run trends accumulate.
"""
import argparse, json, os, re, sys, time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

ROOT = Path("/workspace")
SEO = ROOT / "seo"
OUT_DIR = SEO / "dashboard"
CACHE = OUT_DIR / "cache"
HISTORY = OUT_DIR / "history.jsonl"
AHREFS_TTL = 6 * 3600
GSC_TTL = 15 * 60

# Per-site settings live in seo/config.json (written by the agent-onboarding skill).
CONFIG = json.loads((SEO / "config.json").read_text())
SITE = CONFIG["site"]  # e.g. "example.com"
GSC_PROPERTY = CONFIG["gsc_property"]  # e.g. "sc-domain:example.com"
if not SITE or not GSC_PROPERTY:
    sys.exit("seo/config.json is missing 'site' / 'gsc_property' — run agent-onboarding first")
# brand regex should include the misspellings people actually type
# (they must not count as non-brand)
BRAND_RE = re.compile(CONFIG.get("brand_regex") or re.escape(SITE.split(".")[0]), re.I)
# simple substring for GSC's notContains filter (regex not supported there)
BRAND_TERM = CONFIG.get("brand_filter_term") or SITE.split(".")[0]
TARGETS = CONFIG.get("targets") or {}

# ---------------------------------------------------------------- utilities


def log(msg):
    print(msg, file=sys.stderr)


def cached(name, ttl, fn, force=False):
    """File-cache a collector's output. Returns (payload, fetched_at, from_cache)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.json"
    if path.exists() and not force:
        blob = json.loads(path.read_text())
        age = time.time() - blob["fetched_at_ts"]
        if age < ttl:
            log(f"{name}: cache hit ({int(age)}s old)")
            return blob["data"], blob["fetched_at"], True
    log(f"{name}: fetching live")
    data = fn()
    now = datetime.now(timezone.utc)
    path.write_text(json.dumps(
        {"data": data, "fetched_at": now.isoformat(), "fetched_at_ts": now.timestamp()}))
    return data, now.isoformat(), False


def pct_delta(cur, prev):
    if not prev:
        return None
    return round((cur - prev) / prev * 100, 1)


def is_brand(q):
    return bool(BRAND_RE.search(q or ""))


def norm_url(u):
    return (u or "").rstrip("/")


def loose_num(s):
    """'~15.7k/wk' -> 15700.0, '12,674/wk' -> 12674.0, '—' -> None."""
    if s is None:
        return None
    m = re.search(r"(-?[\d,]*\.?\d+)\s*([km])?", str(s).replace("~", ""), re.I)
    if not m:
        return None
    n = float(m.group(1).replace(",", ""))
    return n * {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1)


# ---------------------------------------------------------------- Ahrefs

AH = "https://api.ahrefs.com/v3"


def ah_get(path, **params):
    key = os.environ["AHREFS_API_KEY"]
    r = requests.get(f"{AH}/{path}", headers={"Authorization": f"Bearer {key}"},
                     params=params, timeout=60)
    if r.status_code != 200:
        log(f"  ahrefs {path} -> {r.status_code}: {r.text[:200]}")
        return {}
    return r.json()


def collect_ahrefs():
    today = date.today().isoformat()
    dom = {"target": SITE, "mode": "subdomains"}
    usage = ah_get("subscription-info/limits-and-usage").get("limits_and_usage", {})

    dr = ah_get("site-explorer/domain-rating", target=SITE, date=today).get("domain_rating", {})
    bl = ah_get("site-explorer/backlinks-stats", date=today, **dom).get("metrics", {})
    met = ah_get("site-explorer/metrics", date=today, **dom).get("metrics", {})
    hist = ah_get("site-explorer/metrics-history", date_from="2026-01-01", **dom).get("metrics", [])
    refdoms = ah_get(
        "site-explorer/refdomains", date=today, limit=1000, order_by="first_seen:desc",
        select="domain,domain_rating,first_seen,last_seen,links_to_target,traffic_domain,dofollow_links",
        **dom).get("refdomains", [])
    kws = ah_get(
        "site-explorer/organic-keywords", date=today, limit=200, order_by="sum_traffic:desc",
        select="keyword,best_position,best_position_url,volume,keyword_difficulty,sum_traffic",
        **dom).get("keywords", [])
    pages = ah_get(
        "site-explorer/top-pages", date=today, limit=100, order_by="sum_traffic:desc",
        select="url,sum_traffic,keywords,top_keyword,top_keyword_best_position,top_keyword_volume",
        **dom).get("pages", [])

    # the API returns one row per locale, so the same keyword repeats with different
    # volume/position — roll up to one row per keyword+URL to match metrics.org_keywords
    rolled = {}
    for k in kws:
        key = (k.get("keyword"), k.get("best_position_url"))
        r = rolled.get(key)
        if not r:
            rolled[key] = dict(k, locales=1)
            continue
        r["locales"] += 1
        r["sum_traffic"] = (r.get("sum_traffic") or 0) + (k.get("sum_traffic") or 0)
        r["volume"] = max(r.get("volume") or 0, k.get("volume") or 0)
        if (k.get("best_position") or 999) < (r.get("best_position") or 999):
            r["best_position"] = k.get("best_position")
    kws = sorted(rolled.values(), key=lambda k: -(k.get("sum_traffic") or 0))
    log(f"  organic keywords: {len(kws)} unique (from {len(rolled)} rolled rows)")

    usage_after = ah_get("subscription-info/limits-and-usage").get("limits_and_usage", {})
    return {
        "date": today,
        "domain_rating": dr.get("domain_rating"),
        "ahrefs_rank": dr.get("ahrefs_rank"),
        "backlinks": bl,
        "metrics": met,
        "history": hist,
        "refdomains": refdoms,
        "organic_keywords": kws,
        "top_pages": pages,
        "units": {
            "used": usage_after.get("units_usage_workspace"),
            "limit": usage_after.get("units_limit_workspace"),
            "reset": usage_after.get("usage_reset_date"),
            # clamps to 0 across the monthly reset, when the counter runs backwards
            "spent_this_pull": max(0, (usage_after.get("units_usage_workspace") or 0)
                                   - (usage.get("units_usage_workspace") or 0)),
        },
    }


def append_history(ah):
    """One row per Ahrefs pull day — the long-run KPI series."""
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "date": ah["date"],
        "dr": ah.get("domain_rating"),
        "refdomains": (ah.get("backlinks") or {}).get("live_refdomains"),
        "backlinks": (ah.get("backlinks") or {}).get("live"),
        "org_keywords": (ah.get("metrics") or {}).get("org_keywords"),
        "org_traffic": (ah.get("metrics") or {}).get("org_traffic"),
        "org_keywords_1_3": (ah.get("metrics") or {}).get("org_keywords_1_3"),
    }
    rows = []
    if HISTORY.exists():
        rows = [json.loads(l) for l in HISTORY.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r["date"] != row["date"]] + [row]
    rows.sort(key=lambda r: r["date"])
    HISTORY.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return rows


# ---------------------------------------------------------------- GSC


def gsc_token():
    info = json.loads(os.environ["GSC_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    creds.refresh(Request())
    return creds.token


def gsc_query(token, start, end, dimensions, limit=1000, filters=None):
    body = {"startDate": start, "endDate": end, "dimensions": dimensions, "rowLimit": limit}
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    url = (f"https://www.googleapis.com/webmasters/v3/sites/"
           f"{requests.utils.quote(GSC_PROPERTY, safe='')}/searchAnalytics/query")
    r = requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body, timeout=90)
    if r.status_code != 200:
        log(f"  gsc {dimensions} -> {r.status_code}: {r.text[:200]}")
        return []
    return r.json().get("rows", [])


def rows_to_dicts(rows, keys):
    out = []
    for r in rows:
        d = dict(zip(keys, r["keys"]))
        d.update(clicks=r["clicks"], impressions=r["impressions"],
                 ctr=round(r["ctr"] * 100, 2), position=round(r["position"], 1))
        out.append(d)
    return out


def collect_gsc():
    token = gsc_token()
    # GSC lags ~2 days.
    end = date.today() - timedelta(days=2)
    d = lambda x: x.isoformat()

    daily = rows_to_dicts(gsc_query(token, d(end - timedelta(days=119)), d(end), ["date"]), ["date"])
    daily_nb = rows_to_dicts(
        gsc_query(token, d(end - timedelta(days=119)), d(end), ["date"],
                  filters=[{"dimension": "query", "operator": "notContains", "expression": BRAND_TERM}]),
        ["date"])

    cur_s, cur_e = d(end - timedelta(days=27)), d(end)
    pre_s, pre_e = d(end - timedelta(days=55)), d(end - timedelta(days=28))
    wk_s, wk_e = d(end - timedelta(days=6)), d(end)
    pwk_s, pwk_e = d(end - timedelta(days=13)), d(end - timedelta(days=7))

    def paired(dim, key):
        cur = rows_to_dicts(gsc_query(token, cur_s, cur_e, [dim], 500), [key])
        pre = {r[key]: r for r in rows_to_dicts(gsc_query(token, pre_s, pre_e, [dim], 500), [key])}
        for r in cur:
            p = pre.get(r[key])
            r["prev_clicks"] = p["clicks"] if p else 0
            r["prev_impressions"] = p["impressions"] if p else 0
            r["prev_position"] = p["position"] if p else None
            r["d_clicks"] = r["clicks"] - r["prev_clicks"]
            r["d_impressions"] = r["impressions"] - r["prev_impressions"]
            r["d_position"] = (round(r["prev_position"] - r["position"], 1)
                              if p else None)  # positive = improved
            r["is_new"] = p is None
        return cur

    queries = paired("query", "query")
    for q in queries:
        q["brand"] = is_brand(q["query"])
    pages = paired("page", "page")
    for p in pages:
        p["page_key"] = norm_url(p["page"])  # join key: page_queries uses the same form

    # top queries per page — powers the per-article drilldown
    pq = {}
    for r in gsc_query(token, cur_s, cur_e, ["page", "query"], 25000):
        page, query = r["keys"]
        pq.setdefault(norm_url(page), []).append({
            "query": query, "clicks": r["clicks"], "impressions": r["impressions"],
            "position": round(r["position"], 1), "brand": is_brand(query)})
    for k in pq:
        pq[k] = sorted(pq[k], key=lambda x: -x["impressions"])[:10]

    def totals(s, e, nb=False):
        f = [{"dimension": "query", "operator": "notContains", "expression": BRAND_TERM}] if nb else None
        rows = gsc_query(token, s, e, ["date"], 500, f)
        c = sum(r["clicks"] for r in rows)
        i = sum(r["impressions"] for r in rows)
        pos = (sum(r["position"] * r["impressions"] for r in rows) / i) if i else 0
        return {"clicks": c, "impressions": i, "ctr": round(c / i * 100, 2) if i else 0,
                "position": round(pos, 1)}

    period = {
        "week": {"cur": totals(wk_s, wk_e), "prev": totals(pwk_s, pwk_e),
                 "cur_nb": totals(wk_s, wk_e, True), "prev_nb": totals(pwk_s, pwk_e, True)},
        "month": {"cur": totals(cur_s, cur_e), "prev": totals(pre_s, pre_e),
                  "cur_nb": totals(cur_s, cur_e, True), "prev_nb": totals(pre_s, pre_e, True)},
    }
    queries.sort(key=lambda q: -q["impressions"])
    pages.sort(key=lambda p: -p["impressions"])
    return {"data_through": d(end), "daily": daily, "daily_nonbrand": daily_nb,
            "queries": queries[:250], "pages": pages[:250], "page_queries": pq,
            "periods": period,
            "ranges": {"cur": [cur_s, cur_e], "prev": [pre_s, pre_e],
                       "week": [wk_s, wk_e], "prev_week": [pwk_s, pwk_e]}}


# ---------------------------------------------------------------- program activity

RUN_TYPES = {
    "daily content": "content",
    "daily links": "links",
    "weekly": "weekly",
    "setup": "setup",
    "p0 execution": "technical",
}


def parse_log():
    """log.md -> dated run entries with type, bullets, published URLs, send counts."""
    text = (SEO / "log.md").read_text()
    entries = []
    for m in re.finditer(r"^## (\d{4}-\d{2}-\d{2})(?: \(([^)]*)\))?\s*$(.*?)(?=^## |\Z)",
                         text, re.M | re.S):
        day, label, body = m.group(1), (m.group(2) or "").lower(), m.group(3)
        kind = next((v for k, v in RUN_TYPES.items() if k in label), "other")
        bullets = [re.sub(r"\s+", " ", b).strip()
                   for b in re.findall(r"^- (.+?)(?=\n- |\n## |\Z)", body, re.M | re.S)]
        urls = re.findall(re.escape(CONFIG.get("blog_url_prefix") or f"https://{SITE}/blog/")
                          + r"[\w\-/]+", body)
        published = sorted(set(urls)) if "[article]" in body and "PUBLISHED" in body else []
        title = None
        tm = re.search(r'\[article\]\s*"([^"]+)"', body)
        if tm:
            title = tm.group(1)
        sends = re.search(r"\*\*Follow-ups sent\*\*\s*\((\d+)\)", body)
        new_sends = re.search(r"\*\*Outreach(?:\s*\([^)]*\))?(?:\s*—\s*new sends)?\*\*\s*\((\d+) sends?", body)
        entries.append({
            "date": day, "label": label or kind, "type": kind,
            "summary": bullets[0][:400] if bullets else "",
            "bullets": bullets, "published": published, "article_title": title,
            "followups_sent": int(sends.group(1)) if sends else 0,
            "new_sends": int(new_sends.group(1)) if new_sends else 0,
        })
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def parse_backlogs():
    def parse(path):
        items = []
        section = None
        for line in path.read_text().splitlines():
            if line.startswith("## "):
                section = line[3:].strip()
            m = re.match(r"^- \[(\w+)\] \[(\w+)(?: (\d{4}-\d{2}-\d{2}))?\] (.+)$", line)
            if m:
                typ, status, dt, rest = m.groups()
                url = None
                um = re.search(r"(https?://\S+)$", rest)
                if um:
                    url = um.group(1)
                title = rest.split(" — ")[0].strip()
                kw = None
                km = re.search(r'"([^"]+)"\s*\((\d[\d,]*)/KD\s*(\d+)', rest)
                items.append({"type": typ, "status": status, "date": dt, "title": title,
                              "section": section, "url": url,
                              "primary_kw": km.group(1) if km else None,
                              "volume": int(km.group(2).replace(",", "")) if km else None,
                              "kd": int(km.group(3)) if km else None})
        return items

    content = parse(SEO / "content-backlog.md")
    links_txt = (SEO / "link-backlog.md").read_text()
    link_items = []
    section = None
    for line in links_txt.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"^- \[([ x])\] (.+)$", line)
        if m:
            link_items.append({"done": m.group(1) == "x", "section": section,
                               "title": m.group(2)[:220],
                               "needs_owner": "needs owner" in m.group(2).lower()
                                              or "PAID" in m.group(2)})
    return {
        "content": content,
        "content_counts": {
            "article_todo": sum(1 for i in content if i["type"] == "article" and i["status"] == "todo"),
            "article_done": sum(1 for i in content if i["type"] == "article" and i["status"] == "done"),
            "article_later": sum(1 for i in content if i["type"] == "article" and i["status"] == "later"),
            "surface_todo": sum(1 for i in content if i["type"] != "article" and i["status"] == "todo"),
            "surface_done": sum(1 for i in content if i["type"] != "article" and i["status"] == "done"),
            "surface_later": sum(1 for i in content if i["type"] != "article" and i["status"] == "later"),
        },
        "links": link_items,
        "link_counts": {
            "open": sum(1 for i in link_items if not i["done"]),
            "done": sum(1 for i in link_items if i["done"]),
            "needs_owner": sum(1 for i in link_items if i["needs_owner"] and not i["done"]),
        },
    }


def parse_crm():
    crm = json.loads((SEO / "outreach" / "crm.json").read_text())
    cfg, prospects = crm.get("config", {}), crm.get("prospects", [])
    followup_days = cfg.get("followup_days", [4, 8])
    max_touches = cfg.get("max_touches", 3)
    today = date.today()

    by_status, due, active, won, timeline = {}, [], [], [], {}
    for p in prospects:
        st = p.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        touches = p.get("touches", [])
        for t in touches:
            timeline[t["date"]] = timeline.get(t["date"], 0) + 1
        if st in ("sent", "followed_up") and touches:
            first = datetime.fromisoformat(touches[0]["date"]).date()
            n = len(touches)
            if n < max_touches and n - 1 < len(followup_days):
                nxt = first + timedelta(days=followup_days[n - 1])
                due.append({"domain": p["domain"], "dr": p.get("domain_rating"),
                            "touch": f"followup_{n}", "due": nxt.isoformat(),
                            "overdue": nxt <= today, "contact": p.get("contact_name")})
        if st in ("replied", "negotiating", "in_progress"):
            active.append({"domain": p["domain"], "dr": p.get("domain_rating"),
                           "status": st, "note": (p.get("pitch_angle") or "")[:200],
                           "contact": p.get("contact_name")})
        if st in ("won", "link_live"):
            won.append({"domain": p["domain"], "dr": p.get("domain_rating"),
                        "url": p.get("url_live") or p.get("url_from")})
    due.sort(key=lambda x: x["due"])
    total = len(prospects)
    replied = sum(v for k, v in by_status.items() if k.startswith("replied")
                  or k in ("negotiating", "won", "link_live", "closed_paid"))
    return {
        "config": {k: cfg.get(k) for k in ("inbox", "daily_limit", "followup_days",
                                           "max_touches", "first_send_date")},
        "total": total,
        "by_status": by_status,
        "funnel": {
            "prospected": total,
            "delivered": total - by_status.get("bounced", 0),
            "replied": replied,
            "won": len(won),
        },
        "bounced": by_status.get("bounced", 0),
        "response_rate": round(replied / total * 100, 1) if total else 0,
        "bounce_rate": round(by_status.get("bounced", 0) / total * 100, 1) if total else 0,
        "followups_due": due,
        "active": active,
        "won": won,
        "send_timeline": [{"date": k, "touches": v} for k, v in sorted(timeline.items())],
    }


def parse_state_kpis():
    text = (SEO / "STATE.md").read_text()
    m = re.search(r"## KPI history\s*\n(\|.*?)(?=\n##|\Z)", text, re.S)
    if not m:
        return []
    lines = [l for l in m.group(1).strip().splitlines() if l.startswith("|")]
    if len(lines) < 3:
        return []
    hdr = [c.strip() for c in lines[0].strip("|").split("|")]
    out = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        row = dict(zip(hdr, cells))
        # display strings like "~15.7k/wk" are unusable for charting — emit numbers too
        row["_num"] = {k: loose_num(v) for k, v in row.items() if k != "Notes"}
        out.append(row)
    return out


# ---------------------------------------------------------------- joins


def published_posts():
    """Published blog posts, for per-article performance.

    CMS-agnostic: reads seo/content-inventory.json — a list of
    {"title", "url", "published_at"} rows that the daily content skill appends to
    on every publish (whatever the CMS). Missing file = no articles section yet.
    """
    path = SEO / "content-inventory.json"
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception as e:
        log(f"content-inventory: {e}")
        return []


def build_articles(posts, gsc, ahrefs, backlog):
    """Join each published post to GSC 28d performance + Ahrefs best rank."""
    pages = {}
    for p in gsc.get("pages", []):
        pages[p["page"].rstrip("/")] = p
    kw_by_url = {}
    for k in ahrefs.get("organic_keywords", []):
        kw_by_url.setdefault((k.get("best_position_url") or "").rstrip("/"), []).append(k)
    bl_by_slug = {}
    for i in backlog["content"]:
        if i.get("url"):
            bl_by_slug[i["url"].rstrip("/").rsplit("/", 1)[-1]] = i

    out = []
    for post in posts:
        url = norm_url(post.get("url"))
        if not url:
            continue
        slug = url.rsplit("/", 1)[-1]
        g = (pages.get(url) or pages.get(url.replace("://www.", "://"))
             or pages.get(url.replace("://", "://www.")))
        b = bl_by_slug.get(slug, {})
        ranks = sorted(kw_by_url.get(url, []), key=lambda k: k.get("best_position") or 999)
        top_qs = gsc.get("page_queries", {}).get(url, [])
        nb_qs = [q for q in top_qs if not q["brand"]]
        pub = (post.get("published_at") or post.get("publishedAt") or "")[:10]
        age = None
        if pub:
            try:
                age = (date.today() - date.fromisoformat(pub)).days
            except ValueError:
                pass
        out.append({
            "title": post.get("title"), "slug": slug, "url": url,
            "published_at": pub, "age_days": age,
            "primary_kw": b.get("primary_kw"), "volume": b.get("volume"), "kd": b.get("kd"),
            "clicks": g["clicks"] if g else 0,
            "impressions": g["impressions"] if g else 0,
            "ctr": g["ctr"] if g else 0,
            "position": g["position"] if g else None,
            "d_clicks": g["d_clicks"] if g else 0,
            "d_impressions": g["d_impressions"] if g else 0,
            "ranking_keywords": len(ranks),
            "best_rank": ranks[0]["best_position"] if ranks else None,
            "best_rank_kw": ranks[0]["keyword"] if ranks else None,
            "top_query": nb_qs[0]["query"] if nb_qs else None,
            "top_query_position": nb_qs[0]["position"] if nb_qs else None,
            "queries": top_qs,
        })
    out.sort(key=lambda a: (-a["impressions"], -a["clicks"]))
    return out


def build_refdomains(refdoms):
    today = date.today()
    def days(ts):
        if not ts:
            return None
        return (today - datetime.fromisoformat(ts.replace("Z", "+00:00")).date()).days
    rows = []
    for r in refdoms:
        age = days(r.get("first_seen"))
        rows.append({
            "domain": r.get("domain"), "dr": r.get("domain_rating"),
            "first_seen": (r.get("first_seen") or "")[:10],
            "lost": bool(r.get("last_seen")),
            "last_seen": (r.get("last_seen") or "")[:10] or None,
            "links": r.get("links_to_target"), "dofollow": r.get("dofollow_links"),
            "traffic": r.get("traffic_domain"), "age_days": age,
            # heuristic: spammy TLD or zero-traffic low-DR = likely link-farm noise
            "suspect": bool(
                re.search(r"\.(shop|xyz|top|icu|club|online|site|space|buzz|link|store)$",
                          r.get("domain") or "")
                or ((r.get("traffic_domain") or 0) < 10 and (r.get("domain_rating") or 0) < 15)),
        })
    new30 = [r for r in rows if r["age_days"] is not None and r["age_days"] <= 30 and not r["lost"]]
    live = [r for r in rows if not r["lost"]]
    return {
        "all": rows,
        "new_30d": new30,
        "new_30d_count": len(new30),
        "new_30d_suspect": sum(1 for r in new30 if r["suspect"]),
        "clean_count": sum(1 for r in live if not r["suspect"]),
        "suspect_count": sum(1 for r in live if r["suspect"]),
        "lost": [r for r in rows if r["lost"]][:50],
        "dr_buckets": {
            "0-19": sum(1 for r in rows if (r["dr"] or 0) < 20),
            "20-39": sum(1 for r in rows if 20 <= (r["dr"] or 0) < 40),
            "40-59": sum(1 for r in rows if 40 <= (r["dr"] or 0) < 60),
            "60+": sum(1 for r in rows if (r["dr"] or 0) >= 60),
        },
    }


def build_kpis(gsc, ahrefs, refd, crm):
    w = gsc["periods"]["week"]
    m = gsc["periods"]["month"]
    bl = ahrefs.get("backlinks") or {}
    met = ahrefs.get("metrics") or {}

    def kpi(label, cur, prev, unit="", good_up=True, hint=""):
        return {"label": label, "value": cur, "prev": prev,
                "delta": None if prev is None else round(cur - prev, 1),
                "delta_pct": pct_delta(cur, prev) if prev is not None else None,
                "unit": unit, "good_up": good_up, "hint": hint}

    return [
        kpi("Non-brand clicks", w["cur_nb"]["clicks"], w["prev_nb"]["clicks"],
            "/wk", True, "The north-star metric — organic clicks excluding brand queries."),
        kpi("Non-brand impressions", w["cur_nb"]["impressions"], w["prev_nb"]["impressions"], "/wk"),
        kpi("Total clicks", w["cur"]["clicks"], w["prev"]["clicks"], "/wk"),
        kpi("Total impressions", w["cur"]["impressions"], w["prev"]["impressions"], "/wk"),
        kpi("Avg position", w["cur"]["position"], w["prev"]["position"], "", False,
            "Impression-weighted average across all queries."),
        kpi("Domain Rating", ahrefs.get("domain_rating"), None, "", True, "Ahrefs DR"),
        kpi("Referring domains", bl.get("live_refdomains"), None, "", True,
            f"{refd['new_30d_count']} new in 30d ({refd['new_30d_suspect']} look like spam)"),
        kpi("Ranking keywords", met.get("org_keywords"), None, "", True,
            f"{met.get('org_keywords_1_3', 0)} in top 3"),
        kpi("Outreach replies", crm["funnel"]["replied"], None, "", True,
            f"{crm['response_rate']}% of {crm['total']} prospects"),
    ]


def build_targets(ahrefs, gsc, refd):
    """Progress vs the goals agreed at onboarding (config.targets)."""
    bl = ahrefs.get("backlinks") or {}
    met = ahrefs.get("metrics") or {}
    nb_month = gsc["periods"]["month"]["cur_nb"]["clicks"]
    def t(label, cur, target, note=""):
        cur = cur or 0
        return {"label": label, "current": cur, "target": target,
                "pct": min(100, round(cur / target * 100, 1)) if target else 0, "note": note}
    out = []
    if TARGETS.get("refdomains"):
        out.append(t("Referring domains", bl.get("live_refdomains"),
                     TARGETS["refdomains"], "12-mo target"))
        out.append(t("Quality refdomains", refd["clean_count"], TARGETS["refdomains"],
                     f"excludes {refd['suspect_count']} spam-signature domains"))
    if TARGETS.get("nonbrand_clicks_month"):
        out.append(t("Non-brand clicks / mo", nb_month,
                     TARGETS["nonbrand_clicks_month"], "12-mo target"))
    if TARGETS.get("top3_rankings"):
        out.append(t("Top-3 keyword rankings", met.get("org_keywords_1_3"),
                     TARGETS["top3_rankings"], "12-mo target"))
    return out


def build_velocity(activity, crm):
    """Weekly shipping cadence: articles, link sessions, outreach touches."""
    weeks = {}
    for e in activity:
        d = date.fromisoformat(e["date"])
        wk = (d - timedelta(days=d.weekday())).isoformat()
        w = weeks.setdefault(wk, {"week": wk, "articles": 0, "content_runs": 0,
                                  "link_runs": 0, "touches": 0, "other": 0})
        if e["type"] == "content":
            w["content_runs"] += 1
            w["articles"] += len(e["published"])
        elif e["type"] == "links":
            w["link_runs"] += 1
            w["touches"] += e["followups_sent"] + e["new_sends"]
        else:
            w["other"] += 1
    # CRM touches are structured data — authoritative over log parsing
    for k in weeks:
        weeks[k]["touches"] = 0
    for t in crm["send_timeline"]:
        d = date.fromisoformat(t["date"])
        wk = (d - timedelta(days=d.weekday())).isoformat()
        w = weeks.setdefault(wk, {"week": wk, "articles": 0, "content_runs": 0,
                                  "link_runs": 0, "touches": 0, "other": 0})
        w["touches"] += t["touches"]
    return [weeks[k] for k in sorted(weeks)]


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-ahrefs", action="store_true", help="ignore the 6h Ahrefs cache")
    ap.add_argument("--refresh-gsc", action="store_true", help="ignore the 15m GSC cache")
    ap.add_argument("--refresh", action="store_true", help="refresh everything")
    ap.add_argument("-o", "--out", default=str(OUT_DIR / "data.json"))
    args = ap.parse_args()

    ahrefs, ah_at, ah_cached = cached("ahrefs", AHREFS_TTL, collect_ahrefs,
                                     args.refresh_ahrefs or args.refresh)
    gsc, gsc_at, gsc_cached = cached("gsc", GSC_TTL, collect_gsc,
                                    args.refresh_gsc or args.refresh)
    if not ah_cached:
        append_history(ahrefs)
    history = ([json.loads(l) for l in HISTORY.read_text().splitlines() if l.strip()]
               if HISTORY.exists() else [])

    backlog = parse_backlogs()
    crm = parse_crm()
    activity = parse_log()
    refd = build_refdomains(ahrefs.get("refdomains", []))
    articles = build_articles(published_posts(), gsc, ahrefs, backlog)

    data = {
        "site": SITE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ahrefs_fetched_at": ah_at, "ahrefs_cached": ah_cached,
        "gsc_fetched_at": gsc_at, "gsc_cached": gsc_cached,
        "gsc_data_through": gsc["data_through"],
        "units": ahrefs.get("units", {}),
        "kpis": build_kpis(gsc, ahrefs, refd, crm),
        "targets": build_targets(ahrefs, gsc, refd),
        "gsc": gsc,
        "ahrefs": {k: ahrefs.get(k) for k in
                   ("domain_rating", "ahrefs_rank", "backlinks", "metrics", "history",
                    "organic_keywords", "top_pages", "date")},
        "refdomains": refd,
        "kpi_history": history,
        "kpi_history_state": parse_state_kpis(),
        "articles": articles,
        "backlog": backlog,
        "outreach": crm,
        "activity": activity,
        "velocity": build_velocity(activity, crm),
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(data, indent=1))
    log(f"wrote {args.out} ({Path(args.out).stat().st_size // 1024} KB) "
        f"| ahrefs {'cache' if ah_cached else 'live'} | gsc {'cache' if gsc_cached else 'live'}")
    print(args.out)


if __name__ == "__main__":
    main()
