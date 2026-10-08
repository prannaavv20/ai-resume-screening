from pathlib import Path
from .parser import extract_candidate
from .scoring import eligibility, score_candidate
from .github_enrichment import enrich
from .llm import review_candidate
from concurrent.futures import ThreadPoolExecutor


def run(input_dir):
    candidates=[]; failures=[]
    for path in sorted(Path(input_dir).glob("*.pdf")):
        try:
            c=extract_candidate(path)
            eligibility(c)
            if c.eligible:
                score_candidate(c)
            candidates.append(c)
        except Exception as e:
            failures.append({"file": path.name, "error": f"{type(e).__name__}: {e}"})
    eligible=[c for c in candidates if c.eligible]
    # Optional semantic LLM review; deterministic scoring remains usable without an API key.
    for c in eligible:
        review = review_candidate(c.text)
        if review:
            c.project_summary = review.summary
            c.score_breakdown["ai_project_depth"] = review.ai_depth
            c.strengths = review.strengths
            c.concerns = review.concerns
            c.total_score = sum(c.score_breakdown.values())

    # GitHub is external I/O; bound concurrency so one slow profile does not block the batch.
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(enrich, eligible))
    eligible=sorted(eligible, key=lambda x:x.total_score, reverse=True)
    rejected=[c for c in candidates if not c.eligible]
    for i,c in enumerate(eligible,1):
        c_dict=c.to_dict(); c_dict["rank"]=i
        # retain rank through a temporary attribute for serializer
        c.rank=i
    return candidates, failures, eligible, rejected
