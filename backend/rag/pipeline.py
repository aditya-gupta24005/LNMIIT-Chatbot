from .retriever import search
from .generator import answer_with_gemini

def rag_pipeline(query: str):
    answer, sources = answer_with_gemini(query)
    return {
        "query": query,
        "response": answer,
        "sources": sources
    }

if __name__ == "__main__":
    
    res = rag_pipeline("What is the placement record?")
    print(res["answer"])