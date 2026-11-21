import os
import re
import sys
import time
import psutil
import datetime
import requests
import webbrowser
import subprocess
import pyautogui
import pyperclip
pyautogui.FAILSAFE = False
from pathlib import Path
from typing import Dict, Any, Optional

APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "firefox": "firefox",
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "mspaint": "mspaint",
    "spotify": "spotify",
    "vs code": "code",
    "vscode": "code",
    "code": "code",
    "file explorer": "explorer",
    "explorer": "explorer",
    "my computer": "explorer",
    "terminal": "wt",
    "cmd": "cmd",
    "powershell": "powershell",
    "task manager": "taskmgr",
    "settings": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "whatsapp": "whatsapp",
    "discord": "discord",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt"
}

PROCESS_MAP = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "spotify": "spotify.exe",
    "vs code": "Code.exe",
    "vscode": "Code.exe",
    "code": "Code.exe",
    "task manager": "Taskmgr.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "WindowsTerminal.exe",
    "discord": "Discord.exe",
    "whatsapp": "WhatsApp.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE"
}

POPULAR_WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
    "linkedin": "https://www.linkedin.com",
    "chatgpt": "https://chatgpt.com",
    "netflix": "https://www.netflix.com",
    "amazon": "https://www.amazon.com",
    "wikipedia": "https://www.wikipedia.org",
    "stack overflow": "https://stackoverflow.com",
    "claude": "https://claude.ai",
    "instagram": "https://www.instagram.com",
    "telegram": "https://web.telegram.org",
    "whatsapp": "https://web.whatsapp.com",
    "spotify": "https://open.spotify.com",
    "google meet": "https://meet.google.com/new",
    "meet": "https://meet.google.com/new",
    "google maps": "https://maps.google.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
    "google calendar": "https://calendar.google.com",
    "canva": "https://www.canva.com",
    "notion": "https://www.notion.so"
}

# Real-world fallback for mobile/laptop daily essential apps
APP_WEB_FALLBACK = {
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "spotify": "https://open.spotify.com",
    "instagram": "https://www.instagram.com",
    "insta": "https://www.instagram.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "discord": "https://discord.com/app",
    "zoom": "https://app.zoom.us/wc",
    "slack": "https://app.slack.com/client",
    "teams": "https://teams.microsoft.com",
    "microsoft teams": "https://teams.microsoft.com",
    "meet": "https://meet.google.com/new",
    "google meet": "https://meet.google.com/new",
    "gmail": "https://mail.google.com",
    "mail": "https://mail.google.com",
    "email": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "youtube music": "https://music.youtube.com",
    "netflix": "https://www.netflix.com",
    "prime video": "https://www.primevideo.com",
    "amazon prime": "https://www.primevideo.com",
    "hotstar": "https://www.hotstar.com",
    "disney hotstar": "https://www.hotstar.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "facebook": "https://www.facebook.com",
    "messenger": "https://www.messenger.com",
    "pinterest": "https://www.pinterest.com",
    "twitch": "https://www.twitch.tv",
    "github": "https://github.com",
    "calendar": "https://calendar.google.com",
    "google calendar": "https://calendar.google.com",
    "maps": "https://maps.google.com",
    "google maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
    "google drive": "https://drive.google.com",
    "docs": "https://docs.google.com",
    "sheets": "https://sheets.google.com",
    "canva": "https://www.canva.com",
    "notion": "https://www.notion.so"
}

def open_application(app_name: str) -> Dict[str, Any]:
    """
    Intelligently opens an application on Windows.
    If the desktop app is not installed or fails, seamlessly falls back to the
    official Web App version in the user's browser.
    NEVER blindly refuses or fails with a dead end!
    """
    clean_name = app_name.lower().strip()
    
    # WhatsApp special handler
    if "whatsapp" in clean_name:
        from tools.whatsapp_tool import open_whatsapp
        return open_whatsapp()

    target_cmd = APP_MAP.get(clean_name, clean_name)

    # 1. Try launching local desktop app
    try:
        if target_cmd.startswith("ms-") or target_cmd.startswith("microsoft."):
            subprocess.Popen(f"start {target_cmd}", shell=True)
            return {"status": "success", "mode": "app", "message": f"Opened {app_name} for you."}

        if target_cmd in ["calc", "mspaint", "notepad", "explorer", "cmd", "taskmgr", "wt"]:
            subprocess.Popen(target_cmd, shell=True)
            return {"status": "success", "mode": "app", "message": f"Opened {app_name}."}
        
        # Test if executable or path exists
        import shutil
        found_bin = shutil.which(target_cmd)
        if found_bin:
            subprocess.Popen(target_cmd, shell=True)
            return {"status": "success", "mode": "app", "message": f"Opened {app_name}."}

        # Try os.startfile for Windows registered apps
        try:
            os.startfile(target_cmd)
            return {"status": "success", "mode": "app", "message": f"Opened {app_name}."}
        except Exception:
            pass

    except Exception:
        pass

    # 2. Seamless Real-World Web Fallback: Never say "there is no app"
    if clean_name in APP_WEB_FALLBACK:
        url = APP_WEB_FALLBACK[clean_name]
        webbrowser.open(url)
        return {
            "status": "success",
            "mode": "web",
            "url": url,
            "message": f"Opening {app_name.title()} Web in your browser for you!"
        }

    # Partial matches in APP_WEB_FALLBACK
    for k, url in APP_WEB_FALLBACK.items():
        if k in clean_name or clean_name in k:
            webbrowser.open(url)
            return {
                "status": "success",
                "mode": "web",
                "url": url,
                "message": f"Opening {k.title()} Web in your browser for you!"
            }

    # 3. Last fallback: Open Google search for the service
    search_url = f"https://www.google.com/search?q={clean_name.replace(' ', '+')}"
    webbrowser.open(search_url)
    return {
        "status": "success",
        "mode": "search",
        "url": search_url,
        "message": f"Opening {app_name} online in your browser!"
    }

