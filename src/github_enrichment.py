import json
import os
import re
import urllib.request
import urllib.error


def username_from_url(url):
    if not url: return None
    m = re.search(r"github\.com/([^/\s]+)", url, re.I)
    return m.group(1) if m else None


def enrich(c):
    username = username_from_url(c.github_url)
    if not username:
        c.github_summary = "No public GitHub profile found; GitHub score: 0/10."
        c.score_breakdown["github"] = 0
        c.total_score = sum(c.score_breakdown.values())
        return c
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{username}/repos?per_page=30&sort=updated",
            headers={"Accept":"application/vnd.github+json", "User-Agent":"resume-screening-assignment"}
        )
        token = os.getenv("GITHUB_TOKEN")
        if token: req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=5) as r:
            repos = json.load(r)
        maintained = [x for x in repos if not x.get("fork")]
        relevant = [x for x in maintained if any(k in ((x.get("language") or "") + " " + (x.get("name") or "")).lower() for k in ["python", "ai", "ml", "rag", "agent"])]
        recent = min(5, len(maintained))
        relevant_pts = min(5, len(relevant))
        score = recent + relevant_pts
        c.score_breakdown["github"] = score
        c.total_score = sum(c.score_breakdown.values())
        c.github_summary = f"Public profile: {len(maintained)} maintained repos; {len(relevant)} Python/AI-relevant repos; GitHub score: {score}/10."
    except Exception as e:
        c.score_breakdown["github"] = 0
        c.total_score = sum(c.score_breakdown.values())
        c.github_summary = f"GitHub enrichment failed gracefully ({type(e).__name__}); score: 0/10."
    return c
