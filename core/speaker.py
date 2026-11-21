import io
import math
import wave
import struct
import asyncio
import threading
import pygame
import edge_tts
from typing import Callable, Optional
from config import VOICE_NAME, SPEECH_RATE, SPEECH_PITCH, AGENT_NAME

class BujjiSpeaker:
    def __init__(self, voice: str = VOICE_NAME, rate: str = SPEECH_RATE, pitch: str = SPEECH_PITCH):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self._lock = threading.Lock()
        self._is_speaking = False
        self.on_start_callback: Optional[Callable[[str], None]] = None
        self.on_stop_callback: Optional[Callable[[], None]] = None
        
        # Initialize pygame mixer once
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[Speaker] Warning initializing mixer: {e}")

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def set_callbacks(self, on_start: Optional[Callable[[str], None]] = None, on_stop: Optional[Callable[[], None]] = None):
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop

    def play_chime(self, chime_type: str = "wake"):
        """Generates and plays dynamic futuristic synthesizer chimes."""
        def _play():
            try:
                sample_rate = 44100
                buf = bytearray()
                
                if chime_type == "wake":
                    # Double rising tone: C5 (523.25Hz) -> E5 (659.25Hz)
                    tones = [(523.25, 0.09), (659.25, 0.12)]
                elif chime_type == "success":
                    # Triumphant 3-tone arpeggio: C5 -> E5 -> G5 (783.99Hz)
                    tones = [(523.25, 0.08), (659.25, 0.08), (783.99, 0.18)]
                elif chime_type == "busy":
                    # Soft processing blip
                    tones = [(440.0, 0.05), (554.37, 0.07)]
                else:
                    tones = [(600.0, 0.1)]

                for freq, duration in tones:
                    n_samples = int(sample_rate * duration)
                    for i in range(n_samples):
                        t = i / sample_rate
                        # Envelope fade out to avoid clicks
                        envelope = 1.0 - (i / n_samples)
                        val = int(32767.0 * 0.25 * envelope * math.sin(2.0 * math.pi * freq * t))
                        buf.extend(struct.pack('<h', val))
                        buf.extend(struct.pack('<h', val))  # stereo

                sound = pygame.mixer.Sound(buffer=bytes(buf))
                sound.play()
            except Exception as e:
                print(f"[Chime Error] {e}")

        threading.Thread(target=_play, daemon=True).start()

    async def _synthesize_edge_tts(self, text: str) -> bytes:
        """Synthesizes text to speech using Microsoft Edge Neural Voices."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def speak(self, text: str, block: bool = True):
        """Speaks the given text using high quality neural voice."""
        if not text or not text.strip():
            return

        clean_text = text.strip()
        print(f"[{AGENT_NAME}]: {clean_text}")

        with self._lock:
            self._is_speaking = True
            if self.on_start_callback:
                try:
                    self.on_start_callback(clean_text)
                except Exception:
                    pass

            try:
                # Synthesize audio in async loop
                loop = asyncio.new_event_loop()
                audio_data = loop.run_until_complete(self._synthesize_edge_tts(clean_text))
                loop.close()

                if audio_data:
                    sound_file = io.BytesIO(audio_data)
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()

                    if block:
                        while pygame.mixer.music.get_busy():
                            pygame.time.Clock().tick(20)
            except Exception as e:
                print(f"[Speaker Error] {e}")
                # Offline SAPI fallback
                self._fallback_sapi(clean_text)
            finally:
                self._is_speaking = False
                if self.on_stop_callback:
                    try:
                        self.on_stop_callback()
                    except Exception:
                        pass

    def speak_async(self, text: str, on_done: Optional[Callable[[], None]] = None):
        """Asynchronous non-blocking speech."""
        def run():
            self.speak(text, block=True)
            if on_done:
                on_done()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    def _fallback_sapi(self, text: str):
        """Fallback to Windows SAPI via pywin32 if edge-tts encounters an issue."""
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except Exception as e:
            print(f"[SAPI Fallback Error] {e}")

    def stop(self):
        """Stops any currently playing audio."""
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass
        self._is_speaking = False
        if self.on_stop_callback:
            try:
                self.on_stop_callback()
            except Exception:
                pass
