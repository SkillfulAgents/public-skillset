---
name: mileage-math
description: 'How to look up and cite the current IRS standard mileage rate, which calendar trips count, how to compute round-trip and multi-stop distances, and how to lay out the monthly mileage report.'
---

# Mileage math

## 1. Get the rate, every run

Never hard-code a rate and never reuse last month's without checking.

1. Search: `mcp__web__web_search` with `IRS standard mileage rate <year>` and `includeDomains: ["irs.gov"]`.
2. Open the IRS news release or notice for that year (`mcp__web__web_fetch`). Read the **business** rate in cents per mile, and its effective date.
3. Check whether a mid-year change applies to any trip date in the month (it happened in 2022). Use the rate in effect on each trip's date.
4. Record the rate, the source URL, the notice number if given, and the date checked in `/workspace/state/time-and-mileage-log/irs-rate.json`. Put the same citation in the report footer.
5. If irs.gov can't be reached or the new year's rate isn't published yet (early January), say so, leave the dollar column blank, and report miles only. Don't guess.

Medical and charitable rates are different. Use them only if the user explicitly asks. If a client reimburses at a contract rate, show that rate in a separate column, labelled as the client's rate.

## 2. Which trips count

Include an event when all of these hold:
- the principal attended (not declined, not cancelled)
- it has a physical address, not a video link
- it is in the configured home state, or within the configured radius
- it is not a flight, train trip or a destination reached by flying (if the month has a flight to that city, skip local events there)
- it is not on the personal-exclusions list (gym, doctor, kids' school, unless the user marks them as business)

Airport runs: when an event or flight shows a trip to or from an airport, use the fixed round-trip miles from config. Don't map it.

Flag, don't guess: no location; a location that is only a business name with several branches ("Starbucks"); "their office", "TBD" or "client site"; an address that geocodes to a different state than expected; two events at the same time in different places.

Commuting: trips between home and a regular office are usually not business mileage for tax purposes. Config `start_point` says whether to measure from home or the office. When home is the start point and the user also has a regular office, add a short note that the user or their accountant should confirm the treatment. This is not tax advice.

## 3. Distance

- **Google Maps (preferred):** with the `google_maps` connected account, geocode each address, then request a driving route (Routes API `computeRoutes` or the Distance Matrix API) without traffic, for the fastest route. Convert to miles and round to 0.1.
- **Fallback:** a web lookup of the driving distance between the two addresses. Mark each such trip `method: web estimate`.
- Cache each pair (`from|to → miles, method, date`) in `/workspace/state/time-and-mileage-log/distance-cache.json` and reuse it for 180 days.
- **Multi-stop days:** if one day has several in-person stops, the default is the chained route (start → A → B → start) rather than separate round trips. Config `multi_stop: "chain" | "separate"`. Show each leg.

## 4. Report layout (Google Sheet, one tab per month)

| Date | Client / purpose | Destination | Legs | Miles | Rate | Amount | Method | Notes |
|---|---|---|---|---|---|---|---|---|

- Purpose comes from the event title and client. The IRS expects date, destination, business purpose and miles.
- Totals row at the bottom. The amount is total miles × the rate in effect on each date, rounded to the cent at the end, not per row.
- Separate sections below the table: "Skipped" (with the reason) and "Needs your input" (flagged trips).
- Footer: the rate used, the IRS source URL and the date checked, the distance method, and "Miles are estimates from calendar data; confirm before submitting."
- Parking and tolls are not covered by the per-mile rate. Leave an empty column for the user to add them if they want.
