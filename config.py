import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECTS_DIR = Path(os.getenv("BUJJI_PROJECTS_DIR", str(Path.home() / "BujjiProjects")))
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Personalization
AGENT_NAME = "Bujji"
USER_NAME = os.getenv("USER_NAME", "Kowshik")
WAKE_WORDS = [
    "hey bujji", "bujji", "bujjii", "bujjiii", "bujjiiii",
    "hey bangaram", "bangaram",
    "hii bujji", "hi bujji", "hiii bujji", "hello bujji",
    "jarvis", "hey jarvis", "hi jarvis", "hiii jarvis", "hey jaravis", "jaravis",
    "siri", "hey siri", "alexa", "hey alexa", "computer"
]

# Battery Saver & Inactivity Timing (5 to 10 minutes of silence)
# Inactivity threshold: drops to low-power standby if user doesn't speak
INACTIVITY_TIMEOUT_SECONDS = int(os.getenv("BUJJI_INACTIVITY_TIMEOUT", "300"))  # 300s = 5 minutes

# Speech & Voice Settings
# Edge TTS Voices:
# 'en-IN-NeerjaNeural' (Indian English Female - energetic, friendly Bujji style)
# 'en-IN-PrabhatNeural' (Indian English Male)
# 'en-GB-RyanNeural' (British Jarvis style)
# 'en-US-AriaNeural' (US English Siri style)
VOICE_NAME = os.getenv("BUJJI_VOICE", "en-IN-NeerjaNeural")
SPEECH_RATE = os.getenv("BUJJI_SPEED", "+5%")
SPEECH_PITCH = os.getenv("BUJJI_PITCH", "+0Hz")

# Antigravity IDE Configuration
ANTIGRAVITY_CMD = os.getenv(
    "ANTIGRAVITY_CMD",
    r"C:\Users\kowsh\AppData\Local\Programs\Antigravity IDE\bin\antigravity-ide.cmd"
)
ANTIGRAVITY_EXE = os.getenv(
    "ANTIGRAVITY_EXE",
    r"C:\Users\kowsh\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe"
)
ANTIGRAVITY_BRAIN_DIR = Path(os.getenv(
    "ANTIGRAVITY_BRAIN_DIR",
    r"C:\Users\kowsh\.gemini\antigravity\brain"
))

# LLM Providers Configuration
# Auto-detects based on available environment variables
FREELLMAPI_KEY = os.getenv("FREELLMAPI_KEY", "")
FREELLMAPI_BASE_URL = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:31415/v1")
DEFAULT_FREELLMAPI_MODEL = os.getenv("FREELLMAPI_MODEL", "auto")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

# Listening Settings
ENERGY_THRESHOLD = 300  # Microphone sensitivity
PAUSE_THRESHOLD = 0.8   # Silence threshold in seconds before processing
TIMEOUT_SECONDS = 5     # Waiting for phrase to start
PHRASE_TIME_LIMIT = 10  # Max length of a single spoken instruction
