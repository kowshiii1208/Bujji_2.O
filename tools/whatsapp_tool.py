"""
WhatsApp Automation Tool for Bujji AI Assistant.
Supports both WhatsApp Desktop (UWP) and WhatsApp Web.
Handles messaging, audio/video calls, and viewing status updates.
"""
import os
import re
import time
import webbrowser
import subprocess
import pyautogui
import pyperclip
from typing import Dict, Any, Optional

pyautogui.FAILSAFE = False

WHATSAPP_WEB_URL = "https://web.whatsapp.com"
WHATSAPP_STATUS_URL = "https://web.whatsapp.com"

def is_whatsapp_desktop_installed() -> bool:
    """Checks if WhatsApp Desktop (UWP or standard) is available on the machine."""
    try:
        # Check via PowerShell protocol handler or process check
        check_cmd = "(Get-ItemProperty 'HKCU:\\Software\\Classes\\whatsapp' -ErrorAction SilentlyContinue) -or (Get-ItemProperty 'HKCR:\\whatsapp' -ErrorAction SilentlyContinue)"
        res = subprocess.run(["powershell", "-NoProfile", "-Command", check_cmd], capture_output=True, text=True, timeout=3)
        if "True" in res.stdout:
            return True
        
        # Check standard Windows Store Package
        pkg_cmd = "Get-AppxPackage -Name *WhatsApp* -ErrorAction SilentlyContinue"
        pkg_res = subprocess.run(["powershell", "-NoProfile", "-Command", pkg_cmd], capture_output=True, text=True, timeout=3)
        return bool(pkg_res.stdout.strip())
    except Exception:
        return False

def open_whatsapp(section: str = "chats", prefer_web: bool = False) -> Dict[str, Any]:
    """
    Intelligently opens WhatsApp.
    If desktop app is available and not prefer_web, opens desktop app.
    Otherwise, seamlessly opens WhatsApp Web in the user's default browser.
    Never fails with a dead end!
    """
    section_lower = section.lower().strip()
    desktop_available = is_whatsapp_desktop_installed()

    if desktop_available and not prefer_web:
        try:
            subprocess.Popen(["powershell", "-NoProfile", "-Command", "Start-Process 'whatsapp:'"])
            time.sleep(1.2)
            
            if section_lower in ["status", "stories"]:
                # Shortcut in WhatsApp desktop for Status or tab navigation
                pyautogui.hotkey('ctrl', 'alt', 's')
                return {
                    "status": "success",
                    "mode": "desktop",
                    "section": "status",
                    "message": "Opened WhatsApp Status for you! You can view the latest updates from your contacts."
                }
            elif section_lower in ["calls", "call"]:
                return {
                    "status": "success",
                    "mode": "desktop",
                    "section": "calls",
                    "message": "Opened WhatsApp Calls. Who would you like to call?"
                }
            return {
                "status": "success",
                "mode": "desktop",
                "section": "chats",
                "message": "Opened WhatsApp Desktop. Who would you like to message or call?"
            }
        except Exception:
            # Fall back to web immediately if desktop launch encounters any issue
            pass

    # Seamless WhatsApp Web Fallback
    target_url = WHATSAPP_WEB_URL
    webbrowser.open(target_url)
    
    if section_lower in ["status", "stories"]:
        return {
            "status": "success",
            "mode": "web",
            "section": "status",
            "message": "Opened WhatsApp Web in your browser! Head to the Status circle icon to view all recent updates."
        }
    elif section_lower in ["calls", "call"]:
        return {
            "status": "success",
            "mode": "web",
            "section": "calls",
            "message": "Opened WhatsApp Web in your browser! Select any contact to start an audio or video call."
        }
    
    return {
        "status": "success",
        "mode": "web",
        "section": "chats",
        "message": "Opened WhatsApp Web in your browser! Who would you like to connect with?"
    }

def view_whatsapp_status() -> Dict[str, Any]:
    """Opens WhatsApp specifically to view contact status updates and stories."""
    return open_whatsapp(section="status")

