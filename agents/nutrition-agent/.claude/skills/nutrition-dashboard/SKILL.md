---
name: Nutrition Dashboard
description: Open or start the nutrition history dashboard — a web view showing day-by-day calories, macros, and meal history. Use when the user asks for "dashboard", "history", "see my week", "show my trend", "stats over time".
---

# Nutrition Dashboard

Starts (or restarts) the `nutrition-dashboard` dashboard and returns the URL.

## How to use

1. Run via the dashboards tool:
   - `mcp__dashboards__start_dashboard` with slug `nutrition-dashboard`.
2. Share the URL with the user in a short sentence.

The dashboard reads `/workspace/nutrition/data/nutrition.db` directly each request, so it's always fresh.