def close_application(app_name: str) -> Dict[str, Any]:
    """Closes an active desktop application."""
    clean_name = app_name.lower().strip()
    proc_name = PROCESS_MAP.get(clean_name, f"{clean_name}.exe")

    closed_count = 0
    try:
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name and (name.lower() == proc_name.lower() or clean_name in name.lower()):
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if closed_count > 0:
            return {"status": "success", "message": f"Closed {app_name}."}
        
        # Fallback to taskkill
        res = subprocess.run(f"taskkill /f /im {proc_name}", shell=True, capture_output=True, text=True)
        if "SUCCESS" in res.stdout or res.returncode == 0:
            return {"status": "success", "message": f"Closed {app_name}."}
        else:
            return {"status": "not_running", "message": f"{app_name} is not currently running."}
    except Exception as e:
        return {"status": "error", "message": f"Could not close {app_name}: {str(e)}"}

def open_website(site_query: str) -> Dict[str, Any]:
    """Opens a website in the default browser."""
    clean = site_query.lower().strip().replace("open ", "").replace("go to ", "").replace("website ", "")
    
    # Check popular websites
    for key, url in POPULAR_WEBSITES.items():
        if key in clean:
            webbrowser.open(url)
            return {"status": "success", "url": url, "message": f"Opening {key.capitalize()}."}

    # If it looks like a URL
    if clean.startswith("http://") or clean.startswith("https://"):
        webbrowser.open(clean)
        return {"status": "success", "url": clean, "message": f"Opening {clean}."}
    elif "." in clean and not " " in clean:
        url = f"https://{clean}"
        webbrowser.open(url)
        return {"status": "success", "url": url, "message": f"Opening {clean}."}
    
    # Otherwise Google search
    return search_web(clean)

def search_web(query: str) -> Dict[str, Any]:
    """Performs a web search in the default browser."""
    clean = re.sub(r"^(?:search|google|look up|search for)\s+", "", query, flags=re.I).strip()
    url = f"https://www.google.com/search?q={clean.replace(' ', '+')}"
    webbrowser.open(url)
    return {"status": "success", "message": f"Searching Google for {clean}."}

def play_youtube(query: str) -> Dict[str, Any]:
    """Opens YouTube and plays or searches for the given video."""
    clean = re.sub(r"^(?:play|listen to)\s+", "", query, flags=re.I).replace("on youtube", "").strip()
    url = f"https://www.youtube.com/results?search_query={clean.replace(' ', '+')}"
    webbrowser.open(url)
    return {"status": "success", "message": f"Playing {clean} on YouTube."}

def lock_screen() -> Dict[str, Any]:
    """Locks the Windows PC immediately."""
    try:
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return {"status": "success", "message": "Screen locked."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to lock screen: {str(e)}"}

def set_brightness(level: int) -> Dict[str, Any]:
    """Adjusts display brightness (0 - 100%)."""
    val = max(0, min(100, int(level)))
    try:
        ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})"
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=3)
        return {"status": "success", "message": f"Brightness set to {val}%."}
    except Exception as e:
        return {"status": "error", "message": f"Could not adjust brightness: {str(e)}"}

def take_screenshot() -> Dict[str, Any]:
    """Captures a screenshot and saves it to user's Pictures/Screenshots folder."""
    try:
        pictures_dir = Path.home() / "Pictures" / "Screenshots"
        pictures_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = pictures_dir / f"Screenshot_{timestamp}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return {"status": "success", "message": "Screenshot captured and saved to your Screenshots folder.", "path": str(filepath)}
    except Exception as e:
        return {"status": "error", "message": f"Failed to take screenshot: {str(e)}"}

