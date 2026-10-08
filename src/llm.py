import os
from typing import Optional
from pydantic import BaseModel, Field

class ProjectReview(BaseModel):
    summary: str = Field(description="One short evidence-based project summary")
    ai_depth: int = Field(ge=0, le=40)
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)


def review_candidate(text: str) -> Optional[ProjectReview]:
    """Optional semantic review. Deterministic scoring remains the fallback."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        prompt = (
            "Review this resume only for the depth of its AI/LLM/agentic project work. "
            "Use evidence from the text. Do not invent technologies. Score AI depth 0-40. "
            "Return a short summary, strengths, and concerns.\n\nRESUME:\n" + text[:12000]
        )
        response = client.beta.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role":"system","content":"You are an explainable resume-screening evaluator."},
                {"role":"user","content":prompt},
            ],
            response_format=ProjectReview,
        )
        return response.choices[0].message.parsed
    except Exception:
        return None
