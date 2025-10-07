from .retriever import retrieve
from .generator import generate

def rag_pipeline(query: str):
    context = retrieve(query)
    return generate(context, query)
