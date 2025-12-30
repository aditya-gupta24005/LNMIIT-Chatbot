import os
import sys
import re
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted

try:
    from .retriever import search
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from retriever import search
    except ImportError:
        try:
            from rag.retriever import search
        except ImportError:
            print("Error: Could not import 'search' from retriever.")
            sys.exit(1)

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "0"

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("CRITICAL WARNING: GEMINI_API_KEY is missing.")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "If the user asks 'Who are you?' or any equivalent question about your identity, reply only with: 'I am an assistant for LNMIIT.' "
    "Dont say based on the provided context or context above, just say i don't know that information"
    "Dont give half or incomplete information"
    "The doaa or dean of academic affairs is Dr Vikas Gupta"
    "You are a strict and concise assistant for LNMIIT. "
    "Your responses must not exceed 5 sentences or 120 words under any circumstance. "
    "If you provide a list, include only the top 3 items. "
    "Avoid unnecessary explanation, speculation, or filler. "
    "Remain factual, context-bound, and do not invent information not supported by the user's input or established LNMIIT details."
)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_INSTRUCTION
)

def build_context(results):
    parts = []
    for r in results:
        content = r.get("content", "").strip()
        if not content:
            continue
        content = textwrap.shorten(content, width=2500, placeholder=" ...")
        parts.append(content)
    return "\n\n".join(parts)

def enforce_short_answer(text):
    text = text.strip()
    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) > 5:
        text = " ".join(sentences[:5])
    words = text.split()
    if len(words) > 120:
        text = " ".join(words[:120]) + "..."
    return text

def answer_with_gemini(query, top_k=5):
    try:
        results = search(query, top_k=top_k)
    except Exception as e:
        return f"Error during retrieval: {e}", []

    if not results:
        return "I couldn't find relevant information.", []

    context_str = build_context(results)
    prompt = (
        f"USER QUESTION: {query}\n\n"
        f"CONTEXT:\n{context_str}\n\n"
        "Based strictly on the context above, answer concisely."
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 2000},
            safety_settings=SAFETY_SETTINGS
        )
        if not response.candidates:
            return "Error: No response returned.", []
        return enforce_short_answer(response.text), results
    except ResourceExhausted:
        return "Service is currently overloaded (Rate Limit Reached). Please try again later.", []
    except Exception as e:
        return f"Error generating response: {str(e)}", []

if __name__ == "__main__":
    while True:
        try:
            q = input("\nAsk me something about LNMIIT (or 'exit'): ").strip()
            if q.lower() in ["exit", "quit"]:
                break
            if q:
                ans = answer_with_gemini(q)
                print("\nANSWER\n")
                print(ans)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
