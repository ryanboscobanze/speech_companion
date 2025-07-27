# transcription.py
from faster_whisper import WhisperModel

try:
    whisper_model = WhisperModel("tiny", compute_type="auto")
    print("✅ WhisperModel loaded")
except Exception as e:
    print("❌ Failed to load WhisperModel:", e)
    whisper_model = None

def transcribe_with_whisper(audio_path):
    try:
        segments, _ = whisper_model.transcribe(audio_path)
        return " ".join([seg.text.strip() for seg in segments])
    except Exception as e:
        print("❌ Whisper failed:", e)
        return ""

import threading
import requests
from config import ASSEMBLYAI_API_KEY

def transcribe_with_assemblyai(audio_path):
    if not ASSEMBLYAI_API_KEY:
        print("❌ ASSEMBLYAI_API_KEY is missing")
        return ""
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
    try:
        with open(audio_path, "rb") as f:
            upload_response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, data=f)
        audio_url = upload_response.json()["upload_url"]
        transcript_request = {"audio_url": audio_url, "language_code": "en"}
        response = requests.post("https://api.assemblyai.com/v2/transcript", json=transcript_request, headers=headers)
        transcript_id = response.json()["id"]
        polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        while True:
            polling_response = requests.get(polling_endpoint, headers=headers)
            status = polling_response.json()["status"]
            if status == "completed":
                return polling_response.json()["text"]
            elif status == "error":
                print("❌ AssemblyAI returned an error")
                return ""
            threading.Event().wait(1)
    except Exception as e:
        print("❌ AssemblyAI failed:", e)
        return ""
