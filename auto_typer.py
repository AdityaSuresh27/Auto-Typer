"""
Auto Typer — Simulates real keyboard typing, one character at a time.
Uses pynput for OS-level keystroke simulation so websites/apps see real keyboard input.
"""

import customtkinter as ctk
import threading
import time
from pynput.keyboard import Controller, Key, Listener


# ─── Color Palette ───────────────────────────────────────────────────────────

COLORS = {
    "bg_dark":      "#0d1117",
    "bg_card":      "#161b22",
    "bg_input":     "#0d1117",
    "border":       "#30363d",
    "accent":       "#58a6ff",
    "accent_hover":  "#79c0ff",
    "accent_dim":   "#1f6feb",
    "text":         "#e6edf3",
    "text_dim":     "#8b949e",
    "green":        "#238636",
    "green_hover":  "#2ea043",
    "yellow":       "#d29922",
    "red":          "#da3633",
    "red_hover":    "#f85149",
    "cyan":         "#39d353",
}


class StatusIndicator(ctk.CTkFrame):
    """A small colored dot + label to show current status."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.dot = ctk.CTkLabel(
            self, text="●", font=ctk.CTkFont(size=14),
            text_color=COLORS["green"], width=20
        )
        self.dot.pack(side="left", padx=(0, 6))

        self.label = ctk.CTkLabel(
            self, text="Ready", font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_dim"]
        )
        self.label.pack(side="left")

    def set(self, text, color):
        self.label.configure(text=text)
        self.dot.configure(text_color=color)


class AutoTyperApp:
    """Main Auto Typer application."""

    def __init__(self):
        # ── Keyboard controller (pynput) ──
        self.keyboard = Controller()
        self.stop_event = threading.Event()
        self.is_typing = False

        # ── Window ──
        ctk.set_appearance_mode("dark")
        self.app = ctk.CTk()
        self.app.title("Auto Typer")
        self.app.geometry("620x720")
        self.app.minsize(520, 620)
        self.app.configure(fg_color=COLORS["bg_dark"])

        # Try to set icon (non-critical if it fails)
        try:
            self.app.iconbitmap(default="")
        except Exception:
            pass

        self._build_ui()
        self._start_escape_listener()

    # ─── UI Construction ─────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self.app, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))

        title = ctk.CTkLabel(
            header, text="⌨  Auto Typer",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=COLORS["text"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Paste your text, click Start, switch to your target — typing begins after the countdown.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_dim"], wraplength=560, justify="left"
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # ── Text Input Card ──
        text_card = ctk.CTkFrame(
            self.app, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1, border_color=COLORS["border"]
        )
        text_card.pack(fill="both", expand=True, padx=24, pady=(16, 0))

        text_label = ctk.CTkLabel(
            text_card, text="Text to type",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text"]
        )
        text_label.pack(anchor="w", padx=16, pady=(14, 6))

        self.text_area = ctk.CTkTextbox(
            text_card, font=ctk.CTkFont(family="Consolas", size=14),
            fg_color=COLORS["bg_input"], text_color=COLORS["text"],
            border_width=1, border_color=COLORS["border"],
            corner_radius=8, wrap="word", height=200
        )
        self.text_area.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Character count
        self.char_count = ctk.CTkLabel(
            text_card, text="0 characters",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_dim"]
        )
        self.char_count.pack(anchor="e", padx=16, pady=(0, 10))
        self.text_area.bind("<KeyRelease>", self._update_char_count)

        # ── Settings Card ──
        settings_card = ctk.CTkFrame(
            self.app, fg_color=COLORS["bg_card"],
            corner_radius=12, border_width=1, border_color=COLORS["border"]
        )
        settings_card.pack(fill="x", padx=24, pady=(12, 0))

        # Typing Speed
        speed_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        speed_frame.pack(fill="x", padx=16, pady=(14, 4))

        speed_header = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_header.pack(fill="x")

        ctk.CTkLabel(
            speed_header, text="Typing Speed",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        self.speed_value_label = ctk.CTkLabel(
            speed_header, text="50 chars/sec",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"]
        )
        self.speed_value_label.pack(side="right")

        self.speed_slider = ctk.CTkSlider(
            speed_frame, from_=5, to=2000, number_of_steps=399,
            fg_color=COLORS["border"], progress_color=COLORS["accent_dim"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            command=self._on_speed_change
        )
        self.speed_slider.set(50)
        self.speed_slider.pack(fill="x", pady=(6, 0))

        # Start Delay
        delay_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        delay_frame.pack(fill="x", padx=16, pady=(10, 14))

        delay_header = ctk.CTkFrame(delay_frame, fg_color="transparent")
        delay_header.pack(fill="x")

        ctk.CTkLabel(
            delay_header, text="Start Delay",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        self.delay_value_label = ctk.CTkLabel(
            delay_header, text="3 seconds",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["accent"]
        )
        self.delay_value_label.pack(side="right")

        self.delay_slider = ctk.CTkSlider(
            delay_frame, from_=1, to=10, number_of_steps=9,
            fg_color=COLORS["border"], progress_color=COLORS["accent_dim"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            command=self._on_delay_change
        )
        self.delay_slider.set(3)
        self.delay_slider.pack(fill="x", pady=(6, 0))

        # ── Action Buttons ──
        btn_frame = ctk.CTkFrame(self.app, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(16, 0))

        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶  START TYPING", height=54,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=COLORS["green"], hover_color=COLORS["green_hover"],
            text_color="#ffffff", corner_radius=10,
            command=self._on_start
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="■  STOP", height=54,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=COLORS["border"], hover_color=COLORS["red_hover"],
            text_color=COLORS["text_dim"], corner_radius=10,
            state="disabled", command=self._on_stop
        )
        self.stop_btn.pack(side="right", expand=True, fill="x", padx=(8, 0))

        # ── Footer / Status ──
        footer = ctk.CTkFrame(self.app, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(14, 18))

        self.status = StatusIndicator(footer)
        self.status.pack(side="left")

        esc_hint = ctk.CTkLabel(
            footer, text="Press  Esc  to stop anytime",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_dim"]
        )
        esc_hint.pack(side="right")

    # ─── Slider Callbacks ────────────────────────────────────────────────

    def _on_speed_change(self, value):
        v = int(value)
        self.speed_value_label.configure(text=f"{v} chars/sec")

    def _on_delay_change(self, value):
        v = int(value)
        self.delay_value_label.configure(text=f"{v} second{'s' if v != 1 else ''}")

    def _update_char_count(self, _event=None):
        text = self.text_area.get("1.0", "end-1c")
        n = len(text)
        self.char_count.configure(text=f"{n:,} character{'s' if n != 1 else ''}")

    # ─── Escape Listener (global, runs in background) ────────────────────

    def _start_escape_listener(self):
        def on_press(key):
            if key == Key.esc and self.is_typing:
                self._on_stop()

        listener = Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    # ─── Start / Stop Logic ──────────────────────────────────────────────

    def _on_start(self):
        text = self.text_area.get("1.0", "end-1c")
        if not text.strip():
            self.status.set("Nothing to type!", COLORS["red"])
            return

        self.stop_event.clear()
        self.is_typing = True

        # UI state
        self.start_btn.configure(state="disabled", fg_color=COLORS["border"])
        self.stop_btn.configure(state="normal", fg_color="#da3633", text_color="#ffffff")
        self.text_area.configure(state="disabled")

        delay = int(self.delay_slider.get())
        speed = int(self.speed_slider.get())

        thread = threading.Thread(
            target=self._typing_worker, args=(text, delay, speed), daemon=True
        )
        thread.start()

    def _on_stop(self):
        self.stop_event.set()

    def _reset_ui(self, status_text, status_color):
        """Reset UI to idle state (must be called from main thread)."""
        self.is_typing = False
        self.start_btn.configure(state="normal", fg_color=COLORS["green"])
        self.stop_btn.configure(state="disabled", fg_color=COLORS["border"], text_color=COLORS["text_dim"])
        self.text_area.configure(state="normal")
        self.status.set(status_text, status_color)

    # ─── Typing Worker (runs in background thread) ───────────────────────

    def _typing_worker(self, text, delay, speed):
        """Countdown → type each character with pynput Controller."""

        # ── Countdown ──
        for remaining in range(delay, 0, -1):
            if self.stop_event.is_set():
                self.app.after(0, self._reset_ui, "Cancelled", COLORS["red"])
                return
            self.app.after(
                0, self.status.set,
                f"Starting in {remaining}…  (switch to target window now)",
                COLORS["yellow"]
            )
            time.sleep(1)

        if self.stop_event.is_set():
            self.app.after(0, self._reset_ui, "Cancelled", COLORS["red"])
            return

        # ── Type ──
        interval = 1.0 / speed
        total = len(text)
        self.app.after(0, self.status.set, f"Typing…  0 / {total}", COLORS["accent"])

        for i, char in enumerate(text):
            if self.stop_event.is_set():
                self.app.after(
                    0, self._reset_ui,
                    f"Stopped at {i}/{total} characters", COLORS["red"]
                )
                return

            # Simulate real key events
            if char == '\n':
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
            elif char == '\t':
                self.keyboard.press(Key.tab)
                self.keyboard.release(Key.tab)
            else:
                # type() sends proper keydown → char → keyup OS events
                self.keyboard.type(char)

            # Update progress every 10 chars (avoid UI flooding)
            if i % 10 == 0:
                progress = i + 1
                self.app.after(
                    0, self.status.set,
                    f"Typing…  {progress} / {total}", COLORS["accent"]
                )

            time.sleep(interval)

        # ── Done ──
        self.app.after(0, self._reset_ui, f"Done — {total} characters typed ✓", COLORS["green"])

    # ─── Run ─────────────────────────────────────────────────────────────

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    app = AutoTyperApp()
    app.run()