def control_volume(action: str) -> Dict[str, Any]:
    """Adjusts Windows system volume."""
    act = action.lower()
    try:
        if "up" in act or "increase" in act:
            for _ in range(5):
                pyautogui.press("volumeup")
            return {"status": "success", "message": "Volume increased."}
        elif "down" in act or "decrease" in act or "lower" in act:
            for _ in range(5):
                pyautogui.press("volumedown")
            return {"status": "success", "message": "Volume decreased."}
        elif "mute" in act or "unmute" in act or "toggle" in act:
            pyautogui.press("volumemute")
            return {"status": "success", "message": "Volume toggled."}
    except Exception as e:
        return {"status": "error", "message": f"Volume control failed: {str(e)}"}
    return {"status": "unknown", "message": "Volume action not recognized."}

def get_time_and_date() -> Dict[str, Any]:
    """Returns the current date and time."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    return {
        "status": "success",
        "time": time_str,
        "date": date_str,
        "message": f"It is currently {time_str} on {date_str}."
    }

def get_system_stats() -> Dict[str, Any]:
    """Returns CPU, RAM, and Battery percentages."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    if battery:
        battery_info = f"Battery is at {battery.percent}% {'and charging' if battery.power_plugged else ''}."
    else:
        battery_info = "Connected to AC power."

    return {
        "status": "success",
        "cpu": cpu,
        "memory": memory,
        "message": f"CPU is at {cpu}%, Memory is at {memory}%. {battery_info}"
    }

def get_weather(location: Optional[str] = None) -> Dict[str, Any]:
    """Fetches live weather report using wttr.in."""
    loc_query = location.strip() if location else ""
    url = f"https://wttr.in/{loc_query.replace(' ', '+')}?format=%C,+%t+(feels+like+%f),+humidity+%h,+wind+%w"
    try:
        resp = requests.get(url, timeout=4, headers={"User-Agent": "BujjiAssistant/1.0"})
        if resp.status_code == 200 and len(resp.text.strip()) > 3:
            weather_text = resp.text.strip()
            place_label = f"in {location.title()}" if location else "outside"
            msg = f"The weather {place_label} is currently {weather_text}."
            return {"status": "success", "weather": weather_text, "message": msg}
    except Exception as e:
        pass
    
    return {"status": "fallback", "message": "I couldn't fetch live weather right now. Please check your internet connection."}

def get_wikipedia_summary(topic: str) -> Dict[str, Any]:
    """Fetches a concise factual summary from Wikipedia."""
    clean_topic = re.sub(r"^(?:who is|what is|tell me about|explain)\s+", "", topic, flags=re.I).strip()
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_topic.replace(' ', '_')}"
    try:
        resp = requests.get(url, timeout=4, headers={"User-Agent": "BujjiAssistant/1.0"})
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract", "")
            if extract:
                # Take first 2 sentences for concise voice delivery
                sentences = re.split(r'(?<=[.!?]) +', extract)
                concise = " ".join(sentences[:2])
                return {"status": "success", "summary": concise, "message": concise}
    except Exception:
        pass
    
    # Fallback to search
    return search_web(topic)

def calculate_math(expression: str) -> Dict[str, Any]:
    """Calculates simple math expressions safely."""
    # Handle percentage: "what is 20 percent of 150"
    pct_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s+of\s+(\d+(?:\.\d+)?)", expression, re.I)
    if pct_match:
        pct = float(pct_match.group(1))
        total = float(pct_match.group(2))
        res = (pct / 100.0) * total
        return {"status": "success", "result": res, "message": f"{pct}% of {total} is {res:g}."}

    # Clean arithmetic symbols
    clean = expression.lower()
    clean = re.sub(r"^(?:what is|calculate|compute)\s+", "", clean).strip(" ?")
    clean = clean.replace("times", "*").replace("multiplied by", "*").replace("x", "*")
    clean = clean.replace("divided by", "/").replace("over", "/")
    clean = clean.replace("plus", "+").replace("minus", "-")

    # Only allow safe mathematical characters
    if not re.match(r"^[\d\s\+\-\*\/\(\)\.\^%]+$", clean):
        return {"status": "error", "message": f"I couldn't parse the math expression in '{expression}'."}

    try:
        clean = clean.replace("^", "**")
        result = eval(clean, {"__builtins__": {}}, {})
        return {"status": "success", "result": result, "message": f"The answer is {result:g}."}
    except Exception:
        return {"status": "error", "message": f"I wasn't able to calculate that."}

def get_clipboard_content() -> Dict[str, Any]:
    """Returns the text currently stored in the clipboard."""
    try:
        content = pyperclip.paste()
        if content and content.strip():
            preview = content.strip()[:150]
            return {"status": "success", "clipboard": content, "message": f"Your clipboard contains: '{preview}'."}
        else:
            return {"status": "empty", "message": "Your clipboard is currently empty."}
    except Exception as e:
        return {"status": "error", "message": f"Could not read clipboard: {str(e)}"}

def copy_to_clipboard(text: str) -> Dict[str, Any]:
    """Copies the provided text to the Windows clipboard."""
    try:
        pyperclip.copy(text)
        return {"status": "success", "message": f"Copied to clipboard: '{text[:50]}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to copy to clipboard: {str(e)}"}
