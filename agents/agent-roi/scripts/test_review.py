"""Run: python3 -m unittest scripts/test_review.py"""
import datetime, json, os, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cost, ledger, review_math, usage_page  # noqa: E402

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
AUG = {"start": "2026-08-01T00:00:00+00:00", "end": "2026-09-01T00:00:00+00:00"}

T = lambda i, n, k, **kw: {"id": i, "name": n, "counts_when": "c", "receipt": "link", "value_kind": k, "price_reason": "r",
                            "price_anchor": "estimate", "counts_on": "delivery", **kw}
CARD = lambda a, types: {"agent_id": a, "agent_name": a.upper(), "purpose": "p", "confirmed_at": "2026-08-01",
                         "confirmed_by": "admin", "outcome_types": types}


class Review(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        ledger.REVIEW = self.dir
        self.write("cards.json", {"cost_of_an_hour_usd": 60, "agents": [
            CARD("a", [T("t1", "Report", "time_saved", hours=1, hours_low=0.5),
                       T("t2", "Meeting", "money_made", price_usd=200, price_anchor="owner")]),
            CARD("c", [T("t3", "Fix", "time_saved", hours=1, rate_usd=None)]), CARD("d", [])]})
        self.write("coverage.json", {"agents": [{"agent_id": x, "readable": True, "in_scope": True} for x in "acd"]})
        self.cost(AUG)

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(data, open(path, "w"))

    def cost(self, window):
        self.write("costs/last30.json", {"period": "last30", "read_at": "2026-09-01T00:00:00Z", "window": window, "agents": {
            "a": {"ai_usd": 100, "tools_usd": 20, "sessions": {"s1": 30, "s2": 40, "s3": 50}},
            "b": {"name": "B", "ai_usd": 50, "tools_usd": 0}}, "unattributed": {"ai_usd": 0, "tools_usd": 5}})

    def view(self, **kw):
        return review_math.load_view(self.dir, "last30", **kw)

    def agent(self, x="a", **kw):
        return next(a for a in self.view(**kw)["numbers"]["agents"] if a["agent_id"] == x)

    def run_(self, *args, period="2026-08"):
        return ledger.main([args[0], "--period", period, *args[1:]])

    def add(self, receipt, type_="t1", period="2026-08", agent="a"):
        return self.run_("add", "--agent", agent, "--type", type_, "--session", "s1", "--delivered-at", f"{period}-03",
                         "--receipt", receipt, "--quote", "q", "--status", "verified", period=period)

    def scan(self, session, kind, n, period="2026-08"):
        gaps = []
        for i in range(n):
            gaps += [["agent", f"{period}-03T1{i}:00:00Z"], ["person", f"{period}-03T1{i}:10:00Z"]]
        return self.run_("scan", "--agent", "a", "--session", session, "--started-at", f"{period}-03", "--kind", kind,
                         "--reason", "r", "--messages", json.dumps(gaps), period=period)

    def month(self, period="2026-08"):
        for r, t in (("r1", "t1"), ("r2", "t1"), ("r3", "t2")):
            self.add(r if period == "2026-08" else f"{r}-{period}", t, period)
        self.scan("s1", "work", 3, period)
        self.scan("s2", "work", 0, period)
        self.scan("s3", "setup", 6, period)
        self.run_("listed", "--agent", "a", "--count", "3", "--unread", "0", period=period)
        for x in "cd":
            self.run_("listed", "--agent", x, "--count", "0", "--unread", "0", period=period)

    def test_view_counts_only_its_window_and_needs_every_month_listed(self):
        self.month("2026-08")
        self.month("2026-09")
        self.cost({"start": "2026-08-25T00:00:00+00:00", "end": "2026-09-24T00:00:00+00:00"})
        v = self.view()
        a = v["numbers"]["agents"][0]
        self.assertEqual((a["outcomes"], a["flags"]), (3, []))
        self.assertTrue(all(o["receipt"].endswith("-2026-09") for o in v["outcomes"]))
        self.cost({"start": "2026-07-25T00:00:00+00:00", "end": "2026-08-24T00:00:00+00:00"})
        self.assertIn("partial_count", self.agent()["flags"])

    def test_cost_is_spend_unless_the_view_adds_peoples_time(self):
        self.month()
        spend_only = self.agent()["cost"]
        self.assertEqual((spend_only["total"], spend_only["people"]), (120, 90))
        self.assertFalse(self.view()["numbers"]["leadership"]["people_in_cost"])
        with_people = self.view(people_in_cost=True)
        self.assertEqual(with_people["numbers"]["agents"][0]["cost"]["total"], 210)
        self.assertTrue(with_people["numbers"]["leadership"]["people_in_cost"])

    def test_hand_computed_range(self):
        self.month()
        a = self.agent(people_in_cost=True)
        self.assertEqual(a["value"], {"time_saved": 120, "money_saved": 0, "money_made": 200})
        self.assertEqual(a["cost"], {"ai": 100, "tools": 20, "people": 90, "total": 210})
        self.assertEqual((a["setup_cost"], a["work_cost"], a["roi"], a["flags"]), (110, 100, 0.52, []))

    def test_receipt_counts_once_across_months(self):
        self.add("r1")
        self.assertEqual(self.add("r1/", period="2026-09"), 3)
        self.run_("reject", "--receipt", "r1", "--by", "admin", "--reason", "x")
        self.assertEqual(self.add("r1", period="2026-09"), 3)

    def test_person_decisions_survive_rescan_and_clear(self):
        self.month()
        self.run_("set-kind", "--agent", "a", "--session", "s1", "--kind", "setup", "--by", "admin", "--reason", "x")
        self.run_("accept", "--receipt", "r3", "--by", "admin", "--reason", "x")
        self.run_("clear", "--agent", "a", "--by", "admin", "--reason", "card changed")
        self.month()
        st = ledger.state(ledger.events("2026-08"))
        self.assertEqual((st["scans"][("a", "s1")]["kind"], st["outcomes"]["r3"]["status"]), ("setup", "verified"))

    def test_missing_inputs_are_unknown_not_zero(self):
        self.month()
        v = self.view()
        c, d = v["numbers"]["agents"][1:]
        self.assertEqual(c["cost"]["total"], None)
        self.assertEqual((d["flags"], d["net_value"]), (["inactive"], None))
        self.assertEqual(v["numbers"]["leadership"]["inactive"], ["C", "D"])
        self.assertEqual(v["numbers"]["leadership"]["total_cost"], 120)

    def test_idle_comes_from_nothing_delivered_in_the_range(self):
        cards = json.load(open(os.path.join(self.dir, "cards.json")))
        cards["agents"].append(CARD("e", [T("t4", "Post", "money_saved", price_usd=10)]))
        self.write("cards.json", cards)
        self.write("coverage.json", {"agents": [{"agent_id": x, "readable": True, "in_scope": True} for x in "acde"]})
        self.month()
        self.run_("listed", "--agent", "e", "--count", "30", "--unread", "30")
        self.assertFalse(self.agent("e")["idle"])  # listed, nothing read yet: not counted, not idle
        self.run_("scan", "--agent", "e", "--session", "e1", "--started-at", "2026-08-04", "--kind", "work",
                  "--reason", "r", "--person-messages", "0")
        e = self.agent("e")
        self.assertEqual((e["idle"], e["flags"]), (False, ["cost_unknown", "partial_count"]))  # partly read: incomplete, not idle
        self.add("e-post", "t4", agent="e")
        self.assertFalse(self.agent("e")["idle"])
        v = self.view()
        self.assertEqual((v["numbers"]["leadership"]["idle_agents"], v["numbers"]["leadership"]["trust"]["agents"]["idle"]),
                         (["C", "D"], 2))
        self.assertFalse(self.agent("a")["idle"])

    def test_split_unknown_unless_session_spend_is_complete(self):
        self.month()
        self.run_("listed", "--agent", "a", "--count", "4", "--unread", "1")
        a = self.agent()
        self.assertEqual((a["setup_cost"], a["flags"], a["net_value"]), (None, ["partial_count"], None))

    def test_low_end_verification_and_scope(self):
        self.month()
        self.run_("verify", "--receipt", "r3", "--how", "opened the calendar invite")
        rows = [{"session": f"p{i}", "started_at": "2026-08-04"} for i in range(3)]
        json.dump(rows, open(os.path.join(self.dir, "routine.json"), "w"))
        self.run_("scan-routine", "--agent", "a", "--kind-name", "poll", "--sessions-file", os.path.join(self.dir, "routine.json"))
        v = self.view()
        L, a = v["numbers"]["leadership"], v["numbers"]["agents"][0]
        self.assertEqual((L["total_value"], L["total_value_low"], L["verified_value"]), (320, 260, 320))
        self.assertEqual((L["value_from_estimates_share"], L["drivers"][0]["outcome"]), (0.38, "Meeting"))
        self.assertEqual(a["sessions_read"], 6)
        self.assertEqual(L["not_reviewed_spend"], 0)
        self.run_("exclusion", "--label", "Bans with no id", "--amount", "53 · $5.3k", "--effect", "value_low")
        L = self.view()["numbers"]["leadership"]
        self.assertEqual((L["cash_low"], L["time_low"], L["receipts"], L["receipts_checked"]), (200, 60, 3, 3))
        self.assertEqual([p["price"] for p in L["prices"]], ["$200", "0.5–1 h × $60/h"])
        self.assertIn("Bans with no id", [x["label"] for x in L["left_out"]])

    def test_a_range_without_cost_shows_value(self):
        os.remove(os.path.join(self.dir, "costs", "last30.json"))
        real = review_math.window_bounds
        review_math.window_bounds = lambda *a: tuple(datetime.datetime.fromisoformat(AUG[k]) for k in ("start", "end"))
        try:
            self.month()
            v = self.view()
        finally:
            review_math.window_bounds = real
        L, a = v["numbers"]["leadership"], v["numbers"]["agents"][0]
        self.assertEqual((a["flags"], a["cost"]["total"], a["net_value"]), (["cost_unknown"], None, None))
        self.assertEqual((L["total_value"], L["total_value_low"], L["agents_counted"]), (320, 260, 0))
        self.assertEqual((L["total_cost"], L["net_value"], L["roi"], L["return_high"], L["cost_source"]),
                         (None, None, None, None, "unknown"))
        self.assertEqual((L["cost_parts"]["ai"], L["workspace_spend"]), (None, None))
        self.assertIn("Cost: this range hasn't been read from the usage page yet", [x["label"] for x in L["left_out"]])

    def test_a_sample_counts_in_worth_but_not_in_cost(self):
        self.add("r1")
        self.run_("listed", "--agent", "a", "--count", "40", "--unread", "39")
        L = self.view()["numbers"]["leadership"]
        self.assertEqual((L["total_value"], L["counted_value"], L["total_cost"]), (60, 0, None))

    def test_singular_unit_when_one_was_delivered(self):
        cards = json.load(open(os.path.join(self.dir, "cards.json")))
        cards["agents"][0]["outcome_types"][0].update(unit="reports", unit_one="report")
        cards["agents"][0]["outcome_types"][1].update(unit="meetings")
        self.write("cards.json", cards)
        self.add("r1")
        self.add("r3", "t2")
        delivered = lambda: {d["unit"]: d["count"] for d in self.agent()["delivered"]}
        self.assertEqual(delivered(), {"report": 1, "meetings": 1})
        self.add("r2")
        self.assertEqual(delivered(), {"reports": 2, "meetings": 1})

    def test_null_type_rate_falls_back_to_workspace_rate(self):
        self.assertEqual(review_math.outcome_value({"value_kind": "time_saved", "hours": 2, "rate_usd": None}, 60), 120)


class PageSource(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        ledger.REVIEW = cost.REVIEW = usage_page.REVIEW = self.dir
        os.environ["REVIEW_DIR"] = self.dir
        self.write("cards.json", {"timezone": "America/Los_Angeles", "agents": []})
        self.write("coverage.json", {"agents": [{"agent_id": "sales-1a2b", "name": "Sales", "in_scope": True},
                                                {"agent_id": "ops-3c4d", "name": "Ops", "in_scope": True}]})
        self.write("cost-source.json", {"type": "command", "name": "Usage page",
                                        "command": f"{sys.executable} {SCRIPTS}/usage_page.py cost"})

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(data, open(path, "w"))

    def reading(self, read_at, kind="30d", **kw):
        return {"kind": kind, "read_at": read_at, "tz": "America/Los_Angeles",
                "ranges": {k: kind for k in usage_page.RANGES},
                "agents": [{"agent_id": "sales-1a2b", "name": "Sales", "ai_usd": 10},
                           {"agent_id": "3c4d", "name": "Ops", "ai_usd": 5},
                           {"agent_id": "private-zzz9", "name": "Secret Project", "ai_usd": 7}],
                "out_of_scope": {"count": 200, "ai_usd": 100}, "ai_total_usd": 130, "tools_total_usd": 40, **kw}

    def cost_file(self, view="last30"):
        cost.main(["--period", view])
        return json.load(open(os.path.join(self.dir, "costs", f"{view}.json")))

    def test_a_reading_prices_its_view_and_private_agents_never_land(self):
        now = datetime.datetime.now(usage_page.review_tz()).isoformat(timespec="seconds")
        out = usage_page.save(self.reading(now))
        saved = open(out["path"]).read()
        self.assertNotIn("zzz9", saved)
        self.assertNotIn("Secret", saved)
        c = self.cost_file()
        self.assertEqual((c["period"], sorted(c["agents"])), ("last30", ["ops-3c4d", "sales-1a2b"]))
        self.assertTrue(c["source"].startswith("Usage page, last 30 days, read "))
        self.assertEqual(c["unattributed"], {"ai_usd": 8, "tools_usd": 40})
        self.assertIn("201 agents outside", " ".join(c["excludes"]))
        self.assertIn("window", c)
        usage_page.save(self.reading(now, kind="wtd"))
        start = datetime.datetime.fromisoformat(self.cost_file("wtd")["window"]["start"])
        self.assertEqual((start.weekday(), start.hour), (0, 0))
        with self.assertRaises(SystemExit) as e:
            self.cost_file("last7")
        self.assertIn("cost blocked", str(e.exception))

    def test_readings_that_dont_match_the_page_are_refused(self):
        now = datetime.datetime.now(usage_page.review_tz()).isoformat(timespec="seconds")
        for bad in (self.reading(now, kind="90d"), self.reading(now, tz="UTC"),
                    {**self.reading(now), "ranges": {"total_range": "30d", "llm_range": "mtd", "service_range": "30d"}}):
            with self.assertRaises(SystemExit):
                usage_page.save(bad)

    def test_range_windows_match_the_page(self):
        tz = usage_page.review_tz()
        read = datetime.datetime(2026, 11, 27, 10, 0, tzinfo=tz)
        got = {k: tuple(f"{d:%m-%d}" for d in usage_page.window_for(k, read, tz)) for k in usage_page.RANGE_KINDS}
        self.assertEqual(got, {"wtd": ("11-23", "11-28"), "mtd": ("11-01", "11-28"), "7d": ("11-21", "11-28"),
                               "14d": ("11-14", "11-28"), "30d": ("10-29", "11-28")})


if __name__ == "__main__":
    unittest.main()
