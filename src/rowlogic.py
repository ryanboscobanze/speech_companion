# rowlogic.py
import tkinter as tk
from collections import deque

from text_utils import (
    extract_difficult_definitions,
    detect_ambiguity,
    detect_hesitation,
)
from llm_utils import (
    get_llm_suggestion,
    get_llm_support_response,
    get_ambiguous_or_hesitant_prompt,
)

# This variable will be injected from main.py
recent_utterances = None
max_context_limit = None

def set_context_handler(_recent_utterances, _max_context_limit):
    global recent_utterances, max_context_limit
    recent_utterances = _recent_utterances
    max_context_limit = _max_context_limit

def update_recent_utterances(new_utterance):
    global recent_utterances
    if recent_utterances.maxlen < max_context_limit:
        items = list(recent_utterances)
        recent_utterances = deque(items, maxlen=recent_utterances.maxlen + 1)
    recent_utterances.append(new_utterance)

def insert_row(text, concepts, entities, engine_name, scrollable_frame, header, row_widgets, canvas):
    try:
        row_color = "green" if engine_name == "Whisper" else "blue"
        row = tk.Frame(scrollable_frame, bg=row_color)
        update_recent_utterances(text)

        llm_response = "—"
        if len(recent_utterances) >= 2:
            context = " ".join(recent_utterances)
            ambiguous = detect_ambiguity(context)
            hesitant = detect_hesitation(context)

            if ambiguous or hesitant:
                prompt = get_ambiguous_or_hesitant_prompt(context, ambiguous, hesitant)
                llm_response = get_llm_support_response(prompt)

            llm_suggestion = get_llm_suggestion(context)
        else:
            llm_suggestion = "—"

        try:
            defs = extract_difficult_definitions(text)
        except Exception as e:
            print("❌ Error in extract_difficult_definitions:", e)
            defs = "❌ Error extracting definitions"

        all_values = [text or "—", concepts or "—", defs or "❌ Error", llm_suggestion or "—", llm_response or "—"]

        for i, val in enumerate(all_values):
            lbl = tk.Label(
                row,
                text=str(val),
                font=("Arial", 11),
                fg="white",
                bg=row_color,
                wraplength=300,
                justify="left",
                anchor="w",
                width=35,
                padx=5,
                pady=5,
                relief="solid",
                borderwidth=1
            )
            lbl.grid(row=0, column=i, sticky="nsew")

        for i in range(5):
            row.columnconfigure(i, weight=1)

        row_widgets.insert(0, row)
        for widget in scrollable_frame.winfo_children():
            if widget != header:
                widget.pack_forget()
        for r in row_widgets:
            r.pack(fill="x", anchor="w", pady=2)
        canvas.yview_moveto(0)

    except Exception as e:
        print("❌ Error in insert_row:", e)
