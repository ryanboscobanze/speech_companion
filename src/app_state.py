# app_state.py
import threading
import queue
from collections import deque

# Recording state
is_recording = False
stop_event = threading.Event()
audio_queue = queue.Queue()
stream = None

# GUI widgets
row_widgets = []

# Context
recent_utterances = deque(maxlen=2)
max_context_limit = 5
