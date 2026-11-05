# Lever Jobs API: how to list every posting from any Lever job board (jobs.lever.co) as JSON

Lever publishes a **public postings API** for every company that hosts its jobs on `jobs.lever.co`. No key, no login. This guide documents the endpoint, the response fields, the `skip`/`limit` pagination and ships a dependency-free Python example.

## The endpoint

```
GET https://api.lever.co/v0/postings/{site}?mode=json
GET https://api.lever.co/v0/postings/{site}?mode=json&limit=100&skip=100
GET https://api.lever.co/v0/postings/{site}/{posting_id}?mode=json
GET https://api.lever.co/v0/postings/{site}?mode=json&team=Engineering&location=Remote&commitment=Full-time
```

`site` is the slug in the board URL: `https://jobs.lever.co/spotify` → `spotify`. Companies on the EU data center use `https://jobs.eu.lever.co/{site}` and `https://api.eu.lever.co/v0/postings/{site}`.

## What you get back

A JSON array (not an object). Each posting:

| Field | Example | Notes |
|---|---|---|
| `id` | `a1b2c3d4-...` | UUID, stable; diff between runs |
| `text` | `Senior Backend Engineer` | the title |
| `categories.team` | `Engineering` | |
| `categories.department` | `R&D` | optional |
| `categories.location` | `Stockholm` | |
| `categories.allLocations[]` | `["Stockholm","Remote"]` | newer field, multi-location |
| `categories.commitment` | `Full-time` | |
| `workplaceType` | `remote` / `hybrid` / `onsite` | present on most boards in practice |
| `hostedUrl` | `https://jobs.lever.co/spotify/a1b2c3d4-...` | job page |
| `applyUrl` | `.../apply` | |
| `createdAt` | `1761040320000` | Unix epoch **milliseconds** |
| `descriptionPlain`, `description` | text / HTML | full description |
| `lists[]` | `[{"text":"Requirements","content":"<li>..."}]` | bullet sections |
| `salaryRange` | `{"min":..,"max":..,"currency":"USD","interval":"per-year-salary"}` | only where the company publishes it |

## Pagination and limits

Default page size is 100 (`limit` max 100); page with `skip`. Lever also returns the entire board with a large `limit` on most sites, but relying on `skip` is the documented way. There is no published rate limit; keep it to a few requests per second and cache.

## Python example (stdlib only)

```python
import json, urllib.request

def lever_jobs(site):
    skip = 0
    while True:
        url = f"https://api.lever.co/v0/postings/{site}?mode=json&limit=100&skip={skip}"
        req = urllib.request.Request(url, headers={"User-Agent": "your-app/1.0 (contact@example.com)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            page = json.load(r)
        if not page:
            return
        for p in page:
            c = p.get("categories") or {}
            yield {"id": p["id"], "title": p["text"], "team": c.get("team"), "location": c.get("location"),
                   "commitment": c.get("commitment"), "workplace": p.get("workplaceType"),
                   "url": p["hostedUrl"], "posted_at": p.get("createdAt")}
        skip += len(page)

if __name__ == "__main__":
    rows = list(lever_jobs("spotify")); print(len(rows), "jobs"); print(rows[0])
```

## Finding Lever boards

Search `site:jobs.lever.co` or `site:jobs.eu.lever.co`. A careers page that links to `jobs.lever.co/<slug>/<uuid>` tells you the slug.

## Common questions

**Why do I get an empty array?** The slug is wrong, the company moved ATS, or the board is on the EU host.

**Is `createdAt` the posting date?** It is the creation time of the posting record in milliseconds; for most companies that matches the publish date closely.


## Hosted version, pay per result

If you would rather not run and maintain this yourself, the same logic runs as a pay-per-result Apify Actor by CleanFeeds: https://apify.com/cleanfeedsapi/lever-jobs-feed ($1.50 per 1,000 rows, no subscription, JSON/CSV/Excel export, API, scheduling, n8n/Make/Zapier and MCP integrations). A multi-ATS variant that mixes Greenhouse, Lever, Ashby, Workday, SmartRecruiters and Recruitee boards in one run: https://apify.com/cleanfeedsapi/ats-jobs-feed

The hosted Actor also takes `postedAfter` (an ISO date or `24h` / `7d`), `titleIncludes` and `titleExcludes`. They are applied before the pay-per-result charge, so rows you filter out are never billed. Dates come from the ATS itself, not from when the job was indexed.


## Legal note

These are public, unauthenticated endpoints that the career pages themselves load. Job postings are employer announcements and belong to the employers. Be polite: identify your client with a User-Agent, cache results, and do not hammer the endpoints. Nothing here is affiliated with or endorsed by Lever.
