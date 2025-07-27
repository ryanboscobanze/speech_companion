# audio_utils.py
import wave
import numpy as np
import spacy

from transcription import transcribe_with_assemblyai, transcribe_with_whisper
from text_utils import extract_clean_concepts, extract_named_entities
from rowlogic import insert_row

import queue
import threading
import sounddevice as sd

stream = None  # Local stream handle

nlp = spacy.load("en_core_web_sm")

def process_audio_chunk(chunk, engine_name, scrollable_frame, header, row_widgets, canvas, root):
    try:
        path = "temp_chunk.wav"
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes((chunk * 32767).astype(np.int16).tobytes())

        if engine_name == "AssemblyAI":
            text = transcribe_with_assemblyai(path)
        elif engine_name == "Whisper":
            text = transcribe_with_whisper(path)
        else:
            print("⚠️ Unknown engine selected")
            return

        if text:
            doc = nlp(text)
            concepts = extract_clean_concepts(doc)
            entities = extract_named_entities(doc)
            root.after(0, lambda: insert_row(text, concepts, entities, engine_name, scrollable_frame, header, row_widgets, canvas))
    except Exception as e:
        print("❌ process_audio_chunk failed:", e)




def record_audio(device_index, stop_event, audio_queue, status_label,
                 process_audio_chunk, engine_var, scrollable_frame, header,
                 row_widgets, canvas, root):
    global stream
    stop_event.clear()
    audio_queue.queue.clear()
    status_label.config(text="Recording...")

    def callback(indata, frames, time_info, status):
        if status:
            print(f"⚠️ Stream status: {status}")
        audio_queue.put(indata.copy())

    try:
        stream = sd.InputStream(device=device_index, callback=callback, channels=1, samplerate=16000)
        stream.start()
        buffer = []

        while not stop_event.is_set():
            try:
                data = audio_queue.get(timeout=0.25)
                buffer.append(data)
                total_samples = sum(len(chunk) for chunk in buffer)
                if total_samples >= 160000:
                    chunk_audio = np.concatenate(buffer, axis=0)
                    buffer = []
                    threading.Thread(
                        target=process_audio_chunk,
                        args=(chunk_audio, engine_var.get(), scrollable_frame, header, row_widgets, canvas, root),
                        daemon=True
                    ).start()
            except queue.Empty:
                continue
    except Exception as e:
        print("❌ record_audio failed:", e)
    finally:
        if stream:
            stream.stop()
            stream.close()
            stream = None
        status_label.config(text="Idle")
