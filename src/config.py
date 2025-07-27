# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
