import os
import re
import uuid
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from config import ANTIGRAVITY_CMD, ANTIGRAVITY_EXE, PROJECTS_DIR, USER_NAME
from core.task_monitor import TaskMonitor

def sanitize_folder_name(name: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', name).strip().replace(' ', '_')
    return clean[:30] if clean else "New_Project"

def execute_antigravity_task(prompt: str, project_name: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    """
    Opens Antigravity IDE in a NEW separate window (without closing the user's current project),
    sets up the workspace, sends the prompt to the Antigravity Agent, and sets up
    a background task monitor to notify the user via voice once ready.
    """
    clean_prompt = prompt.strip()
    # Strip any redundant prefix like "it to", "to", "build build"
    clean_prompt = re.sub(r"^(?:it\s+to|to)\s+", "", clean_prompt, flags=re.I).strip()
    clean_prompt = re.sub(r"^(?:build\s+)+build\s+", "build ", clean_prompt, flags=re.I).strip()

    if not project_name:
        # Infer a clean project name from prompt
        match = re.search(r"(?:build|create|make|develop)\s+(?:a|an)?\s*([a-zA-Z0-9_\- ]+?)(?:\s+in|\s+using|\s+with|$)", clean_prompt, re.I)
        if match:
            project_name = sanitize_folder_name(match.group(1))
        else:
            project_name = sanitize_folder_name(clean_prompt)
        
        if not project_name or len(project_name) < 3:
            project_name = f"Project_{uuid.uuid4().hex[:6]}"

    # Setup project directory
    target_dir = PROJECTS_DIR / project_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path_str = str(target_dir.resolve())

    print(f"[AntigravityTool] Initiating project '{project_name}' at {target_path_str}")

    if dry_run:
        return {
            "status": "dry_run_success",
            "project_name": project_name,
            "workspace_path": target_path_str,
            "task_id": "test_id",
            "spoken_reply": f"Antigravity simulated launch for {prompt}."
        }

    # Check Antigravity executable / cmd
    cmd_path = ANTIGRAVITY_CMD if Path(ANTIGRAVITY_CMD).exists() else None
    exe_path = ANTIGRAVITY_EXE if Path(ANTIGRAVITY_EXE).exists() else None

    launched = False

    # 1. Open the workspace folder in Antigravity in a NEW window (NEVER reuse window)
    if cmd_path:
        try:
            subprocess.Popen(
                [cmd_path, "--new-window", target_path_str],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            launched = True
        except Exception as e:
            print(f"[AntigravityTool Workspace Error] {e}")

    # 2. Trigger the agent chat prompt in that new window
    if cmd_path:
        try:
            subprocess.Popen(
                [cmd_path, "chat", "--new-window", "-m", "agent", prompt],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            launched = True
        except Exception as e:
            print(f"[AntigravityTool Chat Error] {e}")
    elif exe_path:
        try:
            subprocess.Popen([exe_path, target_path_str])
            launched = True
        except Exception as e:
            print(f"[AntigravityTool EXE Error] {e}")

    # 3. Register with TaskMonitor
    task_id = f"ag_{uuid.uuid4().hex[:8]}"
    monitor = TaskMonitor()
    completion_msg = f"Hey {USER_NAME}, your application got ready! Antigravity has completed building your {project_name.replace('_', ' ')}."
    
    monitor.register_task(
        task_id=task_id,
        name=project_name.replace('_', ' '),
        watch_dir=target_path_str,
        custom_message=completion_msg
    )

    return {
        "status": "started" if launched else "fallback_started",
        "project_name": project_name,
        "workspace_path": target_path_str,
        "task_id": task_id,
        "spoken_reply": f"Opening Antigravity now and instructing it to {prompt}. I'll monitor the progress and speak up the moment your application is ready!"
    }
