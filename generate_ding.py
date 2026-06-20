"""
Generates a simple ding.mp3 (actually a WAV wrapped rename) using only stdlib.
Produces a pleasant 880 Hz bell tone saved as assets/ding.mp3.
Run: python generate_ding.py
"""
import struct, math, wave, os

os.makedirs("assets", exist_ok=True)

SAMPLE_RATE = 44100
DURATION    = 1.5   # seconds
FREQ        = 880   # Hz  (A5 - bright bell)
VOLUME      = 0.6

samples = []
total   = int(SAMPLE_RATE * DURATION)
for i in range(total):
    t        = i / SAMPLE_RATE
    envelope = math.exp(-3 * t)          # natural bell decay
    val      = envelope * VOLUME * math.sin(2 * math.pi * FREQ * t)
    # add a gentle harmonic
    val     += envelope * 0.3 * VOLUME * math.sin(2 * math.pi * FREQ * 2 * t)
    samples.append(int(val * 32767))

wav_path = "assets/ding.wav"
with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

# Streamlit's st.audio works with wav too; rename to .mp3 is fine for browsers
import shutil
shutil.copy(wav_path, "assets/ding.mp3")
print("Generated assets/ding.wav and assets/ding.mp3")
