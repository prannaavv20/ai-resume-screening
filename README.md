# AI Resume Screening & Ranking System

## Overview
A small production-minded Python pipeline that processes a folder of PDF resumes, applies deterministic eligibility rules, scores eligible candidates, optionally uses an LLM for semantic AI-project review, enriches GitHub activity, and writes an explainable JSON shortlist.

## Run
```bash
pip install -r requirements.txt
python main.py --input ./resumes --output ./output/results.json
```

Optional environment variables:
```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
GITHUB_TOKEN=...
```

Without `OPENAI_API_KEY`, the system uses its deterministic scoring fallback. A missing/failing LLM or GitHub call never stops the whole batch.

## Architecture
1. **Ingestion:** read every PDF and extract text with `pypdf`.
2. **Candidate extraction:** derive name, email, GitHub URL and matched skills.
3. **Hard eligibility:** require both genuine Python evidence and meaningful AI/LLM/agentic evidence. This is deterministic and stays outside the LLM.
4. **Ranking:** score AI/project depth (40), Python/backend (30), cloud/full-stack (15), GitHub (10), and engineering depth (5).
5. **Semantic AI review:** when configured, the LLM returns a Pydantic-validated structured result containing an AI-depth score, short evidence-based summary, strengths and concerns. Provider-specific code is isolated in `src/llm.py`.
6. **GitHub enrichment:** public repositories are fetched with bounded concurrency. Failures are recorded and scored as zero rather than failing the batch.
7. **Output:** produce machine-readable JSON containing ranks, eligibility, rejection reasons, score breakdown, matched skills, summaries, GitHub status and batch statistics.

## Design Decisions
- Hard eligibility is deterministic because Python + AI evidence are explicit requirements and should not vary between LLM calls.
- LLM judgment is used only for semantic project-depth assessment, where understanding whether a project is meaningful is harder to express with keywords.
- A shallow-project guardrail caps weak AI evidence so an API-only wrapper does not receive a top AI score.
- External GitHub I/O uses bounded concurrency and short timeouts so one slow/rate-limited profile cannot block the entire batch.
- Configuration and credentials are environment-based; no secrets are hard-coded.
- JSON is preferred because it preserves score breakdowns and reasoning cleanly.
- The pipeline is modular so parsing, scoring, LLM review, and GitHub enrichment can be tested or replaced independently.

## Testing
```bash
pytest -q
```
The included tests cover the core eligibility rules.

## If I Had More Time
1. Add stronger PDF-layout extraction and section-aware project parsing.
2. Cache GitHub/LLM results by profile/resume hash.
3. Add async HTTP enrichment with explicit rate-limit backoff.
4. Add integration tests with malformed PDFs and mocked GitHub/LLM failures.
