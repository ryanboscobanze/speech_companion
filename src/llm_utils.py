# llm_utils.py
import requests
import logging
import google.generativeai as genai
from config import OPENROUTER_KEY, GROQ_KEY, GEMINI_KEY

def get_llm_suggestion(context_text):
    print("🧠 Entering get_llm_suggestion()")
    logging.debug("🧠 Context Text: %s", context_text)

    prompt = f"""
[INST]
You are a real-time conversation enhancer.

Input: {context_text}

Your task:
- Do NOT repeat or reference the input.
- Output only three bullet lists:
  - jargon: domain-relevant jargon (short buzzwords only)
  - glossary: compact glossary terms (noun phrases)
  - followup: follow-up ideas (noun phrases or fragments)

Respond using clean markdown bullet points only. No intro, no explanation, no labels.
[/INST]
""".strip()

    messages = [{"role": "user", "content": prompt}]
    
    try:
        print("🌐 Trying OpenRouter API...")
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 200
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=10)
        result = res.json()["choices"][0]["message"]["content"].strip()
        print("✅ OpenRouter Success:\n", result)
        return result
    except Exception as e:
        print("❌ OpenRouter failed:", e)

    try:
        print("🌐 Trying GROQ API...")
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 200
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
        result = res.json()["choices"][0]["message"]["content"].strip()
        print("✅ GROQ Success:\n", result)
        return result
    except Exception as e2:
        print("❌ GROQ failed:", e2)

    try:
        print("🌐 Trying Gemini API...")
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(prompt)
        result = res.text.strip()
        print("✅ Gemini Success:\n", result)
        return result
    except Exception as e3:
        print("❌ Gemini failed:", e3)
        logging.exception("❌ All LLMs failed")
        return "—"

def get_llm_support_response(prompt):
    print("🧠 Entering get_llm_support_response()")
    logging.debug("📨 Prompt for support LLM:\n%s", prompt)

    messages = [{"role": "user", "content": prompt}]

    try:
        print("🌐 Trying OpenRouter API (Support Mode)...")
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 200
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=10)
        result = res.json()["choices"][0]["message"]["content"].strip()
        print("✅ OpenRouter Support Success:\n", result)
        return result
    except Exception as e:
        print("❌ OpenRouter (Support) failed:", e)

    try:
        print("🌐 Trying GROQ API (Support Mode)...")
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 200
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
        result = res.json()["choices"][0]["message"]["content"].strip()
        print("✅ GROQ Support Success:\n", result)
        return result
    except Exception as e2:
        print("❌ GROQ (Support) failed:", e2)

    try:
        print("🌐 Trying Gemini API (Support Mode)...")
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(prompt)
        result = res.text.strip()
        print("✅ Gemini Support Success:\n", result)
        return result
    except Exception as e3:
        print("❌ Gemini (Support) failed:", e3)
        logging.exception("❌ All support LLMs failed")

    return "—"

def get_ambiguous_or_hesitant_prompt(context, ambiguous=False, hesitant=False):
    if ambiguous and hesitant:
        return f"""[INST]
The user appears to be speaking hesitantly while trying to recall a specific name, term, or concept.

Input: {context}

Your task:
- Offer 3–5 possible terms or concepts the user may be trying to recall.
- Offer brief descriptions.
- Be helpful and speculative.

Format:
- guess 1: description
- guess 2: description
...
[/INST]""".strip()
    
    elif ambiguous:
        return f"""[INST]
The user appears to be trying to recall a specific name, term, or concept.

Input: {context}

Your task:
- Offer 3–5 possible terms the user may be trying to remember.
- Include short descriptions.

Format:
- guess 1: description
...
[/INST]""".strip()
    
    elif hesitant:
        return f"""[INST]
The user is speaking hesitantly and might be unsure.

Input: {context}

Your task:
- Offer 2–3 clarifying suggestions.
- Suggest possible interpretations.

Format:
- clarification: suggestion
...
[/INST]""".strip()

    else:
        return f"""[INST]
You are a real-time conversation enhancer.

Input: {context}

Your task:
- Output three bullet lists:
  - jargon: domain buzzwords
  - glossary: key noun phrases
  - followup: good next ideas

No input repeats. Markdown bullets only.
[/INST]""".strip()
