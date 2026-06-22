"""
 ██████╗  ██╗██████╗  █████╗  █████╗     ████████╗ ██████╗ ██╗   ██╗ ██████╗██╗  ██╗
██╔══██╗ ██║██╔══██╗██╔══██╗██╔══██╗       ██╔══╝██╔═══██╗██║   ██║██╔════╝██║  ██║
███████║ ██║██████╔╝███████║╚██████╔╝       ██║   ██║   ██║██║   ██║██║     ███████║
██╔══██║ ██║██╔══██╗██╔══██║ ╚═══██╗        ██║   ██║   ██║██║   ██║██║     ██╔══██║
██║  ██║ ██║██║  ██║██║  ██║ █████╔╝        ██║   ╚██████╔╝╚██████╔╝╚██████╗██║  ██║
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚════╝         ╚═╝    ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝
                        v3.0 ULTRA PREMIUM  — Edição Cruzeiro
        Automação • IA • Voz • HUD Holográfico • Clipboard Intelligence • Macros • Multi-Perfis
        100% Gratuito
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import keyboard
import os, json, sys, re, time, glob, threading, webbrowser
import winreg
import pyautogui
import pystray
from pystray import MenuItem as item
import psutil
import requests

# ── Importações opcionais ──────────────────────────────────────────────────
try:
    import pyperclip
    PYPERCLIP_OK = True
except ImportError:
    PYPERCLIP_OK = False

try:
    import speech_recognition as sr
    VOICE_OK = True
except ImportError:
    VOICE_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  PALETA DE CORES — Cruzeiro Premium (Preto / Azul / Dourado / Neon)
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "bg":      "#0B0E14",   # Fundo principal — preto profundo
    "card":    "#151921",   # Cards escuros
    "card2":   "#1A2030",   # Cards ligeiramente mais claros
    "blue":    "#004B8D",   # Azul Cruzeiro
    "gold":    "#C5A059",   # Dourado Premium
    "text":    "#E1E1E1",   # Texto branco-acinzentado
    "accent":  "#00A8FF",   # Azul neon — detalhe principal
    "green":   "#00FF88",   # Verde neon — OK / RAM
    "red":     "#FF4444",   # Vermelho — perigo / grava
    "purple":  "#8B5CF6",   # Roxo — IA
    "orange":  "#F59E0B",   # Laranja — mouse click
    "border":  "#2A2F3A",   # Bordas sutis
    "dim":     "#444455",   # Texto apagado
}

APP_NAME = "AIra9Touch"
VERSION  = "v3.0 ULTRA"
CFG_FILE = "config_v3.json"

# ── Config padrão ─────────────────────────────────────────────────────────
DEFAULT_CFG = {
    "current_profile": "default",
    "profiles": {
        "default": {"shortcuts": {}, "macros": {}}
    },
    "system_active": True,
    "auto_start":    False,
    "ai": {
        "enabled": False,
        "api_key": "",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "model":   "llama3-8b-8192",
        "hotkey":  "ctrl+alt+a",
    },
    "voice": {
        "enabled":  False,
        "language": "pt-BR",
        "hotkey":   "ctrl+alt+v",
    },
    "clipboard": {"enabled": True},
    "hud": {
        "enabled": False,
        "hotkey":  "ctrl+alt+h",
    },
}


# ══════════════════════════════════════════════════════════════════════════════
#  CLASSE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
class AIra9TouchApp:

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title(f"{APP_NAME} {VERSION}")
        self.root.geometry("740x860")
        self.root.minsize(700, 780)

        ctk.set_appearance_mode("dark")
        self.root.configure(fg_color=C["bg"])

        # ── Variáveis de estado ─────────────────────────────────────────
        self.is_active        = tk.BooleanVar(value=True)
        self.auto_start       = tk.BooleanVar(value=False)
        self.ai_enabled       = tk.BooleanVar(value=False)
        self.voice_enabled    = tk.BooleanVar(value=False)
        self.clipboard_on     = tk.BooleanVar(value=True)
        self.hud_enabled      = tk.BooleanVar(value=False)

        # ── Estado interno ──────────────────────────────────────────────
        self.cfg:          dict  = {}
        self.hud_window          = None
        self.voice_listening     = False
        self._last_clipboard     = ""

        # Macro recorder
        self.recording_macro     = False
        self.macro_events:  list = []
        self._macro_hook         = None
        self._macro_t0:   float  = 0.0

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self._load_config()
        self._build_ui()
        self._create_tray_icon()
        self._reload_hotkeys()
        self._start_bg_threads()

    # ═══════════════════════════════════════════════════════════════════════
    #  CONFIG
    # ═══════════════════════════════════════════════════════════════════════
    def _load_config(self):
        if os.path.exists(CFG_FILE):
            try:
                with open(CFG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge preservando defaults
                self.cfg = dict(DEFAULT_CFG)
                for k, v in saved.items():
                    if isinstance(v, dict) and k in self.cfg:
                        self.cfg[k] = {**DEFAULT_CFG.get(k, {}), **v}
                    else:
                        self.cfg[k] = v
            except Exception:
                self.cfg = dict(DEFAULT_CFG)
        else:
            self.cfg = dict(DEFAULT_CFG)

        # Sync BooleanVars
        self.is_active.set(self.cfg.get("system_active", True))
        self.auto_start.set(self._check_auto_start())
        self.ai_enabled.set(self.cfg["ai"]["enabled"])
        self.voice_enabled.set(self.cfg["voice"]["enabled"])
        self.clipboard_on.set(self.cfg["clipboard"]["enabled"])
        self.hud_enabled.set(self.cfg["hud"]["enabled"])

    def _save_config(self):
        self.cfg["system_active"]       = self.is_active.get()
        self.cfg["ai"]["enabled"]        = self.ai_enabled.get()
        self.cfg["voice"]["enabled"]     = self.voice_enabled.get()
        self.cfg["clipboard"]["enabled"] = self.clipboard_on.get()
        self.cfg["hud"]["enabled"]       = self.hud_enabled.get()
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, indent=4, ensure_ascii=False)

    # ── Perfil ativo ──────────────────────────────────────────────────────
    def _profile(self) -> dict:
        p = self.cfg.get("current_profile", "default")
        if p not in self.cfg["profiles"]:
            self.cfg["profiles"][p] = {"shortcuts": {}, "macros": {}}
        return self.cfg["profiles"][p]

    @property
    def shortcuts(self) -> dict:
        return self._profile().setdefault("shortcuts", {})

    @property
    def macros(self) -> dict:
        return self._profile().setdefault("macros", {})

    def _check_auto_start(self) -> bool:
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            winreg.QueryValueEx(k, APP_NAME)
            winreg.CloseKey(k)
            return True
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════════════════
    #  INTERFACE
    # ═══════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()
        self._build_stats_bar()
        self._build_profile_bar()
        self._build_tabs()
        self._build_footer()

    # ── Header ────────────────────────────────────────────────────────────
    def _build_header(self):
        h = ctk.CTkFrame(self.root, fg_color="transparent")
        h.pack(fill="x", padx=30, pady=(25, 4))

        ctk.CTkLabel(h, text="AIRA9",
            font=ctk.CTkFont("Segoe UI", 30, "bold"),
            text_color=C["blue"]).pack(side="left")
        ctk.CTkLabel(h, text="TOUCH",
            font=ctk.CTkFont("Segoe UI", 30, "bold"),
            text_color=C["gold"]).pack(side="left", padx=(2, 0))
        ctk.CTkLabel(h, text=f"  {VERSION}",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=C["dim"]).pack(side="left", pady=(8, 0))

        ctk.CTkSwitch(h, text="SISTEMA ATIVO",
            variable=self.is_active,
            command=lambda: (self._save_config(), self._reload_hotkeys()),
            progress_color=C["blue"],
            button_color=C["gold"],
            button_hover_color="#A38446",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="right")

    # ── Stats Bar (CPU / RAM / TEMP / DISCO) ──────────────────────────────
    def _build_stats_bar(self):
        bar = ctk.CTkFrame(self.root, fg_color=C["card"], height=34, corner_radius=8)
        bar.pack(fill="x", padx=30, pady=(4, 0))
        bar.pack_propagate(False)

        def stat(text, color, side="left", padx=10):
            return ctk.CTkLabel(bar, text=text,
                font=ctk.CTkFont("Consolas", 10), text_color=color,
                anchor="w").pack(side=side, padx=padx)

        def sep():
            ctk.CTkLabel(bar, text="│", text_color=C["border"]).pack(side="left")

        self.lbl_cpu  = ctk.CTkLabel(bar, text="CPU: --%",   font=ctk.CTkFont("Consolas", 10), text_color=C["accent"])
        self.lbl_ram  = ctk.CTkLabel(bar, text="RAM: --GB",  font=ctk.CTkFont("Consolas", 10), text_color=C["green"])
        self.lbl_temp = ctk.CTkLabel(bar, text="TEMP: --°C", font=ctk.CTkFont("Consolas", 10), text_color=C["gold"])
        self.lbl_disk = ctk.CTkLabel(bar, text="DISCO: --%", font=ctk.CTkFont("Consolas", 10), text_color=C["purple"])
        self.lbl_time = ctk.CTkLabel(bar, text="00:00:00",   font=ctk.CTkFont("Consolas", 10), text_color=C["text"])

        for w in [self.lbl_cpu, self.lbl_ram, self.lbl_temp, self.lbl_disk]:
            w.pack(side="left", padx=10)
            ctk.CTkLabel(bar, text="│", text_color=C["border"]).pack(side="left")
        self.lbl_time.pack(side="right", padx=10)

    # ── Profile Bar ───────────────────────────────────────────────────────
    def _build_profile_bar(self):
        pb = ctk.CTkFrame(self.root, fg_color="transparent")
        pb.pack(fill="x", padx=30, pady=(8, 0))

        ctk.CTkLabel(pb, text="PERFIL:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["gold"]).pack(side="left")

        self.profile_var  = tk.StringVar(value=self.cfg.get("current_profile", "default"))
        self.profile_names = list(self.cfg["profiles"].keys())

        self.profile_menu = ctk.CTkOptionMenu(pb,
            values=self.profile_names,
            variable=self.profile_var,
            command=self._switch_profile,
            fg_color=C["card"], button_color=C["blue"],
            dropdown_fg_color=C["card"],
            font=ctk.CTkFont(size=10), height=28, width=130)
        self.profile_menu.pack(side="left", padx=8)

        _s = {"height": 28, "font": ctk.CTkFont(size=10, weight="bold"),
              "fg_color": "transparent", "border_width": 1}

        ctk.CTkButton(pb, text="+ NOVO PERFIL",
            border_color=C["gold"], **_s,
            command=self._new_profile).pack(side="left")

        ctk.CTkButton(pb, text="✕ REMOVER",
            border_color=C["red"], text_color=C["red"], **_s,
            command=self._remove_profile).pack(side="left", padx=4)

    # ── Tabs ──────────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(self.root,
            fg_color=C["card"],
            segmented_button_fg_color=C["bg"],
            segmented_button_selected_color=C["blue"],
            segmented_button_selected_hover_color="#003D73",
            segmented_button_unselected_color=C["card"],
            segmented_button_unselected_hover_color=C["card2"],
            text_color=C["text"],
            corner_radius=12)
        self.tabs.pack(fill="both", expand=True, padx=30, pady=10)

        for name in ["⚡ ATALHOS", "⏺ MACROS", "🤖 IA", "🎙 VOZ", "⚙ CONFIG"]:
            self.tabs.add(name)

        self._tab_atalhos()
        self._tab_macros()
        self._tab_ia()
        self._tab_voz()
        self._tab_config()

    # ── Footer ────────────────────────────────────────────────────────────
    def _build_footer(self):
        f = ctk.CTkFrame(self.root, fg_color="transparent")
        f.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(f, text="● MODO ADMINISTRADOR",
            text_color=C["accent"],
            font=ctk.CTkFont("Consolas", 9, "bold")).pack(side="left")
        ctk.CTkLabel(f, text="Tecnologia de Automação Premium — Edição Cruzeiro",
            text_color=C["dim"],
            font=ctk.CTkFont(size=9)).pack(side="right")

    # ═══════════════════════════════════════════════════════════════════════
    #  TAB ⚡ ATALHOS
    # ═══════════════════════════════════════════════════════════════════════
    def _tab_atalhos(self):
        tab = self.tabs.tab("⚡ ATALHOS")

        # Listbox
        lf = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        lf.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        ctk.CTkLabel(lf, text="ATALHOS CONFIGURADOS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["gold"]).pack(padx=12, pady=(8, 4), anchor="w")

        self.listbox = tk.Listbox(lf,
            bg=C["card2"], fg=C["text"],
            font=("Consolas", 11),
            borderwidth=0, highlightthickness=0,
            selectbackground=C["blue"],
            selectforeground="white",
            activestyle="none")
        self.listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Botões
        bf = ctk.CTkFrame(tab, fg_color="transparent")
        bf.pack(fill="x", padx=10, pady=5)

        _s = {"height": 38, "corner_radius": 8,
              "font": ctk.CTkFont(size=11, weight="bold"), "border_width": 1}

        matrix = [
            ("+ PROGRAMA/ARQ",   C["blue"],  "#003D73", C["gold"],  self._add_file,       0, 0),
            ("+ PASTA",          C["blue"],  "#003D73", C["gold"],  self._add_folder,     0, 1),
            ("+ TEXTO AUTO",     C["card2"], "#252C3D", C["gold"],  self._add_text,       1, 0),
            ("+ CLIQUE MOUSE",   C["card2"], "#252C3D", C["gold"],  self._add_click,      1, 1),
            ("+ REPRODUZIR PASTA", C["card2"], "#252C3D", C["gold"], self._add_media,     2, 0),
            ("+ URL / SITE",     C["card2"], "#252C3D", C["gold"],  self._add_url,        2, 1),
        ]
        for txt, fg, hov, brd, cmd, r, col in matrix:
            ctk.CTkButton(bf, text=txt,
                fg_color=fg, hover_color=hov, border_color=brd,
                command=cmd, **_s
            ).grid(row=r, column=col, padx=4, pady=4, sticky="ew")

        ctk.CTkButton(bf, text="✕  REMOVER SELECIONADO",
            fg_color="#441111", hover_color="#661111",
            border_color=C["red"],
            command=self._remove_shortcut, **_s
        ).grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        bf.columnconfigure(0, weight=1)
        bf.columnconfigure(1, weight=1)

        ctk.CTkCheckBox(tab, text="Iniciar com o Windows",
            variable=self.auto_start,
            command=self._toggle_startup,
            border_color=C["gold"],
            hover_color=C["blue"],
            checkmark_color=C["gold"]
        ).pack(padx=10, pady=6, anchor="w")

    # ═══════════════════════════════════════════════════════════════════════
    #  TAB ⏺ MACROS
    # ═══════════════════════════════════════════════════════════════════════
    def _tab_macros(self):
        tab = self.tabs.tab("⏺ MACROS")

        # Cabeçalho informativo
        info = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        info.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(info, text="⏺  GRAVADOR DE MACROS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["gold"]).pack(padx=12, pady=(10, 2), anchor="w")
        ctk.CTkLabel(info,
            text="Grave qualquer sequência de teclas e cliques — reproduza com 1 atalho.",
            font=ctk.CTkFont(size=9), text_color=C["dim"],
            wraplength=580).pack(padx=12, pady=(0, 10), anchor="w")

        # Controles de gravação
        ctrl = ctk.CTkFrame(tab, fg_color="transparent")
        ctrl.pack(fill="x", padx=10, pady=4)

        self.macro_name_entry = ctk.CTkEntry(ctrl,
            placeholder_text="Nome da macro...",
            fg_color=C["card2"], border_color=C["gold"],
            width=190, height=38)
        self.macro_name_entry.pack(side="left", padx=(0, 6))

        self.btn_record = ctk.CTkButton(ctrl,
            text="⏺  INICIAR GRAVAÇÃO",
            fg_color="#1A0A0A", hover_color="#330000",
            border_color=C["red"], border_width=1,
            height=38, font=ctk.CTkFont(size=11, weight="bold"),
            command=self._toggle_macro_record)
        self.btn_record.pack(side="left", padx=4)

        self.lbl_rec = ctk.CTkLabel(ctrl, text="◉ PRONTO",
            font=ctk.CTkFont("Consolas", 11, "bold"),
            text_color=C["dim"])
        self.lbl_rec.pack(side="left", padx=10)

        # Lista de macros
        lf = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        lf.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(lf, text="MACROS SALVAS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["gold"]).pack(padx=12, pady=(8, 4), anchor="w")

        self.macro_listbox = tk.Listbox(lf,
            bg=C["card2"], fg=C["text"],
            font=("Consolas", 11),
            borderwidth=0, highlightthickness=0,
            selectbackground=C["blue"],
            selectforeground="white",
            activestyle="none")
        self.macro_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Botões de macro
        mb = ctk.CTkFrame(tab, fg_color="transparent")
        mb.pack(fill="x", padx=10, pady=(0, 5))

        _s = {"height": 38, "corner_radius": 8,
              "font": ctk.CTkFont(size=11, weight="bold"), "border_width": 1}

        ctk.CTkButton(mb, text="▶  EXECUTAR",
            fg_color=C["blue"], hover_color="#003D73",
            border_color=C["gold"],
            command=self._run_selected_macro, **_s
        ).pack(side="left", padx=4, expand=True, fill="x")

        ctk.CTkButton(mb, text="🔑  DEFINIR ATALHO",
            fg_color=C["card2"], hover_color="#252C3D",
            border_color=C["gold"],
            command=self._set_macro_hotkey, **_s
        ).pack(side="left", padx=4, expand=True, fill="x")

        ctk.CTkButton(mb, text="✕  REMOVER",
            fg_color="#441111", hover_color="#661111",
            border_color=C["red"],
            command=self._remove_macro, **_s
        ).pack(side="left", padx=4, expand=True, fill="x")

    # ═══════════════════════════════════════════════════════════════════════
    #  TAB 🤖 IA
    # ═══════════════════════════════════════════════════════════════════════
    def _tab_ia(self):
        tab = self.tabs.tab("🤖 IA")

        # ── Toggle principal ──
        tog = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        tog.pack(fill="x", padx=10, pady=(10, 5))

        tr = ctk.CTkFrame(tog, fg_color="transparent")
        tr.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(tr, text="🤖  IA INTEGRADA",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["purple"]).pack(side="left")
        self.ai_switch = ctk.CTkSwitch(tr, text="",
            variable=self.ai_enabled,
            command=self._on_ai_toggle,
            progress_color=C["purple"],
            button_color=C["gold"])
        self.ai_switch.pack(side="right")

        ctk.CTkLabel(tog,
            text="⚠  API gratuita com limites diários — desative quando não estiver usando.",
            font=ctk.CTkFont(size=9), text_color=C["gold"],
            wraplength=580).pack(padx=12, pady=(0, 10), anchor="w")

        # ── Configuração ──
        self.ai_cfg_frame = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        self.ai_cfg_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.ai_cfg_frame, text="CONFIGURAÇÃO DA API",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["gold"]).pack(padx=12, pady=(10, 4), anchor="w")

        self.ai_entries: dict = {}
        for label, key, placeholder in [
            ("URL da API:", "api_url", "https://api.groq.com/openai/v1/chat/completions"),
            ("Modelo:",     "model",   "llama3-8b-8192"),
            ("Atalho:",     "hotkey",  "ctrl+alt+a"),
        ]:
            row = ctk.CTkFrame(self.ai_cfg_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=label, width=85,
                font=ctk.CTkFont(size=10)).pack(side="left")
            e = ctk.CTkEntry(row,
                placeholder_text=placeholder,
                fg_color=C["bg"], border_color=C["border"],
                height=28, font=ctk.CTkFont("Consolas", 10))
            e.pack(side="left", fill="x", expand=True)
            e.insert(0, self.cfg["ai"].get(key, ""))
            self.ai_entries[key] = e

        # API Key (oculta)
        kr = ctk.CTkFrame(self.ai_cfg_frame, fg_color="transparent")
        kr.pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(kr, text="API Key:", width=85,
            font=ctk.CTkFont(size=10)).pack(side="left")
        self.ai_key_entry = ctk.CTkEntry(kr,
            placeholder_text="gsk_xxxxxxx  (Groq — gratuito em groq.com)",
            fg_color=C["bg"], border_color=C["border"],
            show="•", height=28, font=ctk.CTkFont("Consolas", 10))
        self.ai_key_entry.pack(side="left", fill="x", expand=True)
        self.ai_key_entry.insert(0, self.cfg["ai"].get("api_key", ""))

        ctk.CTkButton(self.ai_cfg_frame, text="💾  SALVAR CONFIGURAÇÃO",
            fg_color=C["blue"], hover_color="#003D73",
            border_color=C["gold"], border_width=1,
            height=34, font=ctk.CTkFont(size=11, weight="bold"),
            command=self._save_ai_cfg
        ).pack(padx=12, pady=10, fill="x")

        # ── Chat rápido ──
        chat = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        chat.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(chat, text="CONSULTA RÁPIDA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["purple"]).pack(padx=12, pady=(10, 4), anchor="w")

        self.ai_output = ctk.CTkTextbox(chat,
            fg_color=C["bg"], text_color=C["text"],
            font=ctk.CTkFont("Consolas", 10),
            height=100, state="disabled")
        self.ai_output.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        ir = ctk.CTkFrame(chat, fg_color="transparent")
        ir.pack(fill="x", padx=12, pady=(0, 10))

        self.ai_input = ctk.CTkEntry(ir,
            placeholder_text="Faça uma pergunta... (Enter para enviar)",
            fg_color=C["bg"], border_color=C["purple"], height=36)
        self.ai_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.ai_input.bind("<Return>", lambda _: self._run_ai_query())

        ctk.CTkButton(ir, text="↵ ENVIAR",
            width=90, height=36,
            fg_color=C["purple"], hover_color="#7C3AED",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._run_ai_query
        ).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════
    #  TAB 🎙 VOZ
    # ═══════════════════════════════════════════════════════════════════════
    def _tab_voz(self):
        tab = self.tabs.tab("🎙 VOZ")

        tog = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        tog.pack(fill="x", padx=10, pady=(10, 5))

        tr = ctk.CTkFrame(tog, fg_color="transparent")
        tr.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(tr, text="🎙  COMANDOS DE VOZ",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["accent"]).pack(side="left")
        ctk.CTkSwitch(tr, text="",
            variable=self.voice_enabled,
            command=self._on_voice_toggle,
            progress_color=C["accent"],
            button_color=C["gold"]
        ).pack(side="right")

        status_clr  = C["green"] if VOICE_OK else C["red"]
        status_text = "✅ Módulo disponível (SpeechRecognition + PyAudio)" \
                      if VOICE_OK else \
                      "❌ Instale:  pip install SpeechRecognition pyaudio"
        ctk.CTkLabel(tog, text=status_text,
            font=ctk.CTkFont(size=9), text_color=status_clr,
            wraplength=580).pack(padx=12, pady=(0, 10), anchor="w")

        # Config
        cf = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        cf.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(cf, text="CONFIGURAÇÃO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["gold"]).pack(padx=12, pady=(10, 4), anchor="w")

        r1 = ctk.CTkFrame(cf, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(r1, text="Atalho de escuta:", width=140,
            font=ctk.CTkFont(size=10)).pack(side="left")
        self.voice_hotkey_e = ctk.CTkEntry(r1,
            fg_color=C["bg"], border_color=C["border"],
            height=28, font=ctk.CTkFont("Consolas", 10))
        self.voice_hotkey_e.pack(side="left", fill="x", expand=True)
        self.voice_hotkey_e.insert(0, self.cfg["voice"].get("hotkey", "ctrl+alt+v"))

        r2 = ctk.CTkFrame(cf, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(r2, text="Idioma:", width=140,
            font=ctk.CTkFont(size=10)).pack(side="left")
        self.voice_lang_m = ctk.CTkOptionMenu(r2,
            values=["pt-BR", "en-US", "es-ES"],
            fg_color=C["bg"], button_color=C["blue"],
            font=ctk.CTkFont("Consolas", 10))
        self.voice_lang_m.set(self.cfg["voice"].get("language", "pt-BR"))
        self.voice_lang_m.pack(side="left")

        ctk.CTkButton(cf, text="💾  SALVAR CONFIG DE VOZ",
            fg_color=C["blue"], hover_color="#003D73",
            border_color=C["gold"], border_width=1,
            height=32, font=ctk.CTkFont(size=10, weight="bold"),
            command=self._save_voice_cfg
        ).pack(padx=12, pady=8, fill="x")

        # Ajuda
        hf = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        hf.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(hf, text="📋  COMO USAR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=C["accent"]).pack(padx=12, pady=(10, 4), anchor="w")

        ctk.CTkLabel(hf,
            text=(
                "1. Pressione o atalho configurado acima.\n"
                "2. Fale o nome do atalho ou do arquivo.\n"
                "3. O sistema casa com seus atalhos e executa.\n\n"
                "Exemplos:\n"
                "   'Abrir Chrome'   →  executa o atalho Chrome\n"
                "   'Pasta de músicas' →  abre a pasta de músicas\n"
                "   'Escrever email' →  digita o texto automático\n\n"
                "Requer: internet (Google Speech) + microfone.\n"
                "Para uso offline: instale Vosk manualmente."
            ),
            font=ctk.CTkFont("Consolas", 9),
            text_color=C["text"], justify="left"
        ).pack(padx=12, pady=(0, 12), anchor="w")

        self.voice_status_lbl = ctk.CTkLabel(tab, text="🎙  Aguardando...",
            font=ctk.CTkFont("Consolas", 11, "bold"),
            text_color=C["dim"])
        self.voice_status_lbl.pack(pady=5)

    # ═══════════════════════════════════════════════════════════════════════
    #  TAB ⚙ CONFIG
    # ═══════════════════════════════════════════════════════════════════════
    def _tab_config(self):
        tab = self.tabs.tab("⚙ CONFIG")

        # Clipboard Intelligence
        self._cfg_toggle_block(tab,
            title="📋  CLIPBOARD INTELLIGENCE",
            color=C["accent"],
            desc=("Detecta automaticamente o tipo do conteúdo copiado e sugere ações:\n"
                  "Telefone → WhatsApp | URL → Abrir | CPF → Validar | CNPJ → Consultar | E-mail → Gmail"),
            var=self.clipboard_on,
            cmd=self._save_config
        )

        # HUD Holográfico
        hud_block = self._cfg_toggle_block(tab,
            title="🖥  HUD HOLOGRÁFICO",
            color=C["green"],
            desc="Painel flutuante semi-transparente com atalhos ativos + stats de sistema. Arraste para mover.",
            var=self.hud_enabled,
            cmd=self._on_hud_toggle,
            return_frame=True
        )

        hr = ctk.CTkFrame(hud_block, fg_color="transparent")
        hr.pack(fill="x", padx=12, pady=(4, 8))
        ctk.CTkLabel(hr, text="Atalho HUD:", width=85,
            font=ctk.CTkFont(size=10)).pack(side="left")
        self.hud_hotkey_e = ctk.CTkEntry(hr,
            fg_color=C["bg"], border_color=C["border"],
            height=26, font=ctk.CTkFont("Consolas", 10))
        self.hud_hotkey_e.pack(side="left", fill="x", expand=True)
        self.hud_hotkey_e.insert(0, self.cfg["hud"].get("hotkey", "ctrl+alt+h"))

        ctk.CTkButton(hud_block, text="💾  SALVAR ATALHO HUD",
            fg_color=C["blue"], hover_color="#003D73",
            border_color=C["gold"], border_width=1,
            height=30, font=ctk.CTkFont(size=10, weight="bold"),
            command=self._save_hud_cfg
        ).pack(padx=12, pady=(0, 10), fill="x")

        # Sobre
        about = ctk.CTkFrame(tab, fg_color=C["card2"], corner_radius=10)
        about.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(about,
            text=f"AIra9Touch  {VERSION}\n"
                 "Desenvolvido com 100% de ferramentas gratuitas.\n"
                 "IA · Voz · HUD · Macros · Clipboard · Multi-Perfis · Stats",
            font=ctk.CTkFont("Consolas", 9),
            text_color=C["dim"], justify="center"
        ).pack(pady=14)

    def _cfg_toggle_block(self, parent, title, color, desc, var, cmd,
                          return_frame=False) -> ctk.CTkFrame | None:
        block = ctk.CTkFrame(parent, fg_color=C["card2"], corner_radius=10)
        block.pack(fill="x", padx=10, pady=(10, 5))

        tr = ctk.CTkFrame(block, fg_color="transparent")
        tr.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(tr, text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color).pack(side="left")
        ctk.CTkSwitch(tr, text="", variable=var, command=cmd,
            progress_color=color, button_color=C["gold"]
        ).pack(side="right")

        ctk.CTkLabel(block, text=desc,
            font=ctk.CTkFont(size=9), text_color=C["dim"],
            wraplength=580, justify="left"
        ).pack(padx=12, pady=(0, 10), anchor="w")

        if return_frame:
            return block

    # ═══════════════════════════════════════════════════════════════════════
    #  STATS — Thread de monitoramento de hardware
    # ═══════════════════════════════════════════════════════════════════════
    def _stats_thread(self):
        while True:
            try:
                cpu  = psutil.cpu_percent(interval=1)
                mem  = psutil.virtual_memory()
                disk = psutil.disk_usage("/").percent
                ram  = mem.used / (1024 ** 3)

                temp_str = "N/A"
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for entries in temps.values():
                            if entries:
                                temp_str = f"{entries[0].current:.0f}°C"
                                break
                except Exception:
                    pass

                now     = time.strftime("%H:%M:%S")
                cpu_clr = C["red"] if cpu  > 80 else C["accent"]
                ram_clr = C["red"] if mem.percent > 85 else C["green"]

                self.root.after(0, lambda c=cpu, r=ram, t=temp_str, d=disk,
                                       n=now, cc=cpu_clr, rc=ram_clr:
                    self._update_stats(c, r, t, d, n, cc, rc))
            except Exception:
                pass
            time.sleep(2)

    def _update_stats(self, cpu, ram, temp, disk, now, cc, rc):
        self.lbl_cpu.configure(text=f"CPU: {cpu:.0f}%",  text_color=cc)
        self.lbl_ram.configure(text=f"RAM: {ram:.1f}GB", text_color=rc)
        self.lbl_temp.configure(text=f"TEMP: {temp}")
        self.lbl_disk.configure(text=f"DISCO: {disk:.0f}%")
        self.lbl_time.configure(text=now)

    # ═══════════════════════════════════════════════════════════════════════
    #  MACRO RECORDER
    # ═══════════════════════════════════════════════════════════════════════
    def _toggle_macro_record(self):
        if not self.recording_macro:
            self._start_record()
        else:
            self._stop_record()

    def _start_record(self):
        name = self.macro_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite um nome para a macro!")
            return

        self.recording_macro = True
        self.macro_events    = []
        self._macro_t0       = time.time()

        self.btn_record.configure(
            text="⏹  PARAR GRAVAÇÃO",
            fg_color="#330000", border_color=C["red"])
        self.lbl_rec.configure(text="⏺  GRAVANDO...", text_color=C["red"])

        def on_key(e):
            if not self.recording_macro:
                return
            delay = time.time() - self._macro_t0
            self._macro_t0 = time.time()
            self.macro_events.append({
                "type":       "key",
                "event_type": e.event_type,
                "name":       e.name,
                "delay":      round(delay, 3),
            })

        self._macro_hook = keyboard.hook(on_key)

    def _stop_record(self):
        self.recording_macro = False
        if self._macro_hook:
            keyboard.unhook(self._macro_hook)
            self._macro_hook = None

        name = self.macro_name_entry.get().strip()
        if name and self.macro_events:
            self.macros[name] = {"events": self.macro_events, "hotkey": None}
            self._save_config()
            self._refresh_macros()
            messagebox.showinfo("Macro Salva!",
                f"Macro '{name}' salva com {len(self.macro_events)} eventos.\n"
                "Use 'DEFINIR ATALHO' para atribuir um hotkey.")

        self.btn_record.configure(
            text="⏺  INICIAR GRAVAÇÃO",
            fg_color="#1A0A0A", border_color=C["red"])
        self.lbl_rec.configure(text="◉ PRONTO", text_color=C["dim"])
        self.macro_name_entry.delete(0, "end")

    def _refresh_macros(self):
        self.macro_listbox.delete(0, tk.END)
        for name, data in self.macros.items():
            hk  = data.get("hotkey") or "sem atalho"
            cnt = len(data.get("events", []))
            self.macro_listbox.insert(
                tk.END, f"[{cnt:>3} eventos]  {name.upper():20s}  ➔  {hk.upper()}")

    def _run_selected_macro(self):
        sel = self.macro_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma macro.")
            return
        name = list(self.macros.keys())[sel[0]]
        threading.Thread(target=self._exec_macro, args=(name,), daemon=True).start()

    def _exec_macro(self, name: str):
        for ev in self.macros[name].get("events", []):
            time.sleep(min(ev["delay"], 1.5))
            try:
                if ev["event_type"] == keyboard.KEY_DOWN:
                    keyboard.press(ev["name"])
                elif ev["event_type"] == keyboard.KEY_UP:
                    keyboard.release(ev["name"])
            except Exception:
                pass

    def _set_macro_hotkey(self):
        sel = self.macro_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma macro.")
            return
        name = list(self.macros.keys())[sel[0]]
        self._ask_macro_hotkey(name)

    def _ask_macro_hotkey(self, macro_name: str):
        win = ctk.CTkToplevel(self.root)
        win.title(f"Atalho — {macro_name}")
        win.geometry("400x220")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=f"MACRO: {macro_name.upper()}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["gold"]).pack(pady=(20, 5))
        ctk.CTkLabel(win, text="Pressione a combinação de teclas:",
            font=ctk.CTkFont(size=10)).pack()

        lbl = ctk.CTkLabel(win, text="...",
            font=ctk.CTkFont("Consolas", 22, "bold"),
            text_color=C["blue"])
        lbl.pack(pady=12)
        ctk.CTkLabel(win, text="(Solte para salvar)",
            font=ctk.CTkFont(size=9), text_color=C["dim"]).pack()

        captured: list = []
        def on_key(e):
            if e.event_type == keyboard.KEY_DOWN and e.name not in captured:
                captured.append(e.name)
                lbl.configure(text="+".join(captured).upper())
            elif e.event_type == keyboard.KEY_UP and captured:
                hk = "+".join(captured).lower()
                keyboard.unhook(hook)
                self.macros[macro_name]["hotkey"] = hk
                self._save_config()
                self._reload_hotkeys()
                self._refresh_macros()
                win.destroy()
                messagebox.showinfo("Atalho Definido!",
                    f"Macro '{macro_name}' → [{hk.upper()}]")

        hook = keyboard.hook(on_key)

    def _remove_macro(self):
        sel = self.macro_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma macro.")
            return
        name = list(self.macros.keys())[sel[0]]
        if messagebox.askyesno("Remover", f"Remover macro '{name}'?"):
            del self.macros[name]
            self._save_config()
            self._refresh_macros()
            self._reload_hotkeys()

    # ═══════════════════════════════════════════════════════════════════════
    #  IA
    # ═══════════════════════════════════════════════════════════════════════
    def _on_ai_toggle(self):
        self._save_config()
        if self.ai_enabled.get():
            self._register_ai_hotkey()
        else:
            self._unregister_hotkey(self.cfg["ai"].get("hotkey", "ctrl+alt+a"))

    def _save_ai_cfg(self):
        for k, e in self.ai_entries.items():
            self.cfg["ai"][k] = e.get()
        self.cfg["ai"]["api_key"] = self.ai_key_entry.get()
        self._save_config()
        self._register_ai_hotkey()
        messagebox.showinfo("Salvo", "Configuração de IA salva!")

    def _register_ai_hotkey(self):
        hk = self.cfg["ai"].get("hotkey", "ctrl+alt+a")
        self._unregister_hotkey(hk)
        if self.ai_enabled.get():
            try:
                keyboard.add_hotkey(hk, lambda: self.root.after(0, self._open_ai_popup))
            except Exception:
                pass

    def _open_ai_popup(self):
        win = ctk.CTkToplevel(self.root)
        win.title("🤖 AIra9 — IA")
        win.geometry("520x360")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="🤖  CONSULTA RÁPIDA — IA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=C["purple"]).pack(pady=(15, 5))

        out = ctk.CTkTextbox(win,
            fg_color=C["card"], text_color=C["text"],
            font=ctk.CTkFont("Consolas", 10),
            height=220, state="disabled")
        out.pack(fill="both", expand=True, padx=15, pady=5)

        row = ctk.CTkFrame(win, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=(5, 15))

        ent = ctk.CTkEntry(row,
            placeholder_text="Faça uma pergunta...",
            fg_color=C["card"], border_color=C["purple"], height=38)
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ent.focus()

        def send():
            q = ent.get().strip()
            if not q:
                return
            ent.delete(0, "end")
            self._ai_append(out, f"Você: {q}\n")
            threading.Thread(target=self._call_ai, args=(q, out), daemon=True).start()

        ent.bind("<Return>", lambda _: send())
        ctk.CTkButton(row, text="↵", width=52, height=38,
            fg_color=C["purple"], command=send).pack(side="left")

    def _run_ai_query(self):
        if not self.ai_enabled.get():
            messagebox.showwarning("IA Desativada",
                "Ative a IA na aba 🤖 IA e salve sua API Key primeiro.")
            return
        q = self.ai_input.get().strip()
        if not q:
            return
        self.ai_input.delete(0, "end")
        self._ai_append(self.ai_output, f"Você: {q}\n")
        threading.Thread(target=self._call_ai, args=(q, self.ai_output), daemon=True).start()

    def _call_ai(self, query: str, widget: ctk.CTkTextbox):
        key = self.cfg["ai"].get("api_key", "").strip()
        if not key:
            self._ai_append(widget, "IA: [Configure sua API Key na aba 🤖 IA]\n\n")
            return
        try:
            resp = requests.post(
                self.cfg["ai"]["api_url"],
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json={
                    "model": self.cfg["ai"].get("model", "llama3-8b-8192"),
                    "messages": [
                        {"role": "system",
                         "content": "Você é o assistente AIra9Touch. "
                                    "Responda de forma clara e concisa em português."},
                        {"role": "user", "content": query},
                    ],
                    "max_tokens": 500,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"]
                self._ai_append(widget, f"IA: {answer}\n\n")
            else:
                self._ai_append(widget,
                    f"IA: [Erro {resp.status_code}] {resp.text[:120]}\n\n")
        except Exception as ex:
            self._ai_append(widget, f"IA: [Conexão falhou] {str(ex)[:80]}\n\n")

    def _ai_append(self, w: ctk.CTkTextbox, text: str):
        self.root.after(0, lambda: self._do_ai_append(w, text))

    def _do_ai_append(self, w: ctk.CTkTextbox, text: str):
        w.configure(state="normal")
        w.insert("end", text)
        w.see("end")
        w.configure(state="disabled")

    # ═══════════════════════════════════════════════════════════════════════
    #  VOZ
    # ═══════════════════════════════════════════════════════════════════════
    def _on_voice_toggle(self):
        if self.voice_enabled.get() and not VOICE_OK:
            messagebox.showerror("Módulo ausente",
                "Instale:\n  pip install SpeechRecognition pyaudio")
            self.voice_enabled.set(False)
            return
        self._save_config()
        if self.voice_enabled.get():
            self._register_voice_hotkey()
        else:
            self._unregister_hotkey(self.cfg["voice"].get("hotkey", "ctrl+alt+v"))

    def _save_voice_cfg(self):
        self.cfg["voice"]["hotkey"]   = self.voice_hotkey_e.get()
        self.cfg["voice"]["language"] = self.voice_lang_m.get()
        self._save_config()
        self._register_voice_hotkey()
        messagebox.showinfo("Salvo", "Configuração de voz salva!")

    def _register_voice_hotkey(self):
        hk = self.cfg["voice"].get("hotkey", "ctrl+alt+v")
        self._unregister_hotkey(hk)
        if self.voice_enabled.get() and VOICE_OK:
            try:
                keyboard.add_hotkey(hk, self._trigger_voice)
            except Exception:
                pass

    def _trigger_voice(self):
        if self.voice_listening:
            return
        threading.Thread(target=self._listen_voice, daemon=True).start()

    def _listen_voice(self):
        self.voice_listening = True
        self._voice_status("🎙  OUVINDO...", C["red"])

        try:
            r = sr.Recognizer()
            with sr.Microphone() as src:
                r.adjust_for_ambient_noise(src, duration=0.4)
                audio = r.listen(src, timeout=5, phrase_time_limit=5)

            lang = self.cfg["voice"].get("language", "pt-BR")
            text = r.recognize_google(audio, language=lang).lower()
            self._voice_status(f"🎙  '{text}'", C["green"])
            self._match_voice(text)

        except sr.WaitTimeoutError:
            self._voice_status("🎙  Timeout — tente de novo", C["gold"])
        except sr.UnknownValueError:
            self._voice_status("🎙  Não entendi", C["gold"])
        except Exception as ex:
            self._voice_status(f"🎙  Erro: {str(ex)[:40]}", C["red"])
        finally:
            self.voice_listening = False
            self.root.after(3500, lambda: self._voice_status("🎙  Aguardando...", C["dim"]))

    def _voice_status(self, msg: str, color: str):
        self.root.after(0, lambda m=msg, c=color:
            self.voice_status_lbl.configure(text=m, text_color=c))

    def _match_voice(self, spoken: str):
        words  = set(spoken.lower().split())
        best   = None
        score  = 0

        for hk, data in self.shortcuts.items():
            v    = data.get("value", "")
            name = os.path.basename(v).lower().replace("_", " ").replace("-", " ")
            overlap = len(words & set(name.split()))
            if overlap > score:
                score = overlap
                best  = data

        if best and score > 0:
            threading.Thread(target=self._exec_shortcut, args=(best,), daemon=True).start()
        else:
            self._voice_status(f"🎙  Sem correspondência: '{spoken}'", C["gold"])

    def _exec_shortcut(self, data: dict):
        if not self.is_active.get():
            return
        t, v = data["type"], data["value"]
        try:
            if t in ("file", "folder"):
                os.startfile(v)
            elif t == "automation":
                time.sleep(0.5)
                pyautogui.write(v)
            elif t == "click":
                x, y = map(int, v.split(","))
                pyautogui.click(x, y)
            elif t == "media":
                self._play_media(v)
            elif t == "url":
                webbrowser.open(v)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════════════
    #  CLIPBOARD INTELLIGENCE
    # ═══════════════════════════════════════════════════════════════════════
    def _clipboard_thread(self):
        if not PYPERCLIP_OK:
            return
        while True:
            try:
                if self.clipboard_on.get():
                    cur = pyperclip.paste()
                    if cur and cur != self._last_clipboard:
                        self._last_clipboard = cur
                        self.root.after(0, lambda c=cur: self._analyze_clip(c))
            except Exception:
                pass
            time.sleep(0.8)

    def _analyze_clip(self, text: str):
        text = text.strip()
        if not text or len(text) > 400:
            return

        patterns = {
            "phone": r'(\+55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}',
            "email": r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
            "url":   r'https?://[^\s]{6,}',
            "cpf":   r'\b\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}\b',
            "cnpj":  r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
        }
        labels = {
            "phone": "📱  Telefone detectado!",
            "email": "📧  E-mail detectado!",
            "url":   "🌐  URL detectada!",
            "cpf":   "🪪  CPF detectado!",
            "cnpj":  "🏢  CNPJ detectado!",
        }

        for ptype, pattern in patterns.items():
            if re.search(pattern, text):
                self._show_clip_popup(ptype, text, labels[ptype])
                return

    def _show_clip_popup(self, ptype: str, text: str, label: str):
        win = ctk.CTkToplevel()
        win.title("Clipboard Intelligence")
        win.geometry("390x185")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)
        win.attributes("-alpha",   0.93)

        sw = win.winfo_screenwidth()
        win.geometry(f"390x185+{sw - 410}+18")

        ctk.CTkLabel(win, text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["accent"]).pack(pady=(14, 4))

        ctk.CTkLabel(win,
            text=text[:65] + ("…" if len(text) > 65 else ""),
            font=ctk.CTkFont("Consolas", 9),
            text_color=C["text"]).pack(pady=4)

        bf = ctk.CTkFrame(win, fg_color="transparent")
        bf.pack(pady=8)

        for lbl_btn, cmd in self._clip_actions(ptype, text):
            ctk.CTkButton(bf, text=lbl_btn,
                height=30, width=170,
                fg_color=C["blue"], hover_color="#003D73",
                border_color=C["gold"], border_width=1,
                font=ctk.CTkFont(size=10, weight="bold"),
                command=lambda c=cmd, w=win: (c(), w.destroy())
            ).pack(side="left", padx=4)

        ctk.CTkButton(win, text="✕  Fechar",
            height=26, fg_color="transparent",
            text_color=C["dim"], hover_color=C["card"],
            command=win.destroy
        ).pack()

        win.after(8000, lambda: win.destroy() if win.winfo_exists() else None)

    def _clip_actions(self, ptype: str, text: str):
        def safe_copy(t):
            if PYPERCLIP_OK:
                pyperclip.copy(t)

        if ptype == "phone":
            num = re.sub(r"[^\d+]", "", text).lstrip("+").lstrip("55")
            return [
                ("📱 WhatsApp", lambda n=num: webbrowser.open(f"https://wa.me/55{n}")),
                ("📋 Copiar limpo", lambda n=num: safe_copy(n)),
            ]
        if ptype == "email":
            return [
                ("📧 Abrir Gmail", lambda e=text: webbrowser.open(f"https://mail.google.com/mail/?view=cm&to={e}")),
                ("📋 Copiar", lambda e=text: safe_copy(e)),
            ]
        if ptype == "url":
            return [
                ("🌐 Abrir URL", lambda u=text: webbrowser.open(u)),
                ("📋 Copiar", lambda u=text: safe_copy(u)),
            ]
        if ptype == "cpf":
            d = re.sub(r"\D", "", text)
            ok = self._valid_cpf(d)
            return [
                (f"🪪 {'✅ Válido' if ok else '❌ Inválido'}", lambda: None),
                ("📋 Copiar digits", lambda dd=d: safe_copy(dd)),
            ]
        if ptype == "cnpj":
            d = re.sub(r"\D", "", text)
            return [
                ("🔍 Consultar CNPJ", lambda dd=d: webbrowser.open(f"https://www.receitaws.com.br/v1/cnpj/{dd}")),
                ("📋 Copiar digits", lambda dd=d: safe_copy(dd)),
            ]
        return []

    @staticmethod
    def _valid_cpf(cpf: str) -> bool:
        if len(cpf) != 11 or len(set(cpf)) == 1:
            return False
        for i in range(9, 11):
            s = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
            if (s * 10 % 11) % 10 != int(cpf[i]):
                return False
        return True

    # ═══════════════════════════════════════════════════════════════════════
    #  HUD HOLOGRÁFICO
    # ═══════════════════════════════════════════════════════════════════════
    def _on_hud_toggle(self):
        self._save_config()
        if self.hud_enabled.get():
            self._show_hud()
        else:
            self._hide_hud()

    def _save_hud_cfg(self):
        self.cfg["hud"]["hotkey"] = self.hud_hotkey_e.get()
        self._save_config()
        self._register_hud_hotkey()
        messagebox.showinfo("Salvo", "Atalho do HUD salvo!")

    def _register_hud_hotkey(self):
        hk = self.cfg["hud"].get("hotkey", "ctrl+alt+h")
        self._unregister_hotkey(hk)
        try:
            keyboard.add_hotkey(hk, lambda: self.root.after(0, self._toggle_hud))
        except Exception:
            pass

    def _toggle_hud(self):
        if self.hud_window and self.hud_window.winfo_exists():
            self._hide_hud()
        else:
            self._show_hud()

    def _show_hud(self):
        if self.hud_window and self.hud_window.winfo_exists():
            return

        hud = tk.Toplevel()
        hud.title("")
        hud.configure(bg="#0B0E14")
        hud.geometry("230x420+18+18")
        hud.attributes("-topmost", True)
        hud.attributes("-alpha", 0.88)
        hud.overrideredirect(True)          # sem barra de título do Windows

        # ── Arrastar ──
        def _start(e):
            hud._dx, hud._dy = e.x, e.y

        def _drag(e):
            hud.geometry(f"+{hud.winfo_x() + e.x - hud._dx}"
                         f"+{hud.winfo_y() + e.y - hud._dy}")

        hud.bind("<Button-1>",   _start)
        hud.bind("<B1-Motion>",  _drag)

        # ── Cabeçalho ──
        bar = tk.Frame(hud, bg="#004B8D", height=28)
        bar.pack(fill="x")
        bar.bind("<Button-1>",  _start)
        bar.bind("<B1-Motion>", _drag)

        tk.Label(bar, text="⚡  AIRA9  HUD",
            bg="#004B8D", fg="#C5A059",
            font=("Consolas", 9, "bold")
        ).pack(side="left", padx=8, pady=5)

        tk.Button(bar, text="✕",
            bg="#004B8D", fg="#FF4444",
            font=("Consolas", 9, "bold"),
            relief="flat", bd=0,
            command=self._hide_hud
        ).pack(side="right", padx=6)

        self.hud_content = tk.Frame(hud, bg="#0B0E14")
        self.hud_content.pack(fill="both", expand=True, padx=4, pady=4)

        self.hud_window = hud
        self._refresh_hud()

    def _refresh_hud(self):
        if not self.hud_window or not self.hud_window.winfo_exists():
            return

        for w in self.hud_content.winfo_children():
            w.destroy()

        tk.Label(self.hud_content, text="ATALHOS",
            bg="#0B0E14", fg="#444455",
            font=("Consolas", 7, "bold")
        ).pack(anchor="w", padx=4, pady=(2, 0))

        tipo_clr = {
            "file":       "#00A8FF",
            "folder":     "#C5A059",
            "automation": "#00FF88",
            "click":      "#F59E0B",
            "media":      "#8B5CF6",
            "url":        "#FF69B4",
        }

        for hk, data in list(self.shortcuts.items())[:12]:
            t, v = data["type"], data["value"]
            name = os.path.basename(v) if t not in ("automation", "click", "url") else v[:18]
            clr  = tipo_clr.get(t, "#E1E1E1")

            row = tk.Frame(self.hud_content, bg="#151921")
            row.pack(fill="x", padx=2, pady=1)

            tk.Label(row, text=hk.upper(),
                bg="#151921", fg=clr,
                font=("Consolas", 7, "bold"),
                width=16, anchor="w"
            ).pack(side="left", padx=3)
            tk.Label(row, text=name[:17],
                bg="#151921", fg="#E1E1E1",
                font=("Consolas", 7), anchor="w"
            ).pack(side="left")

        # Linha separadora
        tk.Frame(self.hud_content, bg="#2A2F3A", height=1).pack(fill="x", pady=3)

        # Stats rápidos
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            tk.Label(self.hud_content,
                text=f"CPU {cpu:.0f}%   RAM {ram:.0f}%   {time.strftime('%H:%M')}",
                bg="#0B0E14", fg="#00A8FF",
                font=("Consolas", 8)
            ).pack(anchor="w", padx=4, pady=2)
        except Exception:
            pass

        # Auto-refresh a cada 3s
        if self.hud_window and self.hud_window.winfo_exists():
            self.hud_window.after(3000, self._refresh_hud)

    def _hide_hud(self):
        if self.hud_window and self.hud_window.winfo_exists():
            self.hud_window.destroy()
        self.hud_window = None

    # ═══════════════════════════════════════════════════════════════════════
    #  MULTI-PERFIS
    # ═══════════════════════════════════════════════════════════════════════
    def _switch_profile(self, name: str):
        self.cfg["current_profile"] = name
        self._save_config()
        self._reload_hotkeys()
        self._refresh_macros()
        self._refresh_hud()

    def _new_profile(self):
        dlg = ctk.CTkInputDialog(text="Nome do novo perfil:", title="Novo Perfil")
        name = dlg.get_input()
        if not name or not name.strip():
            return
        name = name.strip().lower().replace(" ", "_")
        if name in self.cfg["profiles"]:
            messagebox.showwarning("Aviso", f"Perfil '{name}' já existe.")
            return
        self.cfg["profiles"][name] = {"shortcuts": {}, "macros": {}}
        self._save_config()
        self.profile_names = list(self.cfg["profiles"].keys())
        self.profile_menu.configure(values=self.profile_names)
        self.profile_var.set(name)
        self._switch_profile(name)
        messagebox.showinfo("Perfil Criado!", f"Perfil '{name}' criado e ativado.")

    def _remove_profile(self):
        name = self.profile_var.get()
        if name == "default":
            messagebox.showwarning("Aviso", "Não é possível remover o perfil padrão.")
            return
        if not messagebox.askyesno("Remover Perfil",
                f"Remover perfil '{name}' e todos os seus atalhos?"):
            return
        del self.cfg["profiles"][name]
        self.cfg["current_profile"] = "default"
        self._save_config()
        self.profile_names = list(self.cfg["profiles"].keys())
        self.profile_menu.configure(values=self.profile_names)
        self.profile_var.set("default")
        self._switch_profile("default")

    # ═══════════════════════════════════════════════════════════════════════
    #  HOTKEYS — Registro e recarga
    # ═══════════════════════════════════════════════════════════════════════
    def _unregister_hotkey(self, hk: str):
        try:
            keyboard.remove_hotkey(hk)
        except Exception:
            pass

    def _reload_hotkeys(self):
        keyboard.unhook_all()

        self.listbox.delete(0, tk.END)

        tipo_map = {
            "file":       "ARQ ",
            "folder":     "DIR ",
            "automation": "TXT ",
            "click":      "CLK ",
            "media":      "PLAY",
            "url":        "URL ",
        }

        for hk, data in self.shortcuts.items():
            if self.is_active.get():
                self._reg_hk(hk, data)

            t = tipo_map.get(data["type"], "??? ")
            v = data["value"]

            if data["type"] == "click":
                nome = f"Pos {v}"
            elif data["type"] == "automation":
                nome = v[:22] + "…"
            elif data["type"] == "url":
                nome = v[:30]
            else:
                nome = os.path.basename(v) or v

            self.listbox.insert(tk.END, f"[{t}]  {hk.upper():20s}  ➔  {nome}")

        # Macros com hotkey
        for mname, mdata in self.macros.items():
            hk = mdata.get("hotkey")
            if hk and self.is_active.get():
                try:
                    keyboard.add_hotkey(
                        hk, lambda n=mname: threading.Thread(
                            target=self._exec_macro, args=(n,), daemon=True
                        ).start()
                    )
                except Exception:
                    pass

        # Feature hotkeys
        if self.ai_enabled.get():
            self._register_ai_hotkey()
        if self.voice_enabled.get() and VOICE_OK:
            self._register_voice_hotkey()
        self._register_hud_hotkey()

        self._refresh_macros()

    def _reg_hk(self, hk: str, data: dict):
        try:
            t, v = data["type"], data["value"]
            if t in ("file", "folder"):
                keyboard.add_hotkey(hk, lambda val=v: os.startfile(val))
            elif t == "automation":
                keyboard.add_hotkey(hk, lambda val=v: self._run_auto(val))
            elif t == "click":
                keyboard.add_hotkey(hk, lambda val=v: self._run_click(val))
            elif t == "media":
                keyboard.add_hotkey(hk, lambda val=v: self._play_media(val))
            elif t == "url":
                keyboard.add_hotkey(hk, lambda val=v: webbrowser.open(val))
        except Exception as ex:
            print(f"Hotkey error [{hk}]: {ex}")

    # ═══════════════════════════════════════════════════════════════════════
    #  AÇÕES DE ATALHO
    # ═══════════════════════════════════════════════════════════════════════
    def _run_auto(self, text: str):
        if not self.is_active.get():
            return
        time.sleep(0.5)
        pyautogui.write(text)

    def _run_click(self, pos: str):
        if not self.is_active.get():
            return
        try:
            x, y = map(int, pos.split(","))
            pyautogui.click(x, y)
        except Exception:
            pass

    def _play_media(self, folder: str):
        if not self.is_active.get():
            return
        files = []
        for ext in ("*.mp3", "*.wav", "*.mp4", "*.mkv", "*.avi", "*.jpg", "*.png"):
            files.extend(glob.glob(os.path.join(folder, ext)))
        os.startfile(files[0] if files else folder)

    # ═══════════════════════════════════════════════════════════════════════
    #  ADICIONAR ATALHOS
    # ═══════════════════════════════════════════════════════════════════════
    def _add_file(self):
        p = filedialog.askopenfilename(title="Selecionar Programa/Arquivo")
        if p:
            self._ask_hotkey(p, "file")

    def _add_folder(self):
        p = filedialog.askdirectory(title="Selecionar Pasta")
        if p:
            self._ask_hotkey(p, "folder")

    def _add_media(self):
        p = filedialog.askdirectory(title="Selecionar Pasta de Mídia")
        if p:
            self._ask_hotkey(p, "media")

    def _add_url(self):
        self._input_dialog("URL / Site", "Digite a URL completa:", "url")

    def _add_text(self):
        self._input_dialog("Texto Automático", "Digite o texto a ser digitado:", "automation")

    def _add_click(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Capturar Posição")
        win.geometry("400x280")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="CAPTURA DE POSIÇÃO",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C["gold"]).pack(pady=20)
        ctk.CTkLabel(win,
            text="1. Posicione o mouse no alvo\n2. Pressione F8 para capturar"
        ).pack(pady=8)

        lbl = ctk.CTkLabel(win, text="AGUARDANDO F8...",
            font=ctk.CTkFont("Consolas", 14),
            text_color=C["accent"])
        lbl.pack(pady=20)

        def capture():
            while win.winfo_exists():
                if keyboard.is_pressed("f8"):
                    x, y = pyautogui.position()
                    lbl.configure(text=f"CAPTURADO: {x}, {y}")
                    time.sleep(0.5)
                    win.after(500, lambda: (
                        win.destroy(),
                        self._ask_hotkey(f"{x},{y}", "click")
                    ))
                    break
                time.sleep(0.1)

        threading.Thread(target=capture, daemon=True).start()

    def _input_dialog(self, title: str, prompt: str, type_: str):
        win = ctk.CTkToplevel(self.root)
        win.title(title)
        win.geometry("440x220")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text=prompt,
            font=ctk.CTkFont(weight="bold")).pack(pady=20)

        entry = ctk.CTkEntry(win, width=360,
            fg_color=C["card"], border_color=C["gold"])
        entry.pack(pady=8)
        entry.focus()

        def go():
            v = entry.get().strip()
            if v:
                win.destroy()
                self._ask_hotkey(v, type_)

        entry.bind("<Return>", lambda _: go())
        ctk.CTkButton(win, text="PRÓXIMO →",
            fg_color=C["blue"], border_color=C["gold"], border_width=1,
            command=go).pack(pady=15)

    def _ask_hotkey(self, value: str, type_: str):
        win = ctk.CTkToplevel(self.root)
        win.title("Gravar Atalho")
        win.geometry("420x250")
        win.configure(fg_color=C["bg"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(win, text="PRESSIONE AS TECLAS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=C["gold"]).pack(pady=20)

        lbl = ctk.CTkLabel(win, text="...",
            font=ctk.CTkFont("Consolas", 24, "bold"),
            text_color=C["blue"])
        lbl.pack(pady=10)

        ctk.CTkLabel(win, text="(Solte para salvar)",
            font=ctk.CTkFont(size=10),
            text_color=C["dim"]).pack()

        captured: list = []
        def on_key(e):
            if e.event_type == keyboard.KEY_DOWN and e.name not in captured:
                captured.append(e.name)
                lbl.configure(text="+".join(captured).upper())
            elif e.event_type == keyboard.KEY_UP and captured:
                hk = "+".join(captured).lower()
                keyboard.unhook(hook)
                self._save_shortcut(hk, value, type_)
                win.destroy()

        hook = keyboard.hook(on_key)

    def _save_shortcut(self, hk: str, value: str, type_: str):
        self.shortcuts[hk] = {"type": type_, "value": value}
        self._save_config()
        self._reload_hotkeys()
        messagebox.showinfo("✅ Atalho Ativado!",
            f"[{hk.upper()}]  configurado com sucesso!")

    def _remove_shortcut(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um atalho.")
            return
        txt = self.listbox.get(sel[0])
        try:
            hk = txt.split("]  ")[1].split("  ➔")[0].lower().strip()
            if hk in self.shortcuts:
                del self.shortcuts[hk]
                self._save_config()
                self._reload_hotkeys()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════════════
    #  STARTUP WINDOWS
    # ═══════════════════════════════════════════════════════════════════════
    def _toggle_startup(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               key_path, 0, winreg.KEY_SET_VALUE)
            if self.auto_start.get():
                path = os.path.realpath(sys.argv[0])
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, f'"{path}"')
                messagebox.showinfo("OK", "AIra9Touch iniciará com o Windows.")
            else:
                winreg.DeleteValue(k, APP_NAME)
                messagebox.showinfo("OK", "Início automático removido.")
            winreg.CloseKey(k)
        except Exception as ex:
            messagebox.showerror("Erro", str(ex))

    # ═══════════════════════════════════════════════════════════════════════
    #  TRAY
    # ═══════════════════════════════════════════════════════════════════════
    def _create_tray_icon(self):
        img = (Image.open("icon.ico") if os.path.exists("icon.ico")
               else Image.new("RGB", (64, 64), (0, 75, 141)))

        menu = (
            item("Abrir",     self.show_window),
            item("HUD On/Off", lambda _: self.root.after(0, self._toggle_hud)),
            item("Sair",       self._quit),
        )
        self.tray = pystray.Icon(APP_NAME, img, f"{APP_NAME} {VERSION}", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.after(0, lambda: (
            self.root.deiconify(),
            self.root.lift(),
            self.root.focus_force()
        ))

    def _quit(self):
        self.tray.stop()
        self.root.quit()
        sys.exit(0)

    # ═══════════════════════════════════════════════════════════════════════
    #  THREADS DE BACKGROUND
    # ═══════════════════════════════════════════════════════════════════════
    def _start_bg_threads(self):
        threading.Thread(target=self._stats_thread,     daemon=True).start()
        threading.Thread(target=self._clipboard_thread, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = ctk.CTk()
    app  = AIra9TouchApp(root)
    root.mainloop()
