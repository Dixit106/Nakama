import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro 

MODEL_PATH = "models/kokoro-v1.0.onnx"
VOICES_PATH = "models/voices-v1.0.bin"

#we load voice model once so replies stay fassst
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

def speak(text: str, voice: str = "af_bella", speed: float = 1.0, on_start=None, on_mouth=None):
    samples, sample_rate = kokoro.create(
        text,
        voice=voice,
        speed=speed,
        lang="en-us"
    )

    if on_start:
        on_start()

    chunk_size = int(sample_rate * 0.05) #50ms audio slices
    with sd.OutputStream(samplerate=sample_rate, channels=1, dtype="float32") as stream:
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i + chunk_size]
            rms = float(np.sqrt(np.mean(chunk ** 2)))

            if on_mouth:
                if rms < 0.015:
                    on_mouth(0) #closesd
                elif rms < 0.06:
                    on_mouth(1) #Halfopen
                else:
                    on_mouth(2) #Fullopen

            stream.write(chunk.reshape(-1, 1))

        if on_mouth:
            on_mouth(0)