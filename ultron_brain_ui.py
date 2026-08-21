from __future__ import annotations

import math
import os
import random
import tkinter as tk
from dataclasses import dataclass

import customtkinter as ctk


VOID = "#030304"
PANEL = "#09090B"
PANEL_ALT = "#101014"
LINE = "#3C1015"
LINE_BRIGHT = "#8D1D29"
RED = "#FF3142"
RED_DIM = "#A71826"
RED_DARK = "#4A0810"
WHITE = "#F5F5F7"
MUTED = "#85858D"
GREEN = "#4DFF9A"
AMBER = "#FFB84D"


@dataclass
class BrainNode:
    key: str
    label: str
    description: str
    ring: int
    angle: float
    kind: str = "module"


class BrainWindow(ctk.CTkToplevel):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.app = app
        self.title("ULTRON // Neural Architecture")
        self.geometry("1280x780")
        self.minsize(980, 650)
        self.configure(fg_color=VOID)
        self.transient(app)

        self.phase = 0.0
        self.selected: str | None = None
        self.node_positions: dict[str, tuple[float, float]] = {}
        self.nodes = self._build_nodes()
        self.links = self._build_links()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_network()
        self._build_inspector()
        self.after(30, self._animate)
        self.after(800, self._refresh_status)

    def _build_nodes(self) -> list[BrainNode]:
        return [
            BrainNode("core", "PRIME CORE", "Central routing and cognition state.", 0, 0, "core"),
            BrainNode("ai", "AI COGNITION", "OpenAI/Gemini conversational reasoning provider.", 1, 0),
            BrainNode("language", "LANGUAGE ES/EN", "Automatic bilingual English and Chilean Spanish handling.", 1, 60),
            BrainNode("vision", "VISION", "On-demand screen understanding with short-lived visual context.", 1, 120),
            BrainNode("windows", "WINDOWS CONTROL", "Allowlisted PC actions and permission-gated commands.", 1, 180),
            BrainNode("memory", "MEMORY", "Private local memories and learned command mappings.", 1, 240),
            BrainNode("voice", "VOICE", "Speech recognition and speech synthesis.", 1, 300),
            BrainNode("health", "DIAGNOSTICS", "Checks AI, microphone, vision, telemetry and modules.", 2, 15),
            BrainNode("focus", "FOCUS MODE", "Short action-first response mode.", 2, 60),
            BrainNode("awareness", "WINDOW AWARENESS", "Reads the active Windows application and title locally.", 2, 105),
            BrainNode("screen_context", "SCREEN CONTEXT", "Temporary last-screen analysis for follow-up questions.", 2, 150),
            BrainNode("permissions", "PERMISSION GATE", "Requires confirmation for protected computer actions.", 2, 195),
            BrainNode("telemetry", "TELEMETRY", "CPU, RAM, disk and runtime activity state.", 2, 240),
            BrainNode("planner", "PLANNER", "Multi-step execution planning module.", 2, 285, "future"),
            BrainNode("files", "FILE INTELLIGENCE", "Local file discovery and context module.", 2, 330, "future"),
        ]

    def _build_links(self) -> list[tuple[str, str]]:
        links = []
        ring1 = ["ai", "language", "vision", "windows", "memory", "voice"]
        for node in ring1:
            links.append(("core", node))
        links.extend([
            ("ai", "language"), ("ai", "vision"), ("vision", "screen_context"),
            ("vision", "awareness"), ("windows", "permissions"), ("windows", "awareness"),
            ("memory", "focus"), ("memory", "screen_context"), ("voice", "language"),
            ("health", "telemetry"), ("health", "voice"), ("health", "vision"),
            ("planner", "permissions"), ("planner", "windows"), ("files", "planner"),
            ("files", "memory"), ("telemetry", "core"),
        ])
        return links

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, height=72, fg_color=VOID, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="ULTRON // NEURAL ARCHITECTURE", font=ctk.CTkFont("Segoe UI", 24, "bold"), text_color=WHITE).grid(row=0, column=0, sticky="w", padx=8)
        self.activity_label = ctk.CTkLabel(header, text="COGNITION // STANDING BY", font=ctk.CTkFont("Consolas", 10, "bold"), text_color=RED)
        self.activity_label.grid(row=0, column=1)
        ctk.CTkButton(header, text="CLOSE", width=80, command=self.destroy, fg_color="transparent", border_width=1, border_color=LINE_BRIGHT, hover_color=RED_DARK).grid(row=0, column=2, padx=8)

    def _build_network(self) -> None:
        frame = ctk.CTkFrame(self, fg_color=PANEL, border_width=1, border_color=LINE, corner_radius=5)
        frame.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=12)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(frame, height=40, fg_color=PANEL_ALT, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(top, text="LIVE BRAIN NETWORK", font=ctk.CTkFont("Consolas", 10, "bold"), text_color=RED).pack(side="left", padx=12)
        self.stats = ctk.CTkLabel(top, text="", font=ctk.CTkFont("Consolas", 8), text_color=MUTED)
        self.stats.pack(side="right", padx=12)
        self.canvas = tk.Canvas(frame, bg=VOID, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self._on_click)

    def _build_inspector(self) -> None:
        panel = ctk.CTkFrame(self, width=310, fg_color=PANEL, border_width=1, border_color=LINE, corner_radius=5)
        panel.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=12)
        panel.grid_propagate(False)
        ctk.CTkLabel(panel, text="CORE INSPECTOR", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=RED).pack(anchor="w", padx=16, pady=(18, 6))
        self.node_name = ctk.CTkLabel(panel, text="PRIME CORE", font=ctk.CTkFont("Segoe UI", 22, "bold"), text_color=WHITE, wraplength=270, justify="left")
        self.node_name.pack(anchor="w", padx=16, pady=(8, 4))
        self.node_status = ctk.CTkLabel(panel, text="ONLINE", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=GREEN)
        self.node_status.pack(anchor="w", padx=16)
        self.node_desc = ctk.CTkLabel(panel, text="Click any neural node to inspect it.", font=ctk.CTkFont("Consolas", 10), text_color=MUTED, wraplength=270, justify="left")
        self.node_desc.pack(anchor="w", padx=16, pady=(14, 20))

        ctk.CTkLabel(panel, text="ACTIVE SYSTEMS", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=RED).pack(anchor="w", padx=16, pady=(4, 8))
        self.system_text = ctk.CTkTextbox(panel, height=230, fg_color=VOID, border_width=1, border_color=LINE, text_color=WHITE, font=ctk.CTkFont("Consolas", 9))
        self.system_text.pack(fill="x", padx=14)
        self.system_text.configure(state="disabled")

        ctk.CTkLabel(panel, text="NETWORK ACTIVITY", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=RED).pack(anchor="w", padx=16, pady=(18, 6))
        self.activity_bar = ctk.CTkProgressBar(panel, height=8, fg_color=LINE, progress_color=RED)
        self.activity_bar.pack(fill="x", padx=16)
        self.activity_bar.set(0.18)
        self.activity_pct = ctk.CTkLabel(panel, text="18%", font=ctk.CTkFont("Consolas", 9), text_color=MUTED)
        self.activity_pct.pack(anchor="e", padx=16, pady=(5, 0))

    def _status_map(self) -> dict[str, tuple[bool, str]]:
        brain = self.app.brain
        ai = getattr(brain.ai, "available", False)
        provider = getattr(brain.ai, "provider", "local")
        voice = getattr(self.app.voice, "available", False)
        focus = brain.memory.get_setting("ultron_focus", "off") == "on"
        vision = bool(os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        return {
            "core": (True, "ONLINE"),
            "ai": (ai, provider.upper() if ai else "LOCAL"),
            "language": (True, "ES / EN AUTO"),
            "vision": (vision, "READY" if vision else "NO AI KEY"),
            "windows": (os.name == "nt", "ONLINE" if os.name == "nt" else "UNAVAILABLE"),
            "memory": (True, f"{len(brain.memory.list_memories(99))} MEMORIES"),
            "voice": (voice, "ONLINE" if voice else "OFFLINE"),
            "health": (True, "ONLINE"),
            "focus": (True, "ON" if focus else "STANDBY"),
            "awareness": (os.name == "nt", "READY" if os.name == "nt" else "UNAVAILABLE"),
            "screen_context": (True, "SESSION ONLY"),
            "permissions": (True, "ARMED"),
            "telemetry": (True, "LIVE"),
            "planner": (False, "NEXT BUILD"),
            "files": (False, "NEXT BUILD"),
        }

    def _refresh_status(self) -> None:
        status = self._status_map()
        lines = []
        for node in self.nodes:
            ok, label = status.get(node.key, (False, "UNKNOWN"))
            glyph = "●" if ok else "○"
            lines.append(f"{glyph} {node.label:<19} {label}")
        self.system_text.configure(state="normal")
        self.system_text.delete("1.0", "end")
        self.system_text.insert("end", "\n".join(lines))
        self.system_text.configure(state="disabled")
        self.after(1200, self._refresh_status)

    def _on_click(self, event) -> None:
        if not self.node_positions:
            return
        best = None
        for key, (x, y) in self.node_positions.items():
            dist = math.hypot(event.x - x, event.y - y)
            if best is None or dist < best[0]:
                best = (dist, key)
        if best and best[0] <= 34:
            self.selected = best[1]
            node = next(n for n in self.nodes if n.key == self.selected)
            ok, status = self._status_map().get(node.key, (False, "UNKNOWN"))
            self.node_name.configure(text=node.label)
            self.node_status.configure(text=status, text_color=GREEN if ok else AMBER)
            self.node_desc.configure(text=node.description)

    def _animate(self) -> None:
        c = self.canvas
        w = max(c.winfo_width(), 10)
        h = max(c.winfo_height(), 10)
        c.delete("all")
        cx, cy = w / 2, h / 2
        radius1 = min(w, h) * 0.20
        radius2 = min(w, h) * 0.36
        self.node_positions = {}

        # faint concentric architecture rings
        for r, color in ((radius1, "#311016"), (radius2, "#251014"), (radius2 * 1.08, "#15090B")):
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=1)

        # deterministic positions with a subtle living drift
        for node in self.nodes:
            if node.ring == 0:
                x, y = cx, cy
            else:
                r = radius1 if node.ring == 1 else radius2
                theta = math.radians(node.angle + math.sin(self.phase + node.angle) * 1.5)
                x = cx + math.cos(theta) * r
                y = cy + math.sin(theta) * r
            self.node_positions[node.key] = (x, y)

        # neural links
        activity = 1.0 if getattr(self.app, "processing", False) else (0.65 if getattr(self.app, "listening", False) else 0.22)
        for index, (a, b) in enumerate(self.links):
            if a not in self.node_positions or b not in self.node_positions:
                continue
            x1, y1 = self.node_positions[a]
            x2, y2 = self.node_positions[b]
            pulse = (math.sin(self.phase * 2 + index * 0.7) + 1) / 2
            color = RED_DIM if pulse > 0.72 and activity > 0.4 else "#321017"
            c.create_line(x1, y1, x2, y2, fill=color, width=2 if color == RED_DIM else 1)

        statuses = self._status_map()
        for node in self.nodes:
            x, y = self.node_positions[node.key]
            ok, _ = statuses.get(node.key, (False, "UNKNOWN"))
            selected = node.key == self.selected
            if node.kind == "core":
                size = 28 + math.sin(self.phase * 2) * 3 + activity * 5
                c.create_oval(x-size, y-size, x+size, y+size, fill=RED_DARK, outline=RED, width=3)
                c.create_oval(x-9, y-9, x+9, y+9, fill=RED, outline="")
            else:
                size = 9 if node.ring == 1 else 6
                fill = GREEN if ok and node.kind != "future" else (AMBER if node.kind == "future" else MUTED)
                if selected:
                    c.create_oval(x-size-7, y-size-7, x+size+7, y+size+7, outline=RED, width=2)
                c.create_oval(x-size, y-size, x+size, y+size, fill=fill, outline=WHITE if node.ring == 1 else "")
            if node.ring != 2 or selected:
                c.create_text(x, y + 18, text=node.label, fill=WHITE if selected else MUTED, font=("Consolas", 7, "bold" if selected else "normal"))

        # moving data particles
        for i in range(12):
            if not self.links:
                break
            a, b = self.links[i % len(self.links)]
            x1, y1 = self.node_positions[a]
            x2, y2 = self.node_positions[b]
            t = (self.phase * (0.20 + activity * 0.28) + i * 0.087) % 1.0
            x, y = x1 + (x2-x1)*t, y1 + (y2-y1)*t
            c.create_oval(x-2, y-2, x+2, y+2, fill=RED, outline="")

        pct = int(activity * 100)
        self.activity_bar.set(min(1.0, activity))
        self.activity_pct.configure(text=f"{pct}%")
        self.activity_label.configure(
            text="COGNITION // ACTIVE" if getattr(self.app, "processing", False) else ("AUDIO // LISTENING" if getattr(self.app, "listening", False) else "COGNITION // STANDING BY"),
            text_color=AMBER if getattr(self.app, "processing", False) else (GREEN if getattr(self.app, "listening", False) else RED),
        )
        self.stats.configure(text=f"NODES {len(self.nodes)}  //  LINKS {len(self.links)}  //  ACTIVITY {pct}%")
        self.phase += 0.055
        self.after(30, self._animate)


def install_brain_ui(UltronApp) -> None:
    """Attach a live brain-network panel to the existing ULTRON UI without replacing it."""
    if getattr(UltronApp, "_brain_ui_installed", False):
        return

    original_init = UltronApp.__init__

    def init_with_brain(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._brain_window = None

        def open_brain() -> None:
            current = getattr(self, "_brain_window", None)
            if current is not None:
                try:
                    if current.winfo_exists():
                        current.lift()
                        current.focus_force()
                        return
                except Exception:
                    pass
            self._brain_window = BrainWindow(self)

        self.open_brain = open_brain
        self.bind("<Control-b>", lambda _event: open_brain())
        button = ctk.CTkButton(
            self,
            text="BRAIN",
            command=open_brain,
            width=86,
            height=30,
            corner_radius=3,
            fg_color=RED_DARK,
            hover_color=RED_DIM,
            border_width=1,
            border_color=RED,
            text_color=WHITE,
            font=ctk.CTkFont("Consolas", 9, "bold"),
        )
        button.place(relx=0.5, y=23, anchor="n")

    UltronApp.__init__ = init_with_brain
    UltronApp._brain_ui_installed = True
