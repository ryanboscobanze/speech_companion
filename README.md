The Smart Suggestion App listens to you speak and provides intelligent suggestions, definitions, and insights in real time.

People often hesitate in conversation or forget the right word. I do. What if software could listen and help in real time? 

This sets the stage. You're not just building a fancy mic-to-text app — you’re solving the problem of:

- Forgetting words mid-sentence

- Not knowing the meaning of something you said

- Needing extra suggestions or support while speaking

- open powershell or terminal as an admin and run 

Let's break it down:

- 🎙️ User speaks into the mic
- 📝 App transcribes speech using Whisper or AssemblyAI
- 🧠 Text is analyzed using spaCy:
    - Named Entities (like places, people)
    - Key Concepts
    - Hard-to-understand words
- ❓ Ambiguity & hesitation are detected using NLP patterns
- 🤖 LLM suggestions are generated via OpenRouter, Gemini, or Groq
- 📋 Everything is displayed in a live table, color-coded by engine

Highlight Key Features
- Mic input using sounddevice
- Fast transcription with Whisper or API-based with AssemblyAI
- Extract definitions for difficult words
- Context-aware suggestions from LLMs (via OpenRouter / Groq / Gemini)
- Detects if you're unsure or confused
- Real-time table UI (made in Tkinter)

Audience / Use Cases
- You can say this app could be used by:
- ESL (English as Second Language) learners
- Public speakers who practice clarity
- UX researchers testing speech flow
- Teachers or students building NLP demos

```
python setup.py # this will create an environment with all libraries
```

.env

    .env file is essential for managing sensitive data like API keys without hardcoding them into your source code.

    
    OPENROUTER_KEY=your_openrouter_api_key
    GROQ_KEY=your_groq_api_key
    GEMINI_KEY=your_google_generative_ai_key
    ASSEMBLYAI_API_KEY=your_assemblyai_key
    
    ✅ These values are then passed to the correct APIs in llm_utils.py and transcription.py.

1. main.py – 🧠 The Brain / App Launcher

- Initializes the app
- Loads models
- Builds the GUI
- Wires everything together
📌 Entry point script

2. controls.py – 🎮 UI Controls

- Contains logic for the Start/Stop button
- Manages mic dropdown and engine selection
- Talks to record_audio() when user presses "Start"
📌 GUI interaction

3. audio_utils.py – 🎤 Audio Capture & Chunking
- Handles mic streaming via sounddevice
- Buffers audio and sends chunks for processing
- Triggers process_audio_chunk() which decides how to transcribe
📌 This is the audio engine of the app.

4. transcription.py – ✍️ Speech-to-Text
- Uses faster-whisper for local transcription
- Uses AssemblyAI if cloud-based transcription is selected
- Returns raw transcribed text
📌 This is  decoupled from GUI — just takes in a file and gives you text.

5. text_utils.py – 🧠 NLP & Linguistic Analysis
Extracts:
- Key concepts
- Named entities
- Difficult word definitions
- Detects ambiguity or hesitation
📌 This is where text becomes meaning.

6. llm_utils.py – 🤖 LLM Suggestion Engine
- Calls OpenRouter / Groq / Gemini
- Asks LLMs to offer follow-up suggestions or clarification
- Uses special prompt logic for hesitant speech
📌 This is the smart assistant layer.

7. rowlogic.py – 📋 Table Row Generator
- Formats the transcribed + analyzed output
- Inserts a row into the Tkinter table
- Color-codes based on engine type
📌 Think of it as the presentation layer that updates the UI with smart info.

8. app_state.py – 🗃️ Shared Variables
- Contains is_recording, stream, audio_queue, etc.
- Shared across modules without circular imports
📌 It’s the app’s global memory and switches.

📂 controls.py — UI Control Logic
  
    This module handles all user-facing control actions, specifically:

    🎮 1. list_mics(mic_menu, mic_var)
      Purpose: Populates the dropdown with all available input devices (microphones).

      🔑 Key Points:
      - Uses sounddevice.query_devices() to detect input-capable devices.
      - Formats them as "index: name" for easy display.
      - Automatically selects the first mic by default (mic_menu.current(0)).

      Users can dynamically select any available microphone — crucial for cross-platform support.

    🔴🟢 2. toggle_recording(...)
      Purpose: Controls the behavior of the Start/Stop button.

      🔄 Two Modes:
      
        Start Mode:
        - Extracts selected mic index and Changes button state to “Stop”
        - Disables engine/mic selection
        - Starts a new thread with record_audio(...)

        Stop Mode:
        - Signals the stop_event then Resets UI elements also Updates recording state

        🔑 Key Points:
        Uses a mutable list is_recording_state[0] as a recording flag (avoids global). Triggers threaded recording without freezing the GUI. Delegates actual audio streaming to record_audio in audio_utils.py.

        controls.py handles what happens when you click the Start/Stop button or select a microphone. It ensures the UI reacts smoothly and starts background audio recording without freezing the app.


