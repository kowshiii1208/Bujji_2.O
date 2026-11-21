import time
import math
import random
import threading
import tkinter as tk
import customtkinter as ctk
from typing import Optional, List, Dict
from config import AGENT_NAME, USER_NAME, VOICE_NAME, INACTIVITY_TIMEOUT_SECONDS
from core.speaker import BujjiSpeaker
from core.listener import BujjiListener
from core.brain import BujjiBrain
from core.task_monitor import TaskMonitor

# High-DPI and Modern Dark Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BujjiHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Geometry & Dark Theme
        self.title(f"{AGENT_NAME} AI — Ultra Personal Voice Assistant (JARVIS Continuous)")
        self.geometry("1080x800")
        self.minsize(980, 700)
        self.configure(fg_color="#050811")

        # Core Components
        self.speaker = BujjiSpeaker()
        self.listener = BujjiListener()
        self.brain = BujjiBrain(speaker=self.speaker)
        self.task_monitor = TaskMonitor(speaker=self.speaker)

        # Always-Active Continuous Listening with Smart Battery Saver
        self.always_active = True
        self.last_interaction_time = time.time()
        self.inactivity_timeout = INACTIVITY_TIMEOUT_SECONDS
        self.current_state = "listening"  # listening, processing, speaking, standby
        self.animation_tick = 0
        self.heartbeat_phase = 0.0

        # Callbacks
        self.speaker.set_callbacks(
            on_start=self._on_speaking_start,
            on_stop=self._on_speaking_stop
        )
        self.listener.on_state_change = self._on_listener_state_change

        # Build Interface
        self._build_interface()

        # Start 40 FPS High-Res Visualizer Engine
        self._animate_visualizer()

        # Start Background Always-Listening Voice Thread
        self.start_voice_thread()

    def _build_interface(self):
        # 1. Top Glassmorphic Navigation Header
        header = ctk.CTkFrame(self, fg_color="#090e1c", corner_radius=14, border_width=1, border_color="#18233c", height=66)
        header.pack(fill="x", padx=18, pady=(16, 8))

        # Title & Subtitle
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=8)

        title_label = ctk.CTkLabel(
            title_box,
            text=f"⚡ {AGENT_NAME.upper()} // ALWAYS-ACTIVE JARVIS",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#00f2fe"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_box,
            text=f"Continuous Voice Interaction • Dedicated to {USER_NAME} (No Wake Word Needed)",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        subtitle_label.pack(anchor="w")

        # Right Control Badges: Mode Toggle & Status
        badges_box = ctk.CTkFrame(header, fg_color="transparent")
        badges_box.pack(side="right", padx=18, pady=8)

        # Mode Toggle Button (Always-Active vs Wake-Word Standby)
        self.mode_toggle_btn = ctk.CTkButton(
            badges_box,
            text="🟢 ALWAYS ACTIVE: ON",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff",
            fg_color="#059669",
            hover_color="#047857",
            corner_radius=8,
            height=32,
            command=self.toggle_mode
        )
        self.mode_toggle_btn.pack(side="right", padx=(8, 0))

        engine_name = self.brain.provider.upper()
        self.engine_badge = ctk.CTkLabel(
            badges_box,
            text=f"🧠 {engine_name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            fg_color="#063223",
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.engine_badge.pack(side="right", padx=6)

        # 2. Main Content Split: Left (Visualizer + Controls), Right (Conversation Stream)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=18, pady=6)

        # Left Column (Visualizer & Action Chips)
        left_col = ctk.CTkFrame(content_frame, fg_color="#080c18", corner_radius=14, border_width=1, border_color="#141c30", width=430)
        left_col.pack(side="left", fill="both", padx=(0, 8), pady=0)
        left_col.pack_propagate(False)

        # Visualizer Canvas (Heartbeat waves + Arc Reactor Orb)
        canvas_container = ctk.CTkFrame(left_col, fg_color="#050811", corner_radius=12, border_width=1, border_color="#101726")
        canvas_container.pack(fill="x", padx=14, pady=(14, 8))

        self.canvas = tk.Canvas(canvas_container, width=400, height=275, bg="#050811", highlightthickness=0)
        self.canvas.pack(pady=6)

        # Dynamic Status label below canvas
        self.state_label = ctk.CTkLabel(
            left_col,
            text="🟢 Always Listening... Speak any command directly!",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00f2fe"
        )
        self.state_label.pack(pady=(2, 8))

        # Quick Voice Command Chips
        chips_header = ctk.CTkLabel(
            left_col,
            text="⚡ QUICK ACTIONS (ONE-CLICK OR VOICE)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#64748b"
        )
        chips_header.pack(anchor="w", padx=16, pady=(6, 4))

        chips_scroll = ctk.CTkScrollableFrame(left_col, fg_color="transparent", height=240)
        chips_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        quick_actions = [
            ("💬 Open WhatsApp", "open whatsapp"),
            ("📨 Message on WhatsApp", "send message to one of my contacts"),
            ("🎵 Play Music on YouTube", "play believer on youtube"),
            ("🌤️ Weather Report", "what is the weather today"),
            ("⏱️ Set 5 Min Timer", "set a timer for 5 minutes"),
            ("📝 Take a Note", "take a note review project roadmap"),
            ("📋 Read My Notes", "read my notes"),
            ("🔢 Calculate 25% of 850", "what is 25 percent of 850"),
            ("📷 Capture Screenshot", "take a screenshot"),
            ("🔒 Lock Workstation", "lock my pc"),
            ("💤 Put Bujji to Sleep", "go to sleep")
        ]

        for label, cmd in quick_actions:
            btn = ctk.CTkButton(
                chips_scroll,
                text=label,
                anchor="w",
                fg_color="#0e1526",
                hover_color="#1e293b",
                border_width=1,
                border_color="#19243c",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=34,
                corner_radius=8,
                command=lambda c=cmd: self.execute_prompt(c)
            )
            btn.pack(fill="x", pady=3)

        # Right Column (Interactive Live Dialogue Stream)
        right_col = ctk.CTkFrame(content_frame, fg_color="#080c18", corner_radius=14, border_width=1, border_color="#141c30")
        right_col.pack(side="right", fill="both", expand=True, padx=(8, 0), pady=0)

        stream_header = ctk.CTkFrame(right_col, fg_color="transparent")
        stream_header.pack(fill="x", padx=18, pady=(12, 6))

        stream_title = ctk.CTkLabel(
            stream_header,
            text="LIVE INTERACTIVE CONVERSATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94a3b8"
        )
        stream_title.pack(side="left")

        clear_btn = ctk.CTkButton(
            stream_header,
            text="Clear Stream",
            font=ctk.CTkFont(size=11),
            fg_color="#1e293b",
            hover_color="#334155",
            width=90,
            height=26,
            corner_radius=6,
            command=self.clear_conversation
        )
        clear_btn.pack(side="right")

        # Chat Bubble Container
        self.chat_scroll = ctk.CTkScrollableFrame(right_col, fg_color="#050811", corner_radius=10, border_width=1, border_color="#101726")
        self.chat_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Initial Welcome Bubble
        self.add_chat_bubble(
            sender=AGENT_NAME,
            text=f"Hello {USER_NAME}! Bujji is online in Always-Active JARVIS Mode.\n"
                 f"You DO NOT need to say 'Hey Bujji' before every sentence. Just speak naturally—ask me to open WhatsApp, send messages, check weather, play music, or control your PC!",
            is_bujji=True
        )

        # 3. Bottom Control Bar (Microphone & Command Input)
        bottom_bar = ctk.CTkFrame(self, fg_color="#090e1c", corner_radius=14, border_width=1, border_color="#18233c", height=66)
        bottom_bar.pack(fill="x", padx=18, pady=(8, 16))

        self.mic_button = ctk.CTkButton(
            bottom_bar,
            text="🎙️ PUSH TO TALK",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00f2fe",
            text_color="#050811",
            hover_color="#38bdf8",
            width=160,
            height=44,
            corner_radius=10,
            command=self.on_push_to_talk
        )
        self.mic_button.pack(side="left", padx=16, pady=11)

        self.entry_box = ctk.CTkEntry(
            bottom_bar,
            placeholder_text="Speak or type a command... (e.g. 'open whatsapp', 'send message to Rahul', 'what is the weather')",
            font=ctk.CTkFont(size=13),
            fg_color="#0c1222",
            border_color="#1a243c",
            border_width=1,
            corner_radius=10,
            height=44
        )
        self.entry_box.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=11)
        self.entry_box.bind("<Return>", lambda e: self.on_text_submit())

        send_btn = ctk.CTkButton(
            bottom_bar,
            text="Send",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            width=80,
            height=44,
            corner_radius=10,
            command=self.on_text_submit
        )
        send_btn.pack(side="right", padx=(0, 16), pady=11)

    def toggle_mode(self):
        """Toggles between Always-Active Mode and Wake-Word Standby."""
        self.always_active = not self.always_active
        self.last_interaction_time = time.time()
        if self.always_active:
            self.mode_toggle_btn.configure(text="🟢 ALWAYS ACTIVE: ON", fg_color="#059669", hover_color="#047857")
            self.set_state("listening", "🟢 Always-Active Mode ON: Speak freely without wake word!")
            self.speaker.speak(f"Always active mode enabled, {USER_NAME}. I'm listening continuously!", block=False)
        else:
            self.mode_toggle_btn.configure(text="🔋 BATTERY SAVER: STANDBY", fg_color="#d97706", hover_color="#b45309")
            self.set_state("standby", "🔋 Battery Saver: Standby Mode. Say 'Hey Bujji' or 'Hey Bangaram' to activate.")
            self.speaker.speak(f"Standby mode active to save battery, {USER_NAME}. Say 'Hey Bujji' or 'Hey Bangaram' to wake me back up!", block=False)

    def _animate_visualizer(self):
        """
        Cinema-Grade EKG Heartbeat Waveform + Holographic Arc Reactor Core.
        Renders at 40 FPS.
        """
        self.canvas.delete("all")
        self.animation_tick = (self.animation_tick + 1) % 3600
        cx, cy = 200, 137

        # Colors by current state
        if self.current_state == "listening":
            wave_color = "#00f2fe"      # Electric Cyan
            glow_color = "#38bdf8"
            pulse_speed = 0.12
            heartbeat_amp = 48.0
        elif self.current_state == "processing":
            wave_color = "#a855f7"      # Neon Purple
            glow_color = "#c084fc"
            pulse_speed = 0.08
            heartbeat_amp = 22.0
        elif self.current_state == "speaking":
            wave_color = "#10b981"      # Emerald Neon
            glow_color = "#34d399"
            pulse_speed = 0.16
            heartbeat_amp = 38.0
        else:  # standby
            wave_color = "#0284c7"      # Deep Ice Blue
            glow_color = "#0369a1"
            pulse_speed = 0.04
            heartbeat_amp = 8.0

        self.heartbeat_phase = (self.heartbeat_phase + pulse_speed) % (2.0 * math.pi)
        pulse = math.sin(self.heartbeat_phase * 2.5) * 4.0

        # 1. Background Grid & Radar Halo
        for r in [115, 82, 52]:
            alpha_color = "#0b1324" if r > 52 else "#0f1c34"
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=alpha_color, width=1)

        # 2. Glowing Expanding Heartbeat Ripple (when active listening or speaking)
        if self.current_state in ["listening", "speaking"]:
            ripple_r = 45 + ((self.animation_tick * 2.5) % 75)
            ripple_color = "#00f2fe" if self.current_state == "listening" else "#10b981"
            self.canvas.create_oval(cx - ripple_r, cy - ripple_r, cx + ripple_r, cy + ripple_r, outline=ripple_color, width=1)

        # 3. Dynamic EKG Heartbeat Wave across the middle
        wave_points = []
        width = 400
        step_x = 4

        for x in range(0, width + step_x, step_x):
            norm_x = (x / width) * 4.0 * math.pi - (self.heartbeat_phase * 3.0)
            
            # Base harmonic sine wave
            sine_val = math.sin(norm_x) * (8.0 if self.current_state == "standby" else 14.0)

            # Heartbeat spike function (EKG shape) centered near middle
            dist_to_center = abs(x - cx)
            if dist_to_center < 60:
                progress = (x - (cx - 60)) / 120.0
                spike = math.sin(progress * math.pi * 3.0) * math.exp(-((progress - 0.5) ** 2) * 20.0)
                sine_val += spike * heartbeat_amp

            # Subtle audio jitter
            if self.current_state in ["listening", "speaking"]:
                sine_val += (random.random() - 0.5) * 5.0

            y = cy + sine_val
            wave_points.extend([x, y])

        if len(wave_points) >= 4:
            self.canvas.create_line(wave_points, fill=glow_color, width=3, smooth=True)
            self.canvas.create_line(wave_points, fill=wave_color, width=1, smooth=True)

        # 4. Central Reactor Core & Orbiting Nodes
        core_r = 28 + (pulse if self.current_state != "standby" else 0)
        self.canvas.create_oval(cx - core_r, cy - core_r, cx + core_r, cy + core_r, fill="#060e1d", outline=wave_color, width=2)

        # Rotating outer tech ticks
        ticks = 12
        for i in range(ticks):
            angle = math.radians(i * (360 / ticks) + (self.animation_tick * 1.5))
            tx1 = cx + (core_r + 4) * math.cos(angle)
            ty1 = cy + (core_r + 4) * math.sin(angle)
            tx2 = cx + (core_r + 11) * math.cos(angle)
            ty2 = cy + (core_r + 11) * math.sin(angle)
            self.canvas.create_line(tx1, ty1, tx2, ty2, fill=wave_color, width=2)

        # Core Symbol
        icon_text = "⚡" if self.current_state != "listening" else "♥"
        icon_color = "#ffffff" if self.current_state != "listening" else "#00f2fe"
        self.canvas.create_text(cx, cy, text=icon_text, font=("Segoe UI", 16, "bold"), fill=icon_color)

        # Schedule next frame (40 FPS active vs 12 FPS battery saver in standby)
        frame_delay = 25 if self.current_state != "standby" else 80
        self.after(frame_delay, self._animate_visualizer)

    def set_state(self, state: str, message: str = ""):
        self.current_state = state
        colors = {
            "standby": ("#38bdf8", "STANDBY (SAY 'HEY BUJJI')"),
            "listening": ("#00f2fe", "ALWAYS LISTENING (HEARTBEAT ACTIVE)"),
            "processing": ("#c084fc", "PROCESSING QUERY"),
            "speaking": ("#34d399", "SPEAKING RESPONSE")
        }
        color, label = colors.get(state, ("#38bdf8", state.upper()))

        def _update():
            if message:
                self.state_label.configure(text=message, text_color=color)

            if state == "listening":
                self.mic_button.configure(text="🎙️ LISTENING...", fg_color="#f59e0b", text_color="#000000")
            elif state == "speaking":
                self.mic_button.configure(text="🔊 SPEAKING...", fg_color="#10b981", text_color="#000000")
            else:
                self.mic_button.configure(text="🎙️ PUSH TO TALK", fg_color="#00f2fe", text_color="#050811")

        self.after(0, _update)

    def add_chat_bubble(self, sender: str, text: str, is_bujji: bool = False):
        """Adds a sleek modern chat bubble to the conversation stream."""
        def _add():
            timestamp = time.strftime("%I:%M %p")
            
            bubble = ctk.CTkFrame(
                self.chat_scroll,
                fg_color="#0e1628" if not is_bujji else "#091222",
                border_width=1,
                border_color="#1c273e" if not is_bujji else "#0284c7",
                corner_radius=12
            )
            bubble.pack(fill="x", pady=6, padx=6)

            header_box = ctk.CTkFrame(bubble, fg_color="transparent")
            header_box.pack(fill="x", padx=12, pady=(8, 2))

            sender_color = "#38bdf8" if not is_bujji else "#00f2fe"
            icon = "👤" if not is_bujji else "⚡"
            sender_lbl = ctk.CTkLabel(
                header_box,
                text=f"{icon} {sender}",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=sender_color
            )
            sender_lbl.pack(side="left")

            time_lbl = ctk.CTkLabel(
                header_box,
                text=timestamp,
                font=ctk.CTkFont(size=10),
                text_color="#64748b"
            )
            time_lbl.pack(side="right")

            msg_lbl = ctk.CTkLabel(
                bubble,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="#f8fafc",
                wraplength=520,
                justify="left"
            )
            msg_lbl.pack(anchor="w", padx=12, pady=(2, 10))

            self.chat_scroll._parent_canvas.yview_moveto(1.0)

        self.after(0, _add)

    def clear_conversation(self):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.brain.reset_history()
        self.add_chat_bubble(
            sender=AGENT_NAME,
            text=f"Conversation memory cleared. Ready for your commands, {USER_NAME}!",
            is_bujji=True
        )

    def _on_speaking_start(self, text: str):
        self.set_state("speaking", f"{AGENT_NAME} is speaking...")

    def _on_speaking_stop(self):
        if self.always_active:
            self.set_state("listening", "🟢 Always-Active: Listening for your next command...")
        else:
            self.set_state("standby", "Standby Mode. Say 'Hey Bujji' to wake me up.")

    def _on_listener_state_change(self, state: str):
        if state == "listening":
            msg = "🟢 Listening to your words... (Heartbeat Active)" if self.always_active else "Standby: Listening for 'Hey Bujji'..."
            self.set_state("listening", msg)
        elif state == "processing":
            self.set_state("processing", "Analyzing speech & reasoning...")
        elif state == "idle":
            if not self.speaker.is_speaking:
                if self.always_active:
                    self.set_state("listening", "🟢 Always Listening... Speak directly!")
                else:
                    self.set_state("standby", "Standby Mode. Say 'Hey Bujji' to wake me up.")

    def on_text_submit(self):
        text = self.entry_box.get().strip()
        if text:
            self.entry_box.delete(0, "end")
            self.execute_prompt(text)

    def on_push_to_talk(self):
        def _listen():
            self.speaker.play_chime("wake")
            self.set_state("listening", "Listening to your voice... Speak now!")
            spoken = self.listener.listen_audio(timeout=6, phrase_time_limit=10)
            if spoken:
                self.execute_prompt(spoken)
            else:
                self.set_state("listening", "🟢 Always Listening... Speak anytime!")
        threading.Thread(target=_listen, daemon=True).start()

    def execute_prompt(self, query: str):
        """Executes prompt and stays continuously listening."""
        self.last_interaction_time = time.time()
        def _run():
            self.add_chat_bubble(USER_NAME, query, is_bujji=False)
            self.set_state("processing", "Reasoning & executing command...")

            # Process via Brain (retains multi-turn context)
            spoken_reply, meta = self.brain.process(query)

            self.add_chat_bubble(AGENT_NAME, spoken_reply, is_bujji=True)
            self.speaker.speak(spoken_reply, block=True)

            # If user asked to sleep
            if meta and meta.get("type") == "end_conversation":
                self.always_active = False
                def _to_sleep():
                    self.mode_toggle_btn.configure(text="🔋 BATTERY SAVER: STANDBY", fg_color="#d97706", hover_color="#b45309")
                    self.set_state("standby", "Standby Mode. Say 'Hey Bujji' or 'Hey Bangaram' to wake me up.")
                self.after(0, _to_sleep)
            else:
                self.set_state("listening", "🟢 Always-Active: Listening for your next words...")

        threading.Thread(target=_run, daemon=True).start()

    def start_voice_thread(self):
        """
        Always-Active background voice loop with smart battery saver:
        Automatically pauses to low-power Standby after 5-10 minutes of inactivity.
        Awakens instantly when you say 'Hey Bujji', 'Hey Bangaram', 'Hii Bujji', 'Hey Jarvis', etc.
        """
        def loop():
            try:
                self.listener.calibrate(duration=1)
            except Exception as e:
                print(f"[HUD Calibration Warning] {e}")

            while True:
                if self.speaker.is_speaking:
                    time.sleep(0.2)
                    continue

                try:
                    # 1. Smart Battery Saver: Check for inactivity pause (5-10 mins)
                    if self.always_active:
                        elapsed = time.time() - self.last_interaction_time
                        if elapsed >= self.inactivity_timeout:
                            print(f"[HUD Battery Saver] Inactive for {int(elapsed)}s. Entering low-power standby.")
                            self.always_active = False
                            def _to_power_save():
                                self.mode_toggle_btn.configure(text="🔋 BATTERY SAVER: STANDBY", fg_color="#d97706", hover_color="#b45309")
                                self.set_state("standby", "🔋 Battery Saver Active. Say 'Hey Bujji' or 'Hey Bangaram' to wake me!")
                            self.after(0, _to_power_save)
                            self.speaker.play_chime("busy")

                    # 2. Listen with short timeout (3.5s) to remain responsive to pause checks
                    phrase = self.listener.listen_audio(timeout=3.5, phrase_time_limit=12)
                    if not phrase:
                        continue

                    print(f"[HUD Heard]: \"{phrase}\"")

                    clean_phrase = phrase.strip()
                    is_wake, extracted = self.listener.check_wake_word(clean_phrase)

                    if not self.always_active:
                        # Standby / Battery Saver: only wake expressions re-awaken it:
                        # 'hey bujji', 'hey bangaram', 'hii bujji', 'hey jarvis', 'bujjiiii', etc.
                        if not is_wake:
                            continue

                        self.always_active = True
                        self.last_interaction_time = time.time()
                        self.speaker.play_chime("wake")
                        
                        def _wake_ui():
                            self.mode_toggle_btn.configure(text="🟢 ALWAYS ACTIVE: ON", fg_color="#059669", hover_color="#047857")
                            self.set_state("listening", "🟢 Always-Active: Listening for your next words...")
                        self.after(0, _wake_ui)
                        
                        command = extracted if extracted else ""
                        if not command:
                            self.speaker.speak(f"I'm right here, {USER_NAME}! How can I help you?", block=True)
                            continue
                    else:
                        # In Always-Active: update last interaction timestamp
                        self.last_interaction_time = time.time()
                        command = extracted if (is_wake and extracted) else clean_phrase

                    # Sleep command
                    if any(k in command.lower() for k in ["go to sleep", "sleep now", "standby mode", "take a break"]):
                        self.always_active = False
                        def _manual_sleep():
                            self.mode_toggle_btn.configure(text="🔋 BATTERY SAVER: STANDBY", fg_color="#d97706", hover_color="#b45309")
                            self.set_state("standby", "Standby Mode. Say 'Hey Bujji' or 'Hey Bangaram' to wake me up.")
                        self.after(0, _manual_sleep)
                        self.speaker.play_chime("success")
                        self.speaker.speak(f"Going into standby to save battery, {USER_NAME}. Say 'Hey Bujji' or 'Hey Bangaram' whenever you need me!", block=True)
                        continue

                    self.execute_prompt(command)

                except Exception as e:
                    time.sleep(0.5)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()

def launch_hud():
    app = BujjiHUD()
    app.mainloop()

if __name__ == "__main__":
    launch_hud()
