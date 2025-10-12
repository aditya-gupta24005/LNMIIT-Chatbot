# generator_gemini.py
import os
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"
import google.generativeai as genai
from retriever import search
from textwrap import shorten

# Configure Gemini API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are a concise and accurate assistant for LNMIIT. "
    "Use only the retrieved sources to answer the question. "
    "Cite the source numbers [1], [2], etc. after factual statements. "
    "If the answer isn't supported by sources, say you don't know."
)

def build_context(results):
    parts = []
    for i, r in enumerate(results, start=1):
        title = r.get("title") or r.get("url")
        url = r.get("url", "")
        content = shorten(r.get("content", ""), width=1500, placeholder=" ...")
        parts.append(f"[{i}] {title}\n{url}\n{content}")
    return "\n\n".join(parts)

def answer_with_gemini(query: str, top_k: int = 5, temperature: float = 0.0):
    # 1) Retrieve from your local index
    results = search(query, top_k=top_k)

    # 2) Build a combined prompt
    context = build_context(results)
    user_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User question: {query}\n\n"
        f"Relevant sources:\n{context}\n\n"
        "Answer clearly, cite sources, and keep the answer concise."
    )

    # 3) Send to Gemini
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(user_prompt, generation_config={
        "temperature": temperature,
        "max_output_tokens": 512,
    })

    # 4) Extract text response
    return response.text, results

if __name__ == "__main__":
    q = input("Ask me something: ")
    ans, srcs = answer_with_gemini(q)
    print("\n ANSWER \n")
    print(ans)
    print("\n SOURCES\n")
    for i, s in enumerate(srcs, start=1):
        print(f"[{i}] {s['title']} - {s['url']} (score={s['score']:.3f})")