📂 audio_utils.py — Audio Streaming & Chunk Processing
  
    audio_utils.py is the core engine that powers real-time speech capture. It listens to the mic, breaks audio into chunks, sends them off for transcription and NLP, and then lets the GUI update with results — all without freezing the app.

    This file contains the logic to:
    - Stream audio live from a microphone
    - Process it into transcribable chunks
    - Kick off downstream transcription + NLP
    - Update the UI with results

    🔁 1. record_audio(...)

      Purpose: Start capturing live microphone audio in a non-blocking way and process it chunk by chunk.

      🔄 Key Steps:
      - Clears the queue and sets Recording... on UI
      - Starts a sounddevice.InputStream
      - Pushes audio frames into a queue using a callback
      - Buffers audio data until a threshold (160000 samples = ~10 seconds)
      - Calls process_audio_chunk() in a separate thread

    🔍 2. process_audio_chunk(...)
    
      Purpose: Take a raw chunk of audio, transcribe it, extract concepts, and update the results table.

      🔄 Key Steps:
      - Saves the chunk to temp_chunk.wav
      - Transcribes it with the selected engine (Whisper or AssemblyAI)
      - Runs spaCy NLP to extract Concepts and Named entities
      - Uses root.after(...) to call insert_row() safely on the GUI thread

📂 transcription.py — Speech-to-Text Engines

    transcription.py is a core component of your pipeline. It abstracts the speech-to-text functionality and offers a plug-and-play interface for local and cloud transcription engines.

    This file provides two transcription methods:
    - Local, fast, offline using faster-whisper
    - Cloud-based, accurate using AssemblyAI

    🧠 1. transcribe_with_whisper(audio_path)
    
      Purpose: Transcribes an audio file using the lightweight faster-whisper model locally.

      🔧 Key Behavior:
      - Loads WhisperModel("tiny") once at import time or any faster variant in the whisper family of models contingent of infrastructure availability, intentionally chosen the smallest size for demo.
      - Transcribes segments and joins them into one clean string
      - Runs fully offline (after initial model download)

  ☁️ 2. transcribe_with_assemblyai(audio_path)

      Purpose: Transcribes audio using AssemblyAI, a cloud-based API service.

      🔁 Key Steps:
      - Uploads audio to AssemblyAI via /upload
      - Creates a transcript job via /transcript
      - Polls the /transcript/{id} endpoint until complete
      - Returns the full transcription string

📂 text_utils.py — NLP Features & Language Intelligence

    This file performs three main jobs:
    - 🧠 Extracts meaningful concepts and entities
    - 📖 Detects and defines difficult words
    - ❓ Flags ambiguity and hesitation in speech

    1. Concept & Entity Extraction

      📌 extract_named_entities(doc): 
      - Returns all named entities (PERSON, ORG, GPE, etc.) in the text using spaCy.
      - Output is a comma-separated string (e.g., "Einstein, NASA, Paris")

      📌 extract_clean_concepts(doc):
      - Filters out filler/pronouns (he, she, it, etc.)
      - Extracts core nouns, adjectives, noun chunks
      - Deduplicates named entities
      - Lemmatizes and cleans punctuation
      - Returns concepts like "gravity, moon, theory"

    2. Difficult Word Detection & Definition

      📌 is_potentially_difficult(word):
      - Uses wordfreq to flag rare words (< 0.000005 frequency)

      📌 get_definition(word)
      - Queries Free Dictionary API to get simple definitions
      - Logs missing or failed lookups for debugging

      📌 extract_difficult_definitions(txt)
      - Scans user utterance for hard words
      - Looks up definitions for each
      - Returns them as "word: definition" entries

    3. Ambiguity & Hesitation Detection

      📌 detect_ambiguity(utterance)
      - Uses regular expressions to catch phrases like:
          “What’s it called?”,  “I can’t remember the word”, “The thing that goes...” some more common phrases that can be extracted.

      📌 detect_hesitation(utterance)
      - Looks for filler speech patterns:
          “uh”, “um”, “you know”, “like”, “kind of...”
      - Triggers only when 2 or more are present


