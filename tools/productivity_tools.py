import os
import time
import json
import threading
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import BASE_DIR, USER_NAME

NOTES_FILE = BASE_DIR / "user_notes.json"

class TimerManager:
    """Manages background countdown timers and alerts."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(TimerManager, cls).__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self.timers: Dict[str, Dict[str, Any]] = {}
        self.timer_counter = 0

    def set_timer(self, seconds: int, label: str = "Timer", speaker=None) -> Dict[str, Any]:
        """Sets a timer for the specified number of seconds."""
        if seconds <= 0:
            return {"status": "error", "message": "Timer duration must be greater than 0 seconds."}

        self.timer_counter += 1
        timer_id = f"timer_{self.timer_counter}"
        
        display_label = label if label and label.lower() != "timer" else f"{seconds} seconds"

        def _countdown():
            time.sleep(seconds)
            with self._lock:
                if timer_id in self.timers:
                    del self.timers[timer_id]

            # Trigger alert
            alert_msg = f"Hey {USER_NAME}, your timer for {display_label} is up!"
            print(f"\n[Timer Alert]: {alert_msg}")
            if speaker:
                try:
                    speaker.play_chime("success")
                    time.sleep(0.4)
                    speaker.speak(alert_msg, block=False)
                except Exception as e:
                    print(f"[Timer Alert Error]: {e}")

        t = threading.Thread(target=_countdown, daemon=True)
        with self._lock:
            self.timers[timer_id] = {
                "label": display_label,
                "seconds": seconds,
                "start_time": time.time(),
                "thread": t
            }
        t.start()

        # Human friendly duration string
        if seconds >= 60:
            mins = seconds // 60
            secs = seconds % 60
            dur_str = f"{mins} minute{'s' if mins > 1 else ''}" + (f" and {secs} seconds" if secs else "")
        else:
            dur_str = f"{seconds} seconds"

        return {
            "status": "success",
            "timer_id": timer_id,
            "message": f"Timer set for {dur_str}."
        }

    def list_timers(self) -> Dict[str, Any]:
        with self._lock:
            active = []
            now = time.time()
            for tid, tinfo in self.timers.items():
                remaining = max(0, int(tinfo["seconds"] - (now - tinfo["start_time"])))
                active.append(f"{tinfo['label']} ({remaining}s remaining)")

        if not active:
            return {"status": "success", "message": "You have no active timers right now."}
        return {"status": "success", "message": f"Active timers: {', '.join(active)}."}


class NotesManager:
    """Stores and retrieves personal notes."""
    @staticmethod
    def _load_notes() -> List[Dict[str, str]]:
        if not NOTES_FILE.exists():
            return []
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def _save_notes(notes: List[Dict[str, str]]):
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Notes Save Error]: {e}")

    @classmethod
    def take_note(cls, content: str) -> Dict[str, Any]:
        clean = content.strip()
        if not clean:
            return {"status": "error", "message": "Note content cannot be empty."}

        notes = cls._load_notes()
        timestamp = datetime.datetime.now().strftime("%I:%M %p, %b %d")
        notes.append({"timestamp": timestamp, "text": clean})
        cls._save_notes(notes)

        return {"status": "success", "message": f"I've noted that down: '{clean}'."}

    @classmethod
    def read_notes(cls, limit: int = 5) -> Dict[str, Any]:
        notes = cls._load_notes()
        if not notes:
            return {"status": "success", "message": f"You don't have any saved notes yet, {USER_NAME}."}

        recent = notes[-limit:]
        items = [f"{n['text']} (saved {n['timestamp']})" for n in recent]
        summary = "Here are your recent notes: " + "; ".join(items) + "."
        return {"status": "success", "notes": recent, "message": summary}

    @classmethod
    def clear_notes(cls) -> Dict[str, Any]:
        cls._save_notes([])
        return {"status": "success", "message": f"All notes have been cleared, {USER_NAME}."}
