AI_TERMS = ["llm", "rag", "agent", "agents", "langchain", "langgraph", "llamaindex", "embeddings", "vector search", "tool calling", "multi-agent", "genai", "generative ai"]
PYTHON_TERMS = ["python", "fastapi", "django", "flask", "pandas", "numpy", "pytest", "python3"]
DEPTH_TERMS = ["workflow", "pipeline", "retrieval", "validation", "evaluation", "tool calling", "state", "orchestration", "knowledge graph", "multi-hop", "document processing", "classification", "inference", "backend", "api", "database"]
CLOUD_TERMS = ["gcp", "google cloud", "cloud run", "docker", "aws", "azure", "vercel", "netlify", "render"]
BACKEND_TERMS = ["python", "fastapi", "async", "postgresql", "redis"]
ENGINEERING_TERMS = ["testing", "pytest", "architecture", "caching", "queue", "observability", "concurrency", "retry", "error handling", "failure handling"]


def has_term(text, terms):
    low = text.lower()
    return any(t in low for t in terms)


def evidence_terms(text, terms):
    low = text.lower()
    return [t for t in terms if t in low]


def eligibility(c):
    low = c.text.lower()
    python_ok = has_term(low, PYTHON_TERMS)
    ai_ok = has_term(low, AI_TERMS)
    reasons = []
    if not python_ok: reasons.append("No evidence of Python stack")
    if not ai_ok: reasons.append("No AI/agentic project evidence")
    c.eligible = python_ok and ai_ok
    c.rejection_reasons = reasons
    c.matched_skills = c.skills
    return c


def score_candidate(c):
    text = c.text.lower()
    # AI / Agentic / RAG: 40
    ai_hits = evidence_terms(text, AI_TERMS)
    depth_hits = evidence_terms(text, DEPTH_TERMS)
    ai = min(40, 10 + len(set(ai_hits))*3 + len(set(depth_hits))*2)
    if len(ai_hits) <= 1 and len(depth_hits) <= 2:
        ai = min(ai, 20)  # shallow-project guardrail

    # Python/backend: 30
    backend_hits = evidence_terms(text, BACKEND_TERMS)
    python = min(30, len(set(backend_hits))*6 + (6 if "python" in text else 0))

    # Cloud/full-stack: 15
    cloud_hits = evidence_terms(text, CLOUD_TERMS)
    fullstack = 3 * len(set(cloud_hits)) + (3 if "react" in text or "next.js" in text else 0)
    fullstack = min(15, fullstack)

    # GitHub is filled by enrichment.
    github = 0

    # Engineering depth: 5
    eng_hits = evidence_terms(text, ENGINEERING_TERMS)
    engineering = min(5, len(set(eng_hits)))

    c.score_breakdown = {
        "ai_project_depth": ai,
        "python_backend": python,
        "cloud_fullstack": fullstack,
        "github": github,
        "engineering_depth": engineering,
    }
    c.total_score = sum(c.score_breakdown.values())
    c.project_summary = build_project_summary(c)
    c.strengths = []
    if ai >= 25: c.strengths.append("Strong AI/agentic project evidence")
    if python >= 18: c.strengths.append("Good Python/backend evidence")
    if fullstack >= 9: c.strengths.append("End-to-end/full-stack or cloud evidence")
    c.concerns = []
    if python < 12: c.concerns.append("Limited Python/backend evidence")
    if ai < 20: c.concerns.append("AI project depth appears limited")
    return c


def build_project_summary(c):
    low = c.text.lower()
    pieces = []
    if "rag" in low: pieces.append("RAG/retrieval")
    if "agent" in low: pieces.append("agentic workflows")
    if "tool calling" in low: pieces.append("tool calling")
    if "knowledge graph" in low: pieces.append("knowledge graphs")
    if "embedding" in low: pieces.append("embeddings")
    if "fastapi" in low: pieces.append("FastAPI backend")
    return "Built/mentioned " + ", ".join(pieces[:4]) + "." if pieces else "Relevant Python/AI evidence found in resume."
