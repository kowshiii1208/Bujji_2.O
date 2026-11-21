# Bujji AI — Personal Voice Assistant & Interactive HUD

Bujji AI is a personalized, interactive desktop voice assistant designed for seamless everyday computer control, continuous multi-turn conversations, smart power management, and real-time audio visualization.

---

## Key Features

- **Continuous Conversation Mode:** Talk naturally in back-to-back sentences without needing to repeat wake words between consecutive commands.
- **Smart Battery Saver:** Automatically enters low-power standby mode after 5 minutes of silence, reducing CPU and microphone usage.
- **Multi-Variant Wake Calling:** Wake the assistant from standby using flexible phrases such as:
  - `"Hey Bujji"`, `"Bujji"`, `"Hii Bujji"`
  - `"Hey Bangaram"`, `"Bangaram"`
  - `"Hey Jarvis"`, `"Jarvis"`
- **Animated Audio Waveform HUD:** A reactive visualizer displaying glowing EKG-style waveforms and status indicators in real time.
- **Universal App & Web Automation:**
  - **WhatsApp Integration:** Supports messaging, voice calls, video calls, and status updates across both desktop application and WhatsApp Web.
  - **Smart Online Fallbacks:** If a requested application is not installed locally, the assistant automatically opens the corresponding web service (Instagram, Spotify, Google Meet, Gmail, Google Maps, etc.) so tasks never fail.
- **Empathetic Interaction:** Contextual conversational awareness that responds supportively when you express fatigue, stress, or excitement.
- **Multi-LLM Backend:** Works with FreeLLMAPI, Google Gemini, Groq, and OpenAI models via standard environment configuration.

---

## Getting Started

### 1. Prerequisites
- **OS:** Windows 10 or Windows 11
- **Python:** Version 3.10 or higher
- Working microphone and speakers / headphones

### 2. Installation

Clone this repository to your machine:
```bash
git clone https://github.com/kowshiii1208/Bujji_2.O.git
cd Bujji_2.O
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```
*(Or double-click `Install_Dependencies.bat` on Windows)*

### 3. Configuration

Copy the example configuration file:
```bash
copy .env.example .env
```

Open `.env` in any text editor and set your preferred configuration:
- `USER_NAME`: Your name
- `BUJJI_INACTIVITY_TIMEOUT`: Inactivity seconds before battery saver activates (default: `300` for 5 minutes)
- Add your chosen API key (`FREELLMAPI_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENAI_API_KEY`)

### 4. Running the Assistant

- **Launch Interactive GUI HUD:**
  ```bash
  python run_gui.py
  ```
  *(Or double-click `Launch_GUI.bat`)*

- **Launch CLI / Background Loop:**
  ```bash
  python main.py
  ```

- **Run Diagnostics & Verification Tests:**
  ```bash
  python test_agent.py
  ```
  *(Or double-click `Run_Tests.bat`)*

---

## Project Structure

```
my_personal_agent/
├── core/
│   ├── brain.py             # LLM reasoning, multi-turn history, and tool dispatch
│   ├── listener.py          # Speech recognition and wake phrase detection
│   ├── speaker.py           # Neural text-to-speech engine and audio chimes
│   ├── intent_fallback.py   # Zero-latency local natural language intent parser
│   └── task_monitor.py      # Background task observer and completion callbacks
├── tools/
│   ├── system_tools.py      # App management, web search, system controls
│   ├── whatsapp_tool.py     # WhatsApp messaging, calls, and status automation
│   ├── productivity_tools.py# Timer and note management
│   └── antigravity_tool.py  # Isolated background project generation
├── ui/
│   └── hud.py               # Futuristic desktop GUI HUD and waveform visualizer
├── config.py                # Environment and assistant settings
├── main.py                  # CLI voice loop entry point
├── run_gui.py               # HUD GUI launcher
├── test_agent.py            # Automated diagnostic test suite
├── requirements.txt         # Python package dependencies
├── .env.example             # Template for API keys and personalization
└── README.md                # Documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
