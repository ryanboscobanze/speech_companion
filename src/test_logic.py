import sounddevice as sd

def test_audio():
    def callback(indata, frames, time_info, status):
        print("🎧 Listening...", len(indata))
    with sd.InputStream(callback=callback, channels=1, samplerate=16000):
        input("🎤 Press Enter to stop...")

test_audio()
