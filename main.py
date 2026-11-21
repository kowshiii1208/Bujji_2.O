import sys
import time
from config import AGENT_NAME, USER_NAME, WAKE_WORDS, INACTIVITY_TIMEOUT_SECONDS
from core.speaker import BujjiSpeaker
from core.listener import BujjiListener
from core.brain import BujjiBrain
from core.task_monitor import TaskMonitor

def print_banner():
    print("=" * 72)
    print(f"       ⚡ {AGENT_NAME.upper()} - ULTRA PERSONAL AI VOICE ASSISTANT ⚡")
    print(f"        (Always-Active Continuous JARVIS Mode for {USER_NAME})")
    print("=" * 72)
    print(" [✓] Mode:                ALWAYS-ACTIVE LISTENING (NO WAKE WORD REQUIRED!)")
    print(" [✓] Neural Voice Engine: READY (Edge TTS)")
    print(" [✓] Speech Recognition:  READY (Continuous Real-Time)")
    print(" [✓] Intelligence Engine: CONNECTED (FreeLLMAPI Unified Multi-Model)")
    print("-" * 72)
    print(" 🚀 Speak Naturally! Examples (No need to say 'Hey Bujji'):")
    print(" -> 'Open WhatsApp'")
    print(" -> 'Send message to Rahul: I will be there in 10 minutes'")
    print(" -> 'What is the weather today?'")
    print(" -> 'Play Believer on YouTube'")
    print(" -> 'What is 25 percent of 850?'")
    print(" -> 'Go to sleep' (Puts Bujji into standby until you say 'Hey Bujji')")
    print("=" * 72)
    print("\nPress Ctrl+C to exit anytime.\n")

def main():
    print_banner()

    speaker = BujjiSpeaker()
    listener = BujjiListener()
    brain = BujjiBrain(speaker=speaker)
    task_monitor = TaskMonitor(speaker=speaker)

    # Initial Welcome
    speaker.play_chime("wake")
    time.sleep(0.3)
    greeting = f"Hello {USER_NAME}! {AGENT_NAME} is online in Always-Active Mode. I am listening—you can speak your commands directly without saying my wake word!"
    speaker.speak(greeting, block=True)

    # Calibrate ambient noise
    try:
        listener.calibrate(duration=1)
    except Exception as e:
        print(f"[Mic Warning]: {e}")

    # Mode flag: True = Always-Listening (No wake word needed)
    #            False = Standby (Wait for 'Hey Bujji' / 'Hey Bangaram' to re-awaken)
    always_active = True
    last_interaction = time.time()
    inactivity_timeout = INACTIVITY_TIMEOUT_SECONDS

    print(f"\n[{AGENT_NAME}]: 🟢 ALWAYS-ACTIVE LISTENING ENABLED. Speak anytime!")
    print(f"[{AGENT_NAME}]: 🔋 Battery Saver will auto-activate after {inactivity_timeout//60} minutes of silence.\n")

    while True:
        try:
            # Don't listen while Bujji is speaking
            if speaker.is_speaking:
                time.sleep(0.2)
                continue

            # Check for inactivity when in always-active mode
            if always_active:
                elapsed = time.time() - last_interaction
                if elapsed >= inactivity_timeout:
                    print(f"\n[{AGENT_NAME}]: 🔋 Inactive for {int(elapsed)}s. Switching to Standby to save battery.")
                    print(f"[{AGENT_NAME}]: Say 'Hey Bujji' or 'Hey Bangaram' to awaken me.\n")
                    speaker.play_chime("busy")
                    always_active = False

            # Listen with short timeout (3.5s) to stay responsive to inactivity checks
            phrase = listener.listen_audio(timeout=3.5, phrase_time_limit=12)

            if not phrase:
                continue

            print(f"\n[Heard]: \"{phrase}\"")

            clean_phrase = phrase.strip()

            # Check if user invoked wake word
            is_wake, extracted = listener.check_wake_word(clean_phrase)

            if not always_active:
                # In standby: only wake word wakes it up
                if not is_wake:
                    continue
                always_active = True
                last_interaction = time.time()
                speaker.play_chime("wake")
                print(f"[{AGENT_NAME}]: 🟢 Re-awakened into Always-Active Mode!")
                
                # If command was spoken in same breath
                command = extracted if extracted else ""
                if not command:
                    speaker.speak(f"I'm back, {USER_NAME}. What do you need?", block=True)
                    continue
            else:
                # In Always-Active Mode: update last interaction timestamp
                last_interaction = time.time()
                command = extracted if (is_wake and extracted) else clean_phrase

            # Sleep / Standby command
            if any(k in command.lower() for k in ["go to sleep", "sleep now", "standby mode", "take a break", "stop listening for now"]):
                speaker.play_chime("success")
                speaker.speak(f"Going into standby, {USER_NAME}. Just say 'Hey Bujji' or 'Hey Bangaram' whenever you want me back!", block=True)
                always_active = False
                print(f"\n[{AGENT_NAME}]: 💤 STANDBY MODE ACTIVE. Say 'Hey Bujji' or 'Hey Bangaram' to wake me up.\n")
                continue

            # Dismiss / Thank you
            if any(k in command.lower() for k in ["that's all", "thats all", "thanks bujji", "thank you bujji"]):
                speaker.play_chime("success")
                speaker.speak(f"Always a pleasure, {USER_NAME}! I'm right here listening whenever you need anything else.", block=True)
                continue

            print(f"[Executing Command]: \"{command}\"")

            # Process prompt through Brain
            spoken_reply, meta = brain.process(command)

            # Speak response
            speaker.speak(spoken_reply, block=True)

            print(f"[{AGENT_NAME}]: 🟢 Listening for your next command...\n")

        except KeyboardInterrupt:
            print(f"\n\n[{AGENT_NAME}]: Shutting down. Goodbye {USER_NAME}!")
            speaker.speak(f"Goodbye {USER_NAME}!", block=True)
            sys.exit(0)
        except Exception as e:
            print(f"[Loop Exception]: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    main()
