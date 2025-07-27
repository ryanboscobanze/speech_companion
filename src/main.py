# main.py
import tkinter as tk
from tkinter import ttk
import threading
import queue
import numpy as np
import wave
import sounddevice as sd
import spacy
import os
from collections import deque
from faster_whisper import WhisperModel

from config import OPENROUTER_KEY, GROQ_KEY, GEMINI_KEY, ASSEMBLYAI_API_KEY

from llm_utils import (
    get_llm_suggestion,
    get_llm_support_response,
    get_ambiguous_or_hesitant_prompt,
)
from text_utils import (
    extract_clean_concepts,
    extract_named_entities,
    extract_difficult_definitions,
    detect_ambiguity,
    detect_hesitation,
)

# === Global State ===
from app_state import is_recording, stop_event, audio_queue, stream, row_widgets, recent_utterances, max_context_limit

from transcription import transcribe_with_whisper, transcribe_with_assemblyai

from audio_utils import process_audio_chunk, record_audio

from rowlogic import insert_row, set_context_handler

from controls import list_mics, toggle_recording


set_context_handler(recent_utterances, max_context_limit)

print("✅ App is starting...")

# === Load Models ===
nlp = spacy.load("en_core_web_sm")
try:
    whisper_model = WhisperModel("tiny", compute_type="auto")
    print("✅ WhisperModel loaded")
except Exception as e:
    print("❌ Failed to load WhisperModel:", e)
    whisper_model = None

# === GUI ===
root = tk.Tk()
root.title("🎙️ Smart Suggestion App (Definitions in Table)")
root.geometry("1300x700")
root.configure(bg="black")

top_frame = tk.Frame(root, bg="black")
top_frame.pack(pady=10)

tk.Label(top_frame, text="Mic:", fg="white", bg="black").pack(side=tk.LEFT)
mic_var = tk.StringVar()
mic_menu = ttk.Combobox(top_frame, textvariable=mic_var, width=50, state="readonly")
mic_menu.pack(side=tk.LEFT, padx=10)

tk.Label(top_frame, text="Engine:", fg="white", bg="black").pack(side=tk.LEFT, padx=(20, 5))
engine_var = tk.StringVar(value="AssemblyAI")
engine_menu = ttk.Combobox(top_frame, textvariable=engine_var, width=15, state="readonly")
engine_menu["values"] = ["AssemblyAI", "Whisper"]
engine_menu.pack(side=tk.LEFT)

start_button = tk.Button(top_frame, text="Start", bg="blue", fg="black", width=10)
start_button.pack(side=tk.LEFT, padx=10)

status_label = tk.Label(root, text="Idle", fg="lightgray", bg="black")
status_label.pack()

def update_theme(event=None):
    engine = engine_var.get()
    if engine == "Whisper":
        start_button.config(bg="green")
    elif engine == "AssemblyAI":
        start_button.config(bg="blue")

engine_menu.bind("<<ComboboxSelected>>", update_theme)
update_theme()

canvas_frame = tk.Frame(root, bg="black")
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(canvas_frame, bg="white")
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

header = tk.Frame(scrollable_frame, bg="white")
header.pack(fill="x")
header_columns = ["🗣️ User Speech", "🔑 Concepts", "📖 Difficult Word Definitions", "💡 LLM Suggestions", "🧠 Ambiguity/Hesitation"]
for i, text in enumerate(header_columns):
    tk.Label(
        header, text=text, font=("Arial", 12, "bold"),
        bg="white", anchor="w", width=35, padx=5,
        relief="solid", borderwidth=1
    ).grid(row=0, column=i, sticky="nsew")
header.columnconfigure(tuple(range(5)), weight=1)


is_recording_state = [False]  # using list as a mutable bool container

start_button.config(command=lambda: toggle_recording(
    is_recording_state,
    mic_var,
    start_button,
    mic_menu,
    engine_menu,
    status_label,
    stop_event,
    audio_queue,
    engine_var,
    scrollable_frame,
    header,
    row_widgets,
    canvas,
    root,
    record_audio,
    process_audio_chunk
))

list_mics(mic_menu, mic_var)

root.mainloop()
