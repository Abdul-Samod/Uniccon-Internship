import os
import pyaudio
import wave
import numpy as np
import noisereduce as nr

# ---------- CONFIGURATION ----------
SAVE_DIR = "recordings"
THRESHOLD = 500         # sensitivity: lower = more sensitive
SILENCE_LIMIT = 1.5       # seconds of silence before stopping
PREV_AUDIO = 0.5        # seconds to keep before speech start
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
AMPLIFY_FACTOR = 1.0    # 🔊 volume boost multiplier (1.0 = normal)
# ----------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

def get_next_sequence():
    """Find the next sequence number for saving."""
    existing = [f for f in os.listdir(SAVE_DIR) if f.endswith(".wav")]
    numbers = [int(os.path.splitext(f)[0]) for f in existing if os.path.splitext(f)[0].isdigit()]
    return max(numbers, default=0) + 1

def is_silent(data_chunk):
    """Check if chunk is below threshold."""
    audio_data = np.frombuffer(data_chunk, dtype=np.int16)
    return np.abs(audio_data).mean() < THRESHOLD

def record_to_file(path, data):
    """Save data as WAV file."""
    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data))
    wf.close()

def clean_and_amplify(audio_frames):
    """Apply noise reduction, normalization, and amplification."""
    # Combine all chunks into one numpy array
    audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16)
    
    # 🧹 Noise reduction
    reduced = nr.reduce_noise(y=audio_data, sr=RATE)

    # 🔊 Normalize to full volume range
    max_val = np.max(np.abs(reduced))
    if max_val > 0:
        reduced = reduced / max_val * 32767

    # 🔉 Amplify (controlled)
    amplified = reduced * AMPLIFY_FACTOR
    amplified = np.clip(amplified, -32768, 32767)  # avoid distortion

    return (amplified.astype(np.int16)).tobytes()

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

print("🎙 Listening... Speak to start recording.")

audio_buffer = []
recording = False
silence_counter = 0
pre_buffer = []
sequence = get_next_sequence()

try:
    while True:
        chunk = stream.read(CHUNK)
        pre_buffer.append(chunk)
        if len(pre_buffer) > int(PREV_AUDIO * RATE / CHUNK):
            pre_buffer.pop(0)

        if not recording:
            if not is_silent(chunk):
                recording = True
                audio_buffer = pre_buffer.copy()
                print(f"▶ Recording {sequence}.wav...")
        else:
            audio_buffer.append(chunk)
            if is_silent(chunk):
                silence_counter += CHUNK / RATE
                if silence_counter > SILENCE_LIMIT:
                    print(f"⏹ Stopping recording {sequence}.wav")
                    print("🔧 Cleaning and amplifying audio...")

                    clean_data = clean_and_amplify(audio_buffer)
                    filepath = os.path.join(SAVE_DIR, f"{sequence}.wav")

                    wf = wave.open(filepath, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(clean_data)
                    wf.close()

                    print(f"💾 Saved clean, louder audio: {filepath}")
                    sequence += 1
                    recording = False
                    silence_counter = 0
                    audio_buffer = []
                    pre_buffer = []
                    print("🎙 Waiting for next speech...")
            else:
                silence_counter = 0

except KeyboardInterrupt:
    print("\n🛑 Exiting gracefully...")
    stream.stop_stream()
    stream.close()
    p.terminate()