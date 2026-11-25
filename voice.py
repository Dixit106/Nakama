import sounddevice as sd
from kokoro_onnx import Kokoro 

MODEL_PATH = "models/kokoro-v1.0.onnx"
VOICES_PATH = "models/voices-v1.0.bin"

#we load voice model once so replies stay fassst
kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

def speak(text: str, voice: str = "af_bella", speed: float = 1.0):
    samples, sample_rate = kokoro.create(
        text,
        voice=voice,
        speed=speed,
        lang="en-us"
    )
    sd.play(samples, sample_rate)
    sd.wait()

if __name__ == "__main__":
    speak("Yo! My name is Magari, I am an A.I. How do I sound?")