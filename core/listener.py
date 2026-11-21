import re
import time
import speech_recognition as sr
from typing import Optional, Tuple, Callable
from config import WAKE_WORDS, ENERGY_THRESHOLD, PAUSE_THRESHOLD, TIMEOUT_SECONDS, PHRASE_TIME_LIMIT

class BujjiListener:
    def __init__(self, energy_threshold: int = ENERGY_THRESHOLD, pause_threshold: float = PAUSE_THRESHOLD):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.non_speaking_duration = 0.5
        self.microphone = sr.Microphone()
        
        self.is_listening = False
        self.on_state_change: Optional[Callable[[str], None]] = None

        # Build comprehensive regex for all wake expressions:
        # hey bujji, bujji, bujjiiii, hey bangaram, bangaram, hii bujji, hey jarvis, hiii jaravis, etc.
        self.wake_regex = re.compile(
            r"^(?:hey\s+|hi+\s+|hello\s+)?(?:bujji+|bangaram|jarvis|jaravis|siri|alexa)[\s,.]*(.*)$",
            re.IGNORECASE
        )
        # Search pattern anywhere in string
        self.wake_search = re.compile(
            r"\b(?:hey\s+|hi+\s+|hello\s+)?(?:bujji+|bangaram|jarvis|jaravis|siri|alexa)\b",
            re.IGNORECASE
        )

    def calibrate(self, duration: int = 1):
        """Calibrate microphone for ambient background noise."""
        print("[Listener] Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        print(f"[Listener] Calibration complete. Energy threshold set to {self.recognizer.energy_threshold:.1f}")

    def _notify(self, state: str):
        if self.on_state_change:
            try:
                self.on_state_change(state)
            except Exception:
                pass

    def listen_audio(self, timeout: Optional[int] = TIMEOUT_SECONDS, phrase_time_limit: int = PHRASE_TIME_LIMIT) -> Optional[str]:
        """Listens from the microphone and converts speech to text."""
        self._notify("listening")
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            self._notify("processing")
            # Convert to text using Google Speech Recognition (free, fast, reliable)
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[Listener Network Error] {e}")
            return None
        except Exception as e:
            print(f"[Listener Error] {e}")
            return None
        finally:
            self._notify("idle")

    def check_wake_word(self, text: str) -> Tuple[bool, str]:
        """
        Checks if the recognized text contains a wake word.
        Returns (is_wake_word_triggered, remaining_command)
        """
        if not text:
            return False, ""
        
        clean = text.strip().lower()
        
        # Check direct matches with regex
        match = self.wake_regex.match(clean)
        if match:
            remaining = match.group(1).strip()
            return True, remaining

        # Check search anywhere in sentence
        search_match = self.wake_search.search(clean)
        if search_match:
            end_pos = search_match.end()
            remaining = clean[end_pos:].strip(" ,.")
            return True, remaining
        
        # Check substring match
        for w in WAKE_WORDS:
            if clean.startswith(w):
                remaining = clean[len(w):].strip(" ,.")
                return True, remaining
            if w in clean:
                idx = clean.find(w)
                remaining = clean[idx + len(w):].strip(" ,.")
                return True, remaining

        return False, ""
