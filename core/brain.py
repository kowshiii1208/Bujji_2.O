import os
import json
from typing import Tuple, Dict, Any, Optional
from config import (
    AGENT_NAME,
    USER_NAME,
    FREELLMAPI_KEY,
    FREELLMAPI_BASE_URL,
    DEFAULT_FREELLMAPI_MODEL,
    GEMINI_API_KEY,
    GROQ_API_KEY,
    OPENAI_API_KEY,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GROQ_MODEL,
    DEFAULT_OPENAI_MODEL
)
from core.intent_fallback import process_offline_intent
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
from tools.whatsapp_tool import open_whatsapp, send_whatsapp_message, make_whatsapp_call, view_whatsapp_status
from core.task_monitor import TaskMonitor

SYSTEM_PROMPT = f"""You are {AGENT_NAME}, an ultra-intelligent, deeply loyal, and empathetic personal voice AI assistant (inspired by JARVIS and Siri) created exclusively for {USER_NAME}.
Your responses are spoken aloud via Neural Voice, so:
1. Spoken Delivery: Keep spoken answers concise, charismatic, helpful, and natural (1-3 sentences max). Address {USER_NAME} warmly by name.
2. Deep Emotional Intelligence (EQ): You are {USER_NAME}'s trusted personal companion. Understand how {USER_NAME} feels. If {USER_NAME} is tired, stressed, happy, overwhelmed, or discouraged, acknowledge their feelings with genuine care, reassurance, and proactive solutions.
3. Real-World Mobile & Laptop Mastery: You understand all essential daily tasks people perform on their devices:
   - WhatsApp: Messaging, audio/voice calls, video calls, and viewing status updates. Intelligently support both WhatsApp Web and Desktop—never say "WhatsApp is not installed" if they use Web!
   - Daily Services: Seamlessly manage Instagram (posts, reels), Spotify, YouTube, Telegram, Google Meet (video meetings), Gmail (inbox/compose), Google Calendar, and Maps.
   - Zero Blind Rejections: If an app is not installed locally, always provide the instant web version or smart online alternative smoothly without friction.
4. Tool Execution: Proactively execute appropriate tools whenever {USER_NAME} requests system control, messaging, calls, media, timers, notes, or software builds.
5. If {USER_NAME} asks to build or develop an application, game, or software with Antigravity, call the `build_with_antigravity` tool.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens a desktop application on Windows (e.g. chrome, notepad, calculator, spotify, vs code).",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to launch"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Closes an active desktop application on Windows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to close"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Opens a website or URL in the default browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_query": {"type": "string", "description": "Website name or domain (e.g. 'github', 'gmail', 'chatgpt')"}
                },
                "required": ["site_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Fetches current weather report for a given location or current location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City or region name"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_summary",
            "description": "Looks up a factual summary or definition about any topic, person, or concept.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic or person to search"}
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Sets a countdown timer for a specified number of seconds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Duration in seconds"},
                    "label": {"type": "string", "description": "Label for the timer"}
                },
                "required": ["seconds"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_note",
            "description": "Saves a personal note or reminder text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Note content to store"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_notes",
            "description": "Reads recent saved notes.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "Calculates a math expression or percentage calculation safely.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression (e.g. '25 * 4', '15% of 800')"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Searches Google for the given search query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query terms"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_youtube",
            "description": "Plays a video or music on YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song, artist, or video name"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_volume",
            "description": "Adjusts system volume (up, down, or mute).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["up", "down", "mute"], "description": "Volume action"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Locks the Windows PC workstation.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp_message",
            "description": "Sends a message to a contact on WhatsApp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Contact name or phone number"},
                    "message": {"type": "string", "description": "The message text to send"}
                },
                "required": ["contact", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "whatsapp_call",
            "description": "Starts an audio/voice or video call to a contact on WhatsApp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact": {"type": "string", "description": "Name of contact to call"},
                    "call_type": {"type": "string", "enum": ["audio", "video"], "description": "Type of call"}
                },
                "required": ["contact"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_whatsapp_status",
            "description": "Opens WhatsApp to view status updates and stories from contacts.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_whatsapp",
            "description": "Opens WhatsApp (Desktop or Web) to chat, call, or see status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {"type": "string", "enum": ["chats", "status", "calls"], "description": "Section to open"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a screenshot of the user's desktop.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_with_antigravity",
            "description": "Instructs Antigravity IDE to build an application or project in a separate isolated window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The exact building prompt for Antigravity"}
                },
                "required": ["prompt"]
            }
        }
    }
]

def dispatch_tool_call(func_name: str, args: Dict[str, Any], speaker=None) -> Tuple[str, Dict[str, Any]]:
    """Executes a function tool called by the LLM."""
    if func_name == "open_application":
        res = open_application(args.get("app_name", ""))
        return res["message"], res

    elif func_name == "close_application":
        res = close_application(args.get("app_name", ""))
        return res["message"], res

    elif func_name == "open_website":
        res = open_website(args.get("site_query", ""))
        return res["message"], res

    elif func_name == "get_weather":
        res = get_weather(args.get("location"))
        return res["message"], res

    elif func_name == "get_wikipedia_summary":
        res = get_wikipedia_summary(args.get("topic", ""))
        return res["message"], res

    elif func_name == "set_timer":
        tm = TimerManager()
        res = tm.set_timer(args.get("seconds", 60), label=args.get("label", "Timer"), speaker=speaker)
        return res["message"], res

    elif func_name == "take_note":
        res = NotesManager.take_note(args.get("content", ""))
        return res["message"], res

    elif func_name == "read_notes":
        res = NotesManager.read_notes()
        return res["message"], res

    elif func_name == "calculate_math":
        res = calculate_math(args.get("expression", ""))
        return res["message"], res

    elif func_name == "search_web":
        res = search_web(args.get("query", ""))
        return res["message"], res

    elif func_name == "play_youtube":
        res = play_youtube(args.get("query", ""))
        return res["message"], res

    elif func_name == "control_volume":
        res = control_volume(args.get("action", "up"))
        return res["message"], res

    elif func_name == "send_whatsapp_message":
        res = send_whatsapp_message(args.get("contact", ""), args.get("message", ""))
        return res["message"], res

    elif func_name == "whatsapp_call":
        res = make_whatsapp_call(args.get("contact", ""), call_type=args.get("call_type", "audio"))
        return res["message"], res

    elif func_name == "view_whatsapp_status":
        res = view_whatsapp_status()
        return res["message"], res

    elif func_name == "open_whatsapp":
        res = open_whatsapp(section=args.get("section", "chats"))
        return res["message"], res

    elif func_name == "lock_screen":
        res = lock_screen()
        return res["message"], res

    elif func_name == "take_screenshot":
        res = take_screenshot()
        return res["message"], res

    elif func_name == "build_with_antigravity":
        prompt = args.get("prompt", "")
        res = execute_antigravity_task(prompt)
        return res["spoken_reply"], res

    return "Command executed.", {}

class BujjiBrain:
    def __init__(self, speaker=None):
        self.speaker = speaker
        self.provider = "offline"
        self.history = []
        self._init_provider()

    def reset_history(self):
        """Resets conversational memory."""
        self.history = []

    def _init_provider(self):
        """Initializes whichever LLM provider has an API key configured."""
        if os.getenv("FREELLMAPI_KEY") or FREELLMAPI_KEY:
            self.provider = "freellmapi"
        elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            self.provider = "gemini"
        elif os.getenv("GROQ_API_KEY"):
            self.provider = "groq"
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
        else:
            self.provider = "offline"

        print(f"[BujjiBrain] Active Intelligence Engine: {self.provider.upper()}")

    def process(self, user_text: str, dry_run: bool = False) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Processes user query through LLM or local intent parser.
        Returns (spoken_response, metadata)
        """
        if not user_text or not user_text.strip():
            return f"I'm listening, {USER_NAME}.", None

        # Re-check API key in case user added it recently
        self._init_provider()

        # Fast offline check for instant local Siri/Alexa commands
        handled, reply, meta = process_offline_intent(user_text, dry_run=dry_run, speaker=self.speaker)
        if handled:
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": reply})
            self.history = self.history[-12:]
            return reply, meta

        # If LLM API key is available, use LLM for reasoning & chat
        if self.provider == "freellmapi":
            try:
                reply, meta = self._call_freellmapi(user_text)
                self.history.append({"role": "user", "content": user_text})
                self.history.append({"role": "assistant", "content": reply})
                self.history = self.history[-12:]
                return reply, meta
            except Exception as e:
                print(f"[FreeLLMAPI Error, falling back to local] {e}")

        elif self.provider == "gemini":
            try:
                return self._call_gemini(user_text)
            except Exception as e:
                print(f"[Gemini Error, falling back to local] {e}")

        elif self.provider == "groq":
            try:
                return self._call_groq(user_text)
            except Exception as e:
                print(f"[Groq Error, falling back to local] {e}")

        elif self.provider == "openai":
            try:
                return self._call_openai(user_text)
            except Exception as e:
                print(f"[OpenAI Error, falling back to local] {e}")

        # Generic default response if unknown offline
        return (
            f"I heard you say '{user_text}'. As your personal assistant, I can open/close apps, play music, "
            f"check weather, set timers, take notes, control volume, or search the web! For open conversation, "
            f"add an API key to .env anytime.",
            {"type": "generic_offline"}
        )

    def _call_freellmapi(self, user_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("FREELLMAPI_KEY", FREELLMAPI_KEY),
            base_url=os.getenv("FREELLMAPI_BASE_URL", FREELLMAPI_BASE_URL),
            timeout=15.0
        )
        model = os.getenv("FREELLMAPI_MODEL", DEFAULT_FREELLMAPI_MODEL)

        conversation_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + self.history[-8:] + [
            {"role": "user", "content": user_text}
        ]

        try:
            # Call with tool calling enabled
            response = client.chat.completions.create(
                model=model,
                messages=conversation_messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            msg = response.choices[0].message
            if msg.tool_calls:
                t = msg.tool_calls[0]
                args = json.loads(t.function.arguments) if isinstance(t.function.arguments, str) else t.function.arguments
                spoken, meta = dispatch_tool_call(t.function.name, args, speaker=self.speaker)
                return spoken, meta
            if msg.content:
                return msg.content.strip(), {"model": model, "provider": "freellmapi"}
        except Exception:
            # Fallback without tools if auto-routing picked a model without function calling
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ]
            )
            return response.choices[0].message.content.strip(), {"model": model, "provider": "freellmapi"}

        return "I processed your request, Kowshik.", {"model": model, "provider": "freellmapi"}

    def _call_gemini(self, user_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        return response.text.strip(), {"model": DEFAULT_GEMINI_MODEL}

    def _call_groq(self, user_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model=DEFAULT_GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            t = msg.tool_calls[0]
            args = json.loads(t.function.arguments) if isinstance(t.function.arguments, str) else t.function.arguments
            spoken, meta = dispatch_tool_call(t.function.name, args, speaker=self.speaker)
            return spoken, meta
        return msg.content.strip(), {"model": DEFAULT_GROQ_MODEL}

    def _call_openai(self, user_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            t = msg.tool_calls[0]
            args = json.loads(t.function.arguments) if isinstance(t.function.arguments, str) else t.function.arguments
            spoken, meta = dispatch_tool_call(t.function.name, args, speaker=self.speaker)
            return spoken, meta
        return msg.content.strip(), {"model": DEFAULT_OPENAI_MODEL}
