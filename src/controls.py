# controls.py
import threading
import sounddevice as sd

def list_mics(mic_menu, mic_var):
    try:
        devices = sd.query_devices()
        mics = [f"{i}: {d['name']}" for i, d in enumerate(devices) if d["max_input_channels"] > 0]
        mic_menu["values"] = mics
        if mics:
            mic_menu.current(0)
    except Exception as e:
        print("❌ Failed to list microphones:", e)

def toggle_recording(
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
):
    if not is_recording_state[0]:
        try:
            device_index = int(mic_var.get().split(":")[0])
            start_button.config(text="Stop", bg="red")
            mic_menu.config(state="disabled")
            engine_menu.config(state="disabled")
            is_recording_state[0] = True
            threading.Thread(
                target=record_audio,
                args=(device_index, stop_event, audio_queue, status_label,
                      process_audio_chunk, engine_var, scrollable_frame, header,
                      row_widgets, canvas, root),
                daemon=True
            ).start()
        except Exception as e:
            print("❌ Failed to start recording:", e)
    else:
        stop_event.set()
        start_button.config(text="Start")
        start_button.config(bg="blue" if engine_var.get() == "AssemblyAI" else "green")
        mic_menu.config(state="readonly")
        engine_menu.config(state="readonly")
        status_label.config(text="Idle")
        is_recording_state[0] = False
