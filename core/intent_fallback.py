import re
import webbrowser
from typing import Optional, Tuple, Dict, Any
from config import AGENT_NAME, USER_NAME
from tools.antigravity_tool import execute_antigravity_task
from tools.system_tools import (
    open_application,
    close_application,
    open_website,
    search_web,
    play_youtube,
    lock_screen,
    set_brightness,
    take_screenshot,
    control_volume,
    get_time_and_date,
    get_system_stats,
    get_weather,
    get_wikipedia_summary,
    calculate_math,
    get_clipboard_content,
    copy_to_clipboard
)
from tools.productivity_tools import TimerManager, NotesManager
from tools.whatsapp_tool import (
    open_whatsapp,
    send_whatsapp_message,
    make_whatsapp_call,
    view_whatsapp_status
)
from core.task_monitor import TaskMonitor

def process_offline_intent(text: str, dry_run: bool = False, speaker=None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Parses natural language voice requests locally with zero latency.
    Handles Siri/Alexa/Jarvis-style daily assistant commands, deep emotional intelligence,
    real-world mobile/laptop essentials (WhatsApp calls/status, Instagram, Meet, etc.),
    and never gives blind rejections.
    Returns (handled: bool, spoken_response: str, metadata: dict)
    """
    if not text:
        return False, "", None

    query = text.strip().lower()

    # =========================================================================
    # 1. Emotional Intelligence & User Feelings (Understanding Kowshik's Mood)
    # =========================================================================
    if re.search(r"\b(?:i\s+am|i'm|feeling)\s+(?:very\s+)?(?:tired|exhausted|sleepy|drained|fatigued)\b", query):
        return True, f"You've been working really hard today, {USER_NAME}. Take a deep breath and rest your eyes. Would you like me to play some relaxing music, or dim your screen brightness?", {"type": "emotion_tired"}

    if re.search(r"\b(?:i\s+am|i'm|feeling)\s+(?:very\s+)?(?:stressed|anxious|overwhelmed|tense|frustrated|irritated)\b", query):
        return True, f"I hear you, {USER_NAME}. Take a slow breath—I'm right here with you. We'll handle everything one step at a time. Do you want me to put on calming lo-fi music or take care of something for you?", {"type": "emotion_stressed"}

    if re.search(r"\b(?:i\s+am|i'm|feeling)\s+(?:very\s+)?(?:sad|down|upset|lonely|depressed|unhappy)\b", query):
        return True, f"I'm really sorry you're feeling down, {USER_NAME}. Remember that you are capable and not alone—I'm always in your corner. Let me know if you'd like your favorite music, a funny video, or just some peace.", {"type": "emotion_sad"}

    if re.search(r"\b(?:i\s+am|i'm|feeling)\s+(?:very\s+)?(?:happy|excited|great|awesome|pumped|thrilled)\b|\b(?:got\s+good\s+news|i\s+did\s+it|we\s+did\s+it)\b", query):
        return True, f"That's fantastic news, {USER_NAME}! Your positive energy is contagious! I'm truly thrilled for you—let's keep winning!", {"type": "emotion_happy"}

    if re.search(r"\b(?:you\s+are\s+(?:the\s+best|awesome|great|amazing)|love\s+you\s+bujji|good\s+job\s+bujji|bujji\s+you\s+are\s+great)\b", query):
        return True, f"Thank you so much, {USER_NAME}! Having your back and making your day smoother is what I'm built for. You're the best!", {"type": "emotion_gratitude"}

    # =========================================================================
    # 2. Antigravity Agent Tasks (Runs safely in a separate window)
    # =========================================================================
    antigravity_patterns = [
        r"(?:open\s+)?antigravity(?:\s+and)?\s+(?:prompt|promt|tell|ask|instruct|command)\s+(?:it\s+)?(?:to\s+)?(.+)",
        r"(?:open\s+)?antigravity(?:\s+and\s+)?(?:build|create|make|develop)\s+(.+)",
        r"(?:build|create|make|develop)\s+(.+?)\s+(?:in|using|with)\s+antigravity",
        r"(?:tell|ask|instruct)\s+antigravity\s+to\s+(.+)",
        r"(?:prompt|promt)\s+antigravity\s+(?:to\s+)?(.+)"
    ]

    for pat in antigravity_patterns:
        match = re.search(pat, query, re.IGNORECASE)
        if match:
            task_prompt = match.group(1).strip()
            if not task_prompt.startswith(("build", "create", "make", "develop")):
                task_prompt = f"build {task_prompt}"

            result = execute_antigravity_task(task_prompt, dry_run=dry_run)
            return True, result["spoken_reply"], result

    # =========================================================================
    # 3. WhatsApp Comprehensive Real-World Suite (Web + App + Calls + Status)
    # =========================================================================
    # 3A. WhatsApp Status Updates ("check status", "whatsapp status", "view status")
    if re.search(r"\b(?:check|see|view|open|show)\s+(?:my\s+)?(?:whatsapp\s+)?status(?:es)?\b|\bwhatsapp\s+status\b|\bwhatsapp\s+stories\b", query):
        if not dry_run:
            res = view_whatsapp_status()
            return True, res["message"], res
        return True, "Opening WhatsApp Status updates.", {"status": "dry_run"}

    # 3B. WhatsApp Audio/Voice Call ("call Rahul on whatsapp", "whatsapp voice call Mom", "make an audio call to Rahul")
    wa_voice_call = re.search(r"^(?:make\s+(?:an?\s+)?)?(?:whatsapp\s+)?(?:audio\s+call|voice\s+call|call)\s+(?:to\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+on\s+whatsapp)?$", query, re.I)
    if wa_voice_call and "video" not in query and "message" not in query and not any(w in query for w in ["timer", "note", "stop"]):
        target_name = wa_voice_call.group(1).strip()
        res = make_whatsapp_call(target_name, call_type="audio", dry_run=dry_run)
        return True, res["message"], res

    # 3C. WhatsApp Video Call ("video call Rahul on whatsapp", "make video call to Mom", "whatsapp video call Rahul")
    wa_video_call = re.search(r"^(?:make\s+(?:an?\s+)?)?(?:whatsapp\s+)?video\s+call\s+(?:to\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+on\s+whatsapp)?$", query, re.I)
    if wa_video_call and not any(w in query for w in ["timer", "note", "stop"]):
        target_name = wa_video_call.group(1).strip()
        res = make_whatsapp_call(target_name, call_type="video", dry_run=dry_run)
        return True, res["message"], res

    # 3D. Open WhatsApp / WhatsApp Web ("open whatsapp", "open whatsapp web", "launch whatsapp")
    if re.search(r"^(?:open|launch|start|show)\s+whatsapp(?:\s+web)?$", query, re.I):
        if not dry_run:
            res = open_whatsapp()
            return True, res["message"], res
        return True, "Opening WhatsApp for you.", {"status": "dry_run"}

    # 3E. WhatsApp Message Inquiries without specific contact ("send a whatsapp message")
    if re.search(r"^(?:send\s+(?:a\s+)?(?:whatsapp\s+)?message(?:\s+to\s+one\s+of\s+my\s+contacts?|\s+to\s+someone)?|message\s+someone)$", query, re.I):
        return True, "Sure! Who would you like to message on WhatsApp, and what should I say?", {"type": "whatsapp_ask_target"}

    # 3F. WhatsApp Full Message ("send message to Rahul: I am on the way")
    wa_full = re.search(r"^(?:send\s+(?:a\s+)?)?(?:whatsapp\s+)?(?:message|msg)\s+to\s+([a-zA-Z0-9_\-\s]+?)(?::|\s+saying|\s+that|\s+telling\s+them|\s+say)\s+(.+)$", query, re.I)
    if wa_full and not any(w in query for w in ["timer", "note", "clipboard"]):
        contact = wa_full.group(1).strip()
        msg_body = wa_full.group(2).strip()
        res = send_whatsapp_message(contact, msg_body, auto_send=True, dry_run=dry_run)
        return True, res["message"], res

    # 3G. Contact only: ("send message to Rahul")
    wa_contact_only = re.search(r"^(?:send\s+(?:a\s+)?)?(?:whatsapp\s+)?(?:message|msg)\s+to\s+([a-zA-Z0-9_\-\s]+)$", query, re.I)
    if wa_contact_only and "one of" not in query and "clipboard" not in query:
        contact = wa_contact_only.group(1).strip()
        return True, f"What message would you like to send to {contact}?", {"type": "whatsapp_prompt_msg", "contact": contact}

    # =========================================================================
    # 4. Daily Life Essentials (Instagram, Google Meet, Maps, Calendar, Telegram)
    # =========================================================================
    # Instagram & Reels
    if re.search(r"\b(?:open|check)\s+instagram\b|\b(?:instagram\s+)?reels\b", query):
        if "reel" in query:
            webbrowser.open("https://www.instagram.com/reels/")
            return True, "Opening Instagram Reels for you!", {"type": "instagram_reels"}
        webbrowser.open("https://www.instagram.com")
        return True, "Opening Instagram for you!", {"type": "instagram"}

    # Google Meet ("start google meet", "new meeting", "open meet")
    if re.search(r"\b(?:start|new|open|create)\s+(?:a\s+)?(?:google\s+)?meet(?:ing)?\b", query):
        webbrowser.open("https://meet.google.com/new")
        return True, "Creating a new Google Meet for you right now!", {"type": "google_meet"}

    # Google Maps ("open maps", "where is Hyderabad", "directions to Jubilee Hills")
    maps_match = re.search(r"(?:directions\s+to|where\s+is|navigate\s+to|show\s+on\s+maps?)\s+(.+)", query, re.I)
    if maps_match:
        place = maps_match.group(1).strip()
        import urllib.parse
        encoded = urllib.parse.quote(place)
        webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={encoded}")
        return True, f"Showing {place} on Google Maps for you!", {"type": "maps", "location": place}
    elif re.search(r"\b(?:open|check)\s+(?:google\s+)?maps?\b", query):
        webbrowser.open("https://maps.google.com")
        return True, "Opening Google Maps for you!", {"type": "maps"}

    # Google Calendar ("open calendar", "check schedule")
    if re.search(r"\b(?:open|check)\s+(?:google\s+)?calendar\b|\bcheck\s+my\s+schedule\b", query):
        webbrowser.open("https://calendar.google.com")
        return True, "Opening your Google Calendar!", {"type": "calendar"}

    # Gmail / Email ("check email", "open gmail", "compose email")
    if re.search(r"\b(?:check|read|open)\s+(?:my\s+)?(?:emails?|gmail|mail)\b", query):
        webbrowser.open("https://mail.google.com")
        return True, "Opening your Gmail inbox!", {"type": "gmail"}
    if re.search(r"\b(?:compose|write|send)\s+(?:an?\s+)?(?:new\s+)?email\b", query):
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox?compose=new")
        return True, "Opening a new email draft in Gmail!", {"type": "gmail_compose"}

    # Telegram ("open telegram", "telegram web")
    if re.search(r"\b(?:open|launch)\s+telegram\b", query):
        res = open_application("telegram")
        return True, res["message"], res

    # =========================================================================
    # 5. Close Application ("close chrome", "quit spotify", "exit notepad")
    # =========================================================================
    close_match = re.search(r"^(?:close|quit|exit|kill|stop)\s+(?:the\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+app|\s+application)?$", query, re.I)
    if close_match and not any(w in query for w in ["antigravity", "notes", "timer", "volume"]):
        app_target = close_match.group(1).strip()
        res = close_application(app_target)
        return True, res["message"], res

    # =========================================================================
    # 6. Open Website ("open github", "open chatgpt", "go to reddit")
    # =========================================================================
    website_match = re.search(r"^(?:open|go\s+to)\s+(?:the\s+website\s+|website\s+)?(github|gmail|youtube|reddit|twitter|x|linkedin|chatgpt|netflix|amazon|wikipedia|claude|stack\s*overflow)(?:\.com|\.org|\.ai)?$", query, re.I)
    if website_match:
        site_name = website_match.group(1).strip()
        res = open_website(site_name)
        return True, res["message"], res

    # =========================================================================
    # 7. Open Application (Smart Universal Resolver: App or Web Fallback)
    # =========================================================================
    app_match = re.search(r"^(?:open|launch|start)\s+(?:the\s+)?([a-zA-Z0-9_\-\s]+?)(?:\s+app|\s+application)?$", query, re.I)
    if app_match:
        app_target = app_match.group(1).strip()
        if app_target not in ["youtube", "google", "browser", "camera", "weather", "notes", "antigravity"]:
            res = open_application(app_target)
            return True, res["message"], res

    # =========================================================================
    # 8. Lock PC Screen ("lock my pc", "lock screen", "lock computer")
    # =========================================================================
    if re.search(r"\block\s+(?:my\s+)?(?:pc|screen|computer|workstation)\b", query, re.I):
        if not dry_run:
            res = lock_screen()
            return True, res["message"], res
        return True, "Screen locked.", {"status": "dry_run"}

    # =========================================================================
    # 9. Screen Brightness ("set brightness to 70 percent", "brightness 50")
    # =========================================================================
    bright_match = re.search(r"(?:set\s+)?brightness\s+(?:to\s+)?(\d{1,3})(?:\s*%)?", query, re.I)
    if bright_match:
        val = int(bright_match.group(1))
        if not dry_run:
            res = set_brightness(val)
            return True, res["message"], res
        return True, f"Brightness set to {val}%.", {"status": "dry_run"}

    # =========================================================================
    # 10. Timers ("set a timer for 5 minutes", "timer 10 seconds")
    # =========================================================================
    timer_match = re.search(r"(?:set\s+(?:a\s+)?)?timer\s+(?:for\s+)?(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)", query, re.I)
    if timer_match:
        amount = int(timer_match.group(1))
        unit = timer_match.group(2).lower()
        
        if "hour" in unit or "hr" in unit:
            total_seconds = amount * 3600
        elif "min" in unit:
            total_seconds = amount * 60
        else:
            total_seconds = amount

        if not dry_run:
            tm = TimerManager()
            res = tm.set_timer(total_seconds, label=f"{amount} {unit}", speaker=speaker)
            return True, res["message"], res
        return True, f"Timer set for {amount} {unit}.", {"status": "dry_run"}

    if re.search(r"(?:show|list|check)\s+(?:my\s+)?timers", query, re.I):
        tm = TimerManager()
        res = tm.list_timers()
        return True, res["message"], res

    # =========================================================================
    # 11. Notes & Memos ("take a note: buy groceries", "read my notes")
    # =========================================================================
    note_take = re.search(r"^(?:take\s+(?:a\s+)?note|note\s+down|write\s+down|save\s+note)(?::|\s+that|\s+to|\s+saying)?\s+(.+)$", query, re.I)
    if note_take:
        note_body = note_take.group(1).strip()
        if not dry_run:
            res = NotesManager.take_note(note_body)
            return True, res["message"], res
        return True, f"Note saved: {note_body}", {"status": "dry_run"}

    if re.search(r"^(?:read|show|check|list)\s+(?:my\s+)?notes", query, re.I):
        res = NotesManager.read_notes()
        return True, res["message"], res

    # =========================================================================
    # 12. Weather ("what is the weather", "weather in Mumbai")
    # =========================================================================
    weather_match = re.search(r"(?:weather|temperature)(?:\s+(?:in|for|at)\s+([a-zA-Z\s]+))?", query, re.I)
    if weather_match and "rain" not in query:
        loc = weather_match.group(1)
        res = get_weather(loc.strip() if loc else None)
        return True, res["message"], res

    # =========================================================================
    # 13. Math Calculations ("calculate 25 * 4", "what is 15% of 850", "15 times 4")
    # =========================================================================
    math_match = re.search(r"^(?:calculate|what\s+is|compute|solve)\s+(.+)$", query, re.I)
    if math_match and any(c in math_match.group(1) for c in ["+", "-", "*", "/", "%", "percent", "times", "divided by"]):
        raw_expr = math_match.group(1).strip()
        cleaned_expr = raw_expr.replace("times", "*").replace("divided by", "/").replace("plus", "+").replace("minus", "-")
        res = calculate_math(cleaned_expr)
        if res.get("status") == "success":
            return True, res["message"], res

    # =========================================================================
    # 14. Clipboard Management ("copy <text> to clipboard", "what is in my clipboard")
    # =========================================================================
    copy_match = re.search(r"^(?:copy\s+(.+?)\s+to\s+clipboard|clipboard\s+copy\s+(.+))$", query, re.I)
    if copy_match:
        content_to_copy = copy_match.group(1) or copy_match.group(2)
        res = copy_to_clipboard(content_to_copy.strip())
        return True, res["message"], res

    if re.search(r"\b(?:what\s+is\s+in\s+my\s+clipboard|read\s+clipboard|check\s+clipboard|get\s+clipboard)\b", query, re.I):
        res = get_clipboard_content()
        return True, res["message"], res

    # =========================================================================
    # 15. YouTube & Media Playback ("play Believer on YouTube")
    # =========================================================================
    yt_match = re.search(r"^(?:play|listen\s+to)\s+(.+?)(?:\s+on\s+youtube)?$", query, re.I)
    if yt_match and not any(w in query for w in ["game", "notes", "antigravity"]):
        media_target = yt_match.group(1).strip()
        res = play_youtube(media_target)
        return True, res["message"], res

    # =========================================================================
    # 16. Search Web / Google ("search for quantum computing")
    # =========================================================================
    search_match = re.search(r"^(?:search|google|look\s+up|search\s+for)\s+(.+)$", query, re.I)
    if search_match and not any(w in query for w in ["youtube", "wikipedia"]):
        search_term = search_match.group(1).strip()
        res = search_web(search_term)
        return True, res["message"], res

    # =========================================================================
    # 17. Screenshot ("take a screenshot", "capture screen")
    # =========================================================================
    if "screenshot" in query:
        if not dry_run:
            res = take_screenshot()
            return True, res["message"], res
        return True, "Screenshot saved.", {"status": "dry_run"}

    # =========================================================================
    # 18. Volume Controls
    # =========================================================================
    if "volume" in query or "mute" in query:
        if "up" in query or "increase" in query or "raise" in query:
            res = control_volume("up")
            return True, res["message"], res
        elif "down" in query or "decrease" in query or "lower" in query:
            res = control_volume("down")
            return True, res["message"], res
        elif "mute" in query or "unmute" in query:
            res = control_volume("mute")
            return True, res["message"], res

    # =========================================================================
    # 19. Time and Date
    # =========================================================================
    if re.search(r"\b(?:what\s+is\s+the\s+)?(?:time|date|day\s+is\s+today|what\s+day)\b", query, re.I) and "timer" not in query and "times" not in query:
        res = get_time_and_date()
        return True, res["message"], res

    # =========================================================================
    # 20. System Status / Battery / Hardware
    # =========================================================================
    if any(k in query for k in ["system status", "battery", "cpu", "memory usage", "pc status"]):
        res = get_system_stats()
        return True, res["message"], res

    # =========================================================================
    # 21. Task / Build Monitor Status
    # =========================================================================
    if re.search(r"(?:status|progress|ready|done|finished)\s*(?:of\s+)?(?:my\s+)?(?:task|app|application|antigravity)?", query, re.I):
        monitor = TaskMonitor()
        status_msg = monitor.get_status_summary()
        return True, status_msg, {"type": "status"}

    # =========================================================================
    # 22. Identity & Friendly Small Talk
    # =========================================================================
    if any(k in query for k in ["who are you", "what is your name", "your identity"]):
        return True, f"I am {AGENT_NAME}, your personal AI assistant and companion. I'm right here by your side to take care of anything you need, {USER_NAME}.", {"type": "identity"}

    if re.search(r"^(?:hello|hey|hi|good\s+morning|good\s+evening|how\s+are\s+you)(?:\s+bujji)?$", query, re.I):
        return True, f"Hello {USER_NAME}! It's great to be with you. How can I help you right now?", {"type": "greeting"}

    # =========================================================================
    # 23. Dismiss / End Active Conversation
    # =========================================================================
    if any(k in query for k in ["that's all", "thats all", "thank you", "thanks bujji", "go to sleep", "stop listening", "bye bujji", "goodbye"]):
        return True, f"Always a pleasure, {USER_NAME}! Standing by whenever you need me.", {"type": "end_conversation"}

    return False, "", None