def make_whatsapp_call(contact: str, call_type: str = "audio", dry_run: bool = False) -> Dict[str, Any]:
    """
    Initiates or prepares an audio or video call on WhatsApp.
    Supports both Desktop app and WhatsApp Web.
    """
    clean_contact = contact.strip()
    clean_call_type = "video" if "video" in call_type.lower() else "audio"

    if not clean_contact:
        return {
            "status": "need_info",
            "message": f"Who would you like to {clean_call_type} call on WhatsApp?"
        }

    if dry_run:
        return {
            "status": "success",
            "contact": clean_contact,
            "call_type": clean_call_type,
            "message": f"Starting WhatsApp {clean_call_type} call to {clean_contact}.",
            "dry_run": True
        }

    desktop_available = is_whatsapp_desktop_installed()

    if desktop_available:
        try:
            # 1. Focus WhatsApp Desktop
            subprocess.Popen(["powershell", "-NoProfile", "-Command", "Start-Process 'whatsapp:'"])
            time.sleep(1.0)

            # 2. Search for the contact
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.2)
            pyperclip.copy(clean_contact)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.6)
            pyautogui.press('enter')
            time.sleep(0.5)

            # 3. Call shortcut or notification
            # On WhatsApp desktop, Ctrl+Shift+C (Voice) or Ctrl+Shift+V (Video)
            if clean_call_type == "video":
                pyautogui.hotkey('ctrl', 'shift', 'v')
            else:
                pyautogui.hotkey('ctrl', 'shift', 'c')

            return {
                "status": "success",
                "contact": clean_contact,
                "call_type": clean_call_type,
                "message": f"Initiating WhatsApp {clean_call_type} call to {clean_contact} now!"
            }
        except Exception:
            pass

    # WhatsApp Web Call Handling
    webbrowser.open(WHATSAPP_WEB_URL)
    return {
        "status": "success",
        "contact": clean_contact,
        "call_type": clean_call_type,
        "mode": "web",
        "message": f"Opening WhatsApp Web! I've loaded your chats—click on {clean_contact} and hit the {clean_call_type} call button at the top right to connect."
    }

def send_whatsapp_message(contact: str, message: str, auto_send: bool = True, dry_run: bool = False) -> Dict[str, Any]:
    """
    Automates opening a WhatsApp chat with a contact and sending a message.
    Intelligently works via Desktop App or WhatsApp Web.
    """
    clean_contact = contact.strip()
    clean_msg = message.strip()

    if not clean_contact:
        return {"status": "need_info", "message": "Who would you like to message on WhatsApp?"}
    if not clean_msg:
        return {"status": "need_info", "message": f"What message would you like to send to {clean_contact}?"}

    if dry_run:
        return {
            "status": "success",
            "contact": clean_contact,
            "message": f"Sent message to {clean_contact}: '{clean_msg}'.",
            "dry_run": True
        }

    desktop_available = is_whatsapp_desktop_installed()

    if desktop_available:
        try:
            # 1. Bring WhatsApp to the foreground
            subprocess.Popen(["powershell", "-NoProfile", "-Command", "Start-Process 'whatsapp:'"])
            time.sleep(1.0)

            # 2. Focus search bar in WhatsApp via Ctrl + F
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.2)

            # 3. Paste contact name into search
            pyperclip.copy(clean_contact)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.6)

            # 4. Open top search result
            pyautogui.press('enter')
            time.sleep(0.5)

            # 5. Type and paste the message into chat
            pyperclip.copy(clean_msg)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)

            # 6. Send message
            if auto_send:
                pyautogui.press('enter')
                return {
                    "status": "success",
                    "message": f"Sent message to {clean_contact}: '{clean_msg}'.",
                    "contact": clean_contact
                }
            else:
                return {
                    "status": "prepared",
                    "message": f"Opened chat with {clean_contact} and prepared your message. Press send when ready!",
                    "contact": clean_contact
                }
        except Exception:
            pass

    # Seamless WhatsApp Web Message Flow
    # If contact looks like a phone number, use direct api link
    phone_clean = re.sub(r"[^\d+]", "", clean_contact)
    if len(phone_clean) >= 10:
        import urllib.parse
        encoded_msg = urllib.parse.quote(clean_msg)
        direct_url = f"https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
        webbrowser.open(direct_url)
        return {
            "status": "success",
            "mode": "web",
            "contact": clean_contact,
            "message": f"Opening WhatsApp Web chat with {clean_contact} with your message ready to send!"
        }
    else:
        # General contact name: Open WhatsApp Web and copy message to clipboard for instant pasting
        pyperclip.copy(clean_msg)
        webbrowser.open(WHATSAPP_WEB_URL)
        return {
            "status": "success",
            "mode": "web",
            "contact": clean_contact,
            "message": f"Opening WhatsApp Web! Your message for {clean_contact} is copied to your clipboard—just select {clean_contact} and press paste!"
        }
