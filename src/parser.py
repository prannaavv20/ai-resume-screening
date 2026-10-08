import re
from pathlib import Path
from pypdf import PdfReader
from .models import Candidate

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_.-]+", re.I)


def extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def clean(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.replace("\x00", "")).strip()


def extract_name(text: str, filename: str) -> str:
    for line in text.splitlines():
        line = clean(line)
        if not line or any(x in line.lower() for x in ["resume", "curriculum vitae"]):
            continue
        if EMAIL_RE.search(line) or "linkedin" in line.lower() or "github" in line.lower():
            continue
        if 1 < len(line.split()) <= 5 and not any(c.isdigit() for c in line):
            return line.strip("|•-")
    return Path(filename).stem


def extract_candidate(path: Path) -> Candidate:
    raw = extract_pdf(path)
    text = clean(raw)
    email = EMAIL_RE.search(text)
    github = GITHUB_RE.search(text)
    skills = extract_skills(text)
    return Candidate(
        source_file=path.name,
        name=extract_name(raw, path.name),
        email=email.group(0) if email else None,
        github_url=("https://" + github.group(0).strip()) if github else None,
        text=text,
        skills=skills,
        projects=extract_project_sections(text),
    )


def extract_skills(text: str) -> list[str]:
    terms = [
        "Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "GCP", "AWS",
        "React", "Next.js", "Node.js", "RAG", "LLM", "AI Agents", "LangChain",
        "LangGraph", "LlamaIndex", "Hugging Face", "OpenAI", "Claude", "Gemini",
        "Neo4j", "Vector Search", "Embeddings", "Tool Calling", "Machine Learning",
        "TensorFlow", "PyTorch", "GitHub Actions"
    ]
    low = text.lower()
    return [term for term in terms if term.lower() in low]


def extract_project_sections(text: str) -> list[str]:
    chunks = re.split(r"(?i)\b(?:projects?|work experience|experience|education|certifications?)\b", text)
    return [c[:2500] for c in chunks if len(c.strip()) > 80]