📂 llm_utils.py — LLM Integration & Smart Prompts

    This file connects your app to multiple AI models and defines how to talk to them in real-time. This is the brain behind the assistant’s intelligence. It talks to Mistral, Groq, or Gemini and fetches jargon, glossaries, or helpful guesses in real time. If the user seems confused, it gently steps in with clarifications — just like a good co-pilot.

    🤖 1. get_llm_suggestion(context_text)

        Purpose: Given a user’s spoken context, this function calls an LLM to generate:

        - jargon (buzzwords)
        - glossary terms
        - follow-up ideas

        🔁 Fallback Flow:
        - Tries OpenRouter (Mistral)
        - If that fails, tries Groq (LLaMA 3)
        - If that fails, tries Gemini (Google)

    🧠 2. get_llm_support_response(prompt)

        Purpose: Generates support when user is confused or hesitant. This powers the 🧠 Ambiguity/Hesitation column in your app — giving empathetic AI assistance. Similar to get_llm_suggestion, but:

        - Prompt is more speculative/helpful
        - Models provide guesses or clarifications based on ambiguous context

    ✍️ 3. get_ambiguous_or_hesitant_prompt(context, ambiguous, hesitant)

        Purpose: Creates the actual prompt string for get_llm_support_response.

        - If ambiguous=True, generates a recall-style prompt (“guess what the user meant”)
        - If hesitant=True, generates clarifying suggestions
        - If both are true, generates combined recall + clarification

📂 rowlogic.py — UI Row Generation & Context Tracking

    rowlogic.py is where all the hard work (speech → transcription → NLP → LLM) gets visualized in the GUI. This file essentially translates intelligence into interface.


    🧠 1. set_context_handler(_recent_utterances, _max_context_limit)
        - Purpose: Injects shared global values from main.py
        - recent_utterances holds a rolling history of past phrases
        - max_context_limit controls how much context is kept

    🌀 2. update_recent_utterances(new_utterance)
        - Purpose: Appends a new utterance to the deque, dynamically increasing its length if needed
        - Ensures that LLMs get a rich, running context (not just the latest line) and 
        enables better ambiguity/hesitation detection over a larger span of dialogue

    📋 3. insert_row(...)
        - Purpose: The main function that populates a new row in the scrollable table UI

        🔄 Processing Flow:
        - 🟩 Sets row_color based on engine (Whisper = green, AssemblyAI = blue)
        - 📜 Updates context history
        - ❓ Checks for ambiguity or hesitation in full context
        - 🤖 If detected, fetches a support response via get_llm_support_response
        - 💡 Fetches smart LLM suggestions via get_llm_suggestion
        - 📖 Extracts difficult word definitions via extract_difficult_definitions
        - 🧱 Assembles and formats all the output into a color-coded, scrollable table row

📂 app_state.py — Global State Management
    
    This file defines all the mutable global objects used across your app, including:

    - 🎙️ Recording state
    - 🧵 Thread control signals
    - 📥 Audio buffering
    - 📋 Table widget memory
    - 🧠 Utterance context


📂 main.py — App Launcher & GUI Orchestrator

    main.py is the command center. It wires together the GUI, loads the models, and passes control to modular logic files that handle transcription, audio, NLP, and LLMs. It keeps everything organized and clean, making the app easy to maintain and extend.

    This is the central hub that:

      - Loads all models and shared state
      - Sets up the full Tkinter GUI
      - Connects UI buttons to control logic
      - Initializes the microphone and engine
      - Starts the app loo    

    🧠 1. Model Initialization
      - Loads the spaCy NLP model for extracting concepts/entities
      - Loads the faster-whisper model for local transcription 

    🎨 2. GUI Setup (Tkinter)
      - Mic input dropdown (mic_menu)
      - Transcription engine selector (engine_menu)
      - Start/Stop button (start_button)
      - Scrollable table (canvas, scrollable_frame)
      - Header row with 5 labeled columns

    🎛️ 3. Engine Theme Logic 
      - Changes button color depending on engine
      - Adds polish to the UI interaction

    🧵 4. Mic Control Binding
      Passes everything into toggle_recording from controls.py, including:
      - UI elements
      - Audio streaming logic
      - App state (stop_event, audio_queue, record_audio, etc.)

    📥 5. Mic List Initialization
      - Populates mic dropdown on startup using sounddevice.query_devices()

    🔁 6. App Loop
    - Keeps the GUI alive and responsive
    - Handles all events and UI updates in a single-threaded loop
