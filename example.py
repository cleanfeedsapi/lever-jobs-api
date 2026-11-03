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

def diff(prev_path, rows):
    """Return (new, closed) ids versus a previous JSON snapshot."""
    try:
        prev = {r["id"] for r in json.load(open(prev_path))}
    except FileNotFoundError:
        prev = set()
    cur = {r["id"] for r in rows}
    return sorted(cur - prev), sorted(prev - cur)

if __name__ == "__main__":
    rows = list(lever_jobs("spotify")); print(len(rows), "jobs"); print(rows[0])
