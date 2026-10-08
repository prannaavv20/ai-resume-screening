from src.models import Candidate
from src.scoring import eligibility

def c(text): return Candidate("x.pdf","X",None,None,text,[],[])

def test_python_ai_eligible():
    x=eligibility(c("Python FastAPI built a RAG agent with embeddings")); assert x.eligible

def test_no_python_rejected():
    x=eligibility(c("JavaScript React built a RAG application")); assert not x.eligible

def test_no_ai_rejected():
    x=eligibility(c("Python FastAPI PostgreSQL backend")); assert not x.eligible
