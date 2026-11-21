import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from config import ANTIGRAVITY_BRAIN_DIR, USER_NAME

class TaskMonitor:
    """
    Monitors background agent tasks, specifically watching Antigravity
    workspace generation and session progress, notifying the user via voice
    as soon as their project/application has finished building.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskMonitor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, speaker=None):
        if self._initialized:
            if speaker and not self.speaker:
                self.speaker = speaker
            return
            
        self.speaker = speaker
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._initialized = True

    def register_task(
        self,
        task_id: str,
        name: str,
        watch_dir: Optional[str] = None,
        custom_message: Optional[str] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        settle_timeout: int = 6,
        max_duration: int = 300
    ):
        """
        Registers a new background task to monitor.
        settle_timeout: Seconds of inactivity after files start being generated to consider build complete.
        """
        watch_path = Path(watch_dir) if watch_dir else None
        initial_files = set()
        if watch_path and watch_path.exists():
            try:
                initial_files = set(str(f) for f in watch_path.rglob("*") if f.is_file())
            except Exception:
                pass

        task_data = {
            "name": name,
            "watch_dir": watch_path,
            "initial_files": initial_files,
            "custom_message": custom_message,
            "on_complete": on_complete,
            "settle_timeout": settle_timeout,
            "max_duration": max_duration,
            "start_time": time.time(),
            "last_change_time": 0,
            "files_detected": False,
            "status": "running"
        }

        with self._lock:
            self.active_tasks[task_id] = task_data

        thread = threading.Thread(
            target=self._monitor_loop,
            args=(task_id,),
            daemon=True
        )
        thread.start()
        print(f"[TaskMonitor] Registered task '{name}' (ID: {task_id}) watching: {watch_dir}")

    def _monitor_loop(self, task_id: str):
        """Watches for file generation and settling."""
        time.sleep(1)  # Give Antigravity time to start
        
        while True:
            time.sleep(1.0)
            with self._lock:
                task = self.active_tasks.get(task_id)
                if not task or task["status"] != "running":
                    break

            watch_dir = task["watch_dir"]
            now = time.time()

            # Timeout safeguard
            if now - task["start_time"] > task["max_duration"]:
                self._complete_task(task_id, reason="timeout")
                break

            # Check directory changes
            if watch_dir and watch_dir.exists():
                try:
                    current_files = set(str(f) for f in watch_dir.rglob("*") if f.is_file())
                    new_files = current_files - task["initial_files"]
                    
                    if new_files:
                        task["files_detected"] = True
                        task["last_change_time"] = now
                        task["initial_files"] = current_files
                        # If files have been detected and no new files for settle_timeout seconds:
                    elif task["files_detected"] and (now - task["last_change_time"] >= task["settle_timeout"]):
                        self._complete_task(task_id, reason="settled")
                        break
                except Exception as e:
                    print(f"[TaskMonitor Error] {e}")

            # Also check latest session transcript in Antigravity brain
            if self._check_antigravity_brain_done(task["start_time"]):
                self._complete_task(task_id, reason="brain_done")
                break

    def _check_antigravity_brain_done(self, start_time: float) -> bool:
        """Checks if a new transcript entry has completed in the brain dir."""
        if not ANTIGRAVITY_BRAIN_DIR.exists():
            return False
        try:
            # Look at directories created after start_time
            for folder in ANTIGRAVITY_BRAIN_DIR.iterdir():
                if folder.is_dir():
                    stat = folder.stat()
                    if stat.st_mtime >= start_time - 5:
                        transcript = folder / ".system_generated" / "logs" / "transcript.jsonl"
                        if transcript.exists():
                            t_stat = transcript.stat()
                            # If updated recently and quiet for 5 seconds
                            if time.time() - t_stat.st_mtime > 5 and t_stat.st_mtime > start_time:
                                return True
        except Exception:
            pass
        return False

    def _complete_task(self, task_id: str, reason: str = ""):
        with self._lock:
            task = self.active_tasks.get(task_id)
            if not task or task["status"] == "completed":
                return
            task["status"] = "completed"

        name = task["name"]
        print(f"[TaskMonitor] Task '{name}' completed! (Reason: {reason})")

        # Notification message
        msg = task["custom_message"] or f"Hey {USER_NAME}, your application got ready! Antigravity has completed building {name}."

        if self.speaker:
            self.speaker.play_chime("success")
            time.sleep(0.5)
            self.speaker.speak_async(msg)

        if task["on_complete"]:
            try:
                task["on_complete"](msg)
            except Exception as e:
                print(f"[TaskMonitor Callback Error] {e}")

    def get_status_summary(self) -> str:
        """Returns a human-readable status of ongoing tasks."""
        with self._lock:
            running = [t["name"] for t in self.active_tasks.values() if t["status"] == "running"]
            completed = [t["name"] for t in self.active_tasks.values() if t["status"] == "completed"]

        if not running and not completed:
            return "No background tasks have been started yet."
        
        parts = []
        if running:
            parts.append(f"Currently working on: {', '.join(running)}.")
        if completed:
            parts.append(f"Completed tasks: {', '.join(completed[-3:])}.")
        return " ".join(parts)
