#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Naftali <https://github.com/Naftaliro>
"""
GNOME Theme Switcher — v1.4.0

A terminal-based theme manager for switching between system-wide GNOME themes.

This software is provided "as is", without warranty of any kind, express or implied.
Use at your own risk. For full details, see the LICENSE file in the repository.
This project is not affiliated with any of the upstream theme authors.

Copyright (c) 2026 Naftali
"""

import curses
import json
import os
import re
import subprocess
import sys
import shutil
import threading
import time
import traceback
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from enum import IntEnum

# ─── Version ─────────────────────────────────────────────────────────────────
VERSION = "1.4.0"

# ─── Exit / Error Codes ─────────────────────────────────────────────────────
class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    NOT_A_TERMINAL = 2
    CURSES_INIT_FAILED = 3
    CONFIG_DIR_ERROR = 4
    GSETTINGS_NOT_FOUND = 5
    NETWORK_ERROR = 10
    DOWNLOAD_FAILED = 11
    INSTALL_SCRIPT_FAILED = 12
    INSTALL_DEPS_FAILED = 13
    INSTALL_PERMISSION_DENIED = 14
    INSTALL_TIMEOUT = 15
    UPDATE_FAILED = 20
    BACKUP_FAILED = 30
    RESTORE_FAILED = 31

# Human-readable error messages
ERROR_MESSAGES = {
    ExitCode.SUCCESS: "Operation completed successfully.",
    ExitCode.GENERAL_ERROR: "An unexpected error occurred.",
    ExitCode.NOT_A_TERMINAL: "This application must be run in a terminal (TTY).",
    ExitCode.CURSES_INIT_FAILED: "Failed to initialize the terminal UI. Ensure your terminal supports curses.",
    ExitCode.CONFIG_DIR_ERROR: "Failed to create or access the configuration directory.",
    ExitCode.GSETTINGS_NOT_FOUND: "gsettings command not found. Is GNOME installed?",
    ExitCode.NETWORK_ERROR: "Network error. Check your internet connection.",
    ExitCode.DOWNLOAD_FAILED: "Failed to download the install script. URL may be invalid.",
    ExitCode.INSTALL_SCRIPT_FAILED: "The install script exited with an error.",
    ExitCode.INSTALL_DEPS_FAILED: "Failed to install dependencies (apt/dnf error).",
    ExitCode.INSTALL_PERMISSION_DENIED: "Permission denied. You may need to enter your sudo password.",
    ExitCode.INSTALL_TIMEOUT: "Installation timed out after 10 minutes.",
    ExitCode.UPDATE_FAILED: "Failed to update the application.",
    ExitCode.BACKUP_FAILED: "Failed to backup current theme settings.",
    ExitCode.RESTORE_FAILED: "Failed to restore theme from backup.",
}

# ─── Paths ───────────────────────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".config" / "gnome-theme-switcher"
CUSTOM_THEMES_FILE = CONFIG_DIR / "custom_themes.json"
BACKUP_FILE = CONFIG_DIR / "backup.json"
UPDATE_CHECK_FILE = CONFIG_DIR / "last_update_check.json"
LOG_FILE = CONFIG_DIR / "last_install.log"

# ─── GitHub Repos ────────────────────────────────────────────────────────────
SWITCHER_REPO = "Naftaliro/gnome-theme-switcher"
THEMES_REPO = "Naftaliro/zorinos-gnome-themes"
REPO_BASE = f"https://raw.githubusercontent.com/{THEMES_REPO}/v1.2.0"
GITHUB_API = "https://api.github.com"

# ─── Built-in Theme Definitions ─────────────────────────────────────────────
BUILTIN_THEMES = [
    {
        "name": "WhiteSur macOS",
        "category": "macOS",
        "gtk_theme": "WhiteSur-Dark-purple",
        "shell_theme": "WhiteSur-Dark-purple",
        "icon_theme": "WhiteSur-dark",
        "cursor_theme": "WhiteSur-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/macos-themes/whitesur-macos-theme-install.sh",
        "description": "macOS Big Sur / Monterey look with dark mode and purple accent. Includes GDM, wallpapers, and Firefox theme.",
        "builtin": True,
    },
    {
        "name": "Colloid Material",
        "category": "macOS",
        "gtk_theme": "Colloid-Purple-Dark",
        "shell_theme": "Colloid-Purple-Dark",
        "icon_theme": "Colloid-purple-dark",
        "cursor_theme": "Colloid-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/macos-themes/colloid-material-theme-install.sh",
        "description": "Clean Material Design theme with dark mode and purple accent. Supports Nord, Dracula, Catppuccin colorschemes.",
        "builtin": True,
    },
    {
        "name": "Fluent Win11",
        "category": "Windows",
        "gtk_theme": "Fluent-purple-Dark",
        "shell_theme": "Fluent-purple-Dark",
        "icon_theme": "Fluent-dark",
        "cursor_theme": "Fluent-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/windows-themes/fluent-win11-theme-install.sh",
        "description": "Windows 11 Fluent Design by vinceliuice. Dark mode with purple accent, matching icons and cursors.",
        "builtin": True,
    },
    {
        "name": "Win11",
        "category": "Windows",
        "gtk_theme": "Win11-purple-Dark",
        "shell_theme": "Win11-purple-Dark",
        "icon_theme": "Win11-dark",
        "cursor_theme": "Fluent-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/windows-themes/win11-theme-install.sh",
        "description": "Windows 11 theme by yeyushengfan258. Dark mode with purple accent and Fluent cursors.",
        "builtin": True,
    },
    {
        "name": "We10X Win10",
        "category": "Windows",
        "gtk_theme": "We10X-purple-Dark",
        "shell_theme": "We10X-purple-Dark",
        "icon_theme": "We10X-dark",
        "cursor_theme": "Fluent-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/windows-themes/we10x-win10-theme-install.sh",
        "description": "Windows 10 theme by yeyushengfan258. Dark mode with purple accent and Fluent cursors.",
        "builtin": True,
    },
    {
        "name": "Orchis Material",
        "category": "Linux-Native",
        "gtk_theme": "Orchis-Purple-Dark",
        "shell_theme": "Orchis-Purple-Dark",
        "icon_theme": "Tela-purple-dark",
        "cursor_theme": "Graphite-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/linux-native-themes/orchis-theme-install.sh",
        "description": "Polished Material Design theme with dark mode and purple accent. Tela icons and Graphite cursors.",
        "builtin": True,
    },
    {
        "name": "Graphite Minimal",
        "category": "Linux-Native",
        "gtk_theme": "Graphite-purple-Dark",
        "shell_theme": "Graphite-purple-Dark",
        "icon_theme": "Tela-purple-dark",
        "cursor_theme": "Graphite-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/linux-native-themes/graphite-theme-install.sh",
        "description": "Sleek, minimalist dark theme with purple accent. Includes GDM support, Tela icons, Graphite cursors.",
        "builtin": True,
    },
    {
        "name": "Lavanda Purple",
        "category": "Linux-Native",
        "gtk_theme": "Lavanda-Dark",
        "shell_theme": "Lavanda-Dark",
        "icon_theme": "Tela-purple-dark",
        "cursor_theme": "Graphite-dark-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/linux-native-themes/lavanda-theme-install.sh",
        "description": "Inherently purple theme — the entire design is built around a lavender palette. Tela icons, Graphite cursors.",
        "builtin": True,
    },
    {
        "name": "Catppuccin Mocha",
        "category": "Linux-Native",
        "gtk_theme": "Catppuccin-purple-Dark-Macchiato",
        "shell_theme": "Catppuccin-purple-Dark-Macchiato",
        "icon_theme": "Catppuccin-Mocha",
        "cursor_theme": "catppuccin-mocha-mauve-cursors",
        "color_scheme": "prefer-dark",
        "install_url": f"{REPO_BASE}/linux-native-themes/catppuccin-theme-install.sh",
        "description": "Warm, soothing pastel dark theme beloved by developers. Catppuccin icons and mauve cursors.",
        "builtin": True,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[GTS-E{ExitCode.CONFIG_DIR_ERROR:03d}] {ERROR_MESSAGES[ExitCode.CONFIG_DIR_ERROR]}: {e}")
        sys.exit(ExitCode.CONFIG_DIR_ERROR)


def log_to_file(message):
    """Append a timestamped message to the log file."""
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except OSError:
        pass


def strip_ansi(text):
    """Remove ANSI escape sequences from text."""
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def check_gsettings():
    """Verify gsettings is available."""
    return shutil.which("gsettings") is not None


def load_json_file(path, default=None):
    """Safely load a JSON file, returning default on any error."""
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        return default


def save_json_file(path, data):
    """Safely save data to a JSON file."""
    ensure_config_dir()
    tmp = path.with_suffix(".tmp")
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        shutil.move(str(tmp), str(path))
        return True
    except (IOError, OSError):
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  THEME MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def load_custom_themes():
    """Load custom themes from the JSON config file."""
    return load_json_file(CUSTOM_THEMES_FILE, [])


def save_custom_themes(themes):
    """Save custom themes to the JSON config file."""
    return save_json_file(CUSTOM_THEMES_FILE, themes)


def get_all_themes():
    """Return builtin themes + custom themes."""
    return BUILTIN_THEMES + load_custom_themes()


def gsettings_get(schema, key):
    """Get a gsettings value, return empty string on failure."""
    try:
        result = subprocess.run(
            ["gsettings", "get", schema, key],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().strip("'\"")
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def gsettings_set(schema, key, value):
    """Set a gsettings value. Returns (success, error_message)."""
    try:
        result = subprocess.run(
            ["gsettings", "set", schema, key, value],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "gsettings timed out"
    except FileNotFoundError:
        return False, "gsettings not found"
    except OSError as e:
        return False, str(e)


def get_current_theme_settings():
    """Read the current theme settings from gsettings."""
    return {
        "gtk_theme": gsettings_get("org.gnome.desktop.interface", "gtk-theme"),
        "shell_theme": gsettings_get("org.gnome.shell.extensions.user-theme", "name"),
        "icon_theme": gsettings_get("org.gnome.desktop.interface", "icon-theme"),
        "cursor_theme": gsettings_get("org.gnome.desktop.interface", "cursor-theme"),
        "color_scheme": gsettings_get("org.gnome.desktop.interface", "color-scheme"),
    }


def apply_theme(theme):
    """Apply a theme by setting all gsettings keys. Returns (success, errors_list)."""
    errors = []
    settings = [
        ("org.gnome.desktop.interface", "gtk-theme", theme["gtk_theme"]),
        ("org.gnome.desktop.wm.preferences", "theme", theme["gtk_theme"]),
        ("org.gnome.shell.extensions.user-theme", "name", theme.get("shell_theme", theme["gtk_theme"])),
        ("org.gnome.desktop.interface", "icon-theme", theme["icon_theme"]),
        ("org.gnome.desktop.interface", "cursor-theme", theme["cursor_theme"]),
        ("org.gnome.desktop.interface", "color-scheme", theme.get("color_scheme", "prefer-dark")),
    ]
    for schema, key, value in settings:
        ok, err = gsettings_set(schema, key, value)
        if not ok:
            errors.append(f"  {schema} {key}: {err}")
            log_to_file(f"gsettings_set FAILED: {schema} {key} {value} -> {err}")

    if errors:
        return False, errors
    return True, []


def backup_current_theme():
    """Backup current theme settings. Returns (success, data_or_error)."""
    try:
        current = get_current_theme_settings()
        current["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_json_file(BACKUP_FILE, current):
            return True, current
        return False, "Failed to write backup file."
    except Exception as e:
        return False, str(e)


def load_backup():
    """Load backup theme settings."""
    data = load_json_file(BACKUP_FILE, None)
    return data


def restore_backup():
    """Restore theme from backup. Returns (success, errors)."""
    backup = load_backup()
    if not backup:
        return False, ["No backup file found."]
    return apply_theme(backup)


def check_theme_installed(theme):
    """Check if a theme's GTK theme directory exists."""
    gtk_name = theme.get("gtk_theme", "")
    if not gtk_name:
        return False
    search_paths = [
        Path.home() / ".themes" / gtk_name,
        Path.home() / ".local" / "share" / "themes" / gtk_name,
        Path("/usr/share/themes") / gtk_name,
    ]
    return any(p.exists() for p in search_paths)


def detect_active_theme_index(themes):
    """Find which theme matches the currently active settings."""
    current = get_current_theme_settings()
    gtk = current.get("gtk_theme", "")
    for i, t in enumerate(themes):
        if t.get("gtk_theme", "") == gtk:
            return i
    return -1


# ═══════════════════════════════════════════════════════════════════════════════
#  UPDATE CHECKING
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_latest_release(repo):
    """Fetch the latest release tag from GitHub API. Returns (tag, url) or (None, None)."""
    try:
        url = f"{GITHUB_API}/repos/{repo}/releases/latest"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "gnome-theme-switcher"
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            return data.get("tag_name", None), data.get("html_url", "")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None, None


def check_for_updates():
    """Check both repos for updates. Returns dict with update info."""
    results = {"switcher": None, "themes": None}
    sw_tag, sw_url = fetch_latest_release(SWITCHER_REPO)
    if sw_tag and sw_tag.lstrip("v") != VERSION:
        results["switcher"] = {"current": VERSION, "latest": sw_tag, "url": sw_url}
    th_tag, th_url = fetch_latest_release(THEMES_REPO)
    current_themes_ver = REPO_BASE.split("/")[-1] if "/" in REPO_BASE else "unknown"
    if th_tag and th_tag != current_themes_ver:
        results["themes"] = {"current": current_themes_ver, "latest": th_tag, "url": th_url}
    return results


def save_update_check(results):
    """Save update check results and timestamp."""
    save_json_file(UPDATE_CHECK_FILE, {
        "timestamp": datetime.now().isoformat(),
        "results": {"switcher": results.get("switcher"), "themes": results.get("themes")}
    })


def should_check_updates():
    """Return True if we haven't checked in the last 6 hours."""
    data = load_json_file(UPDATE_CHECK_FILE, None)
    if not data or "timestamp" not in data:
        return True
    try:
        last = datetime.fromisoformat(data["timestamp"])
        return (datetime.now() - last).total_seconds() > 21600
    except (ValueError, TypeError):
        return True


def self_update():
    """Download and replace the current script with the latest version.
    Returns (success, message, error_code)."""
    try:
        tag, _ = fetch_latest_release(SWITCHER_REPO)
        if not tag:
            return False, "Could not determine latest version.", ExitCode.NETWORK_ERROR
        raw_url = f"https://raw.githubusercontent.com/{SWITCHER_REPO}/{tag}/gnome-theme-switcher.py"
        install_dir = Path.home() / ".local" / "bin"
        target = install_dir / "gnome-theme-switcher"
        tmp = target.with_suffix(".tmp")
        req = urllib.request.Request(raw_url, headers={"User-Agent": "gnome-theme-switcher"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
        with open(tmp, "wb") as f:
            f.write(content)
        os.chmod(tmp, 0o755)
        shutil.move(str(tmp), str(target))
        return True, f"Updated to {tag}. Please restart the application.", ExitCode.SUCCESS
    except urllib.error.URLError as e:
        return False, f"Download failed: {e}", ExitCode.DOWNLOAD_FAILED
    except PermissionError:
        return False, "Permission denied writing to ~/.local/bin/", ExitCode.INSTALL_PERMISSION_DENIED
    except Exception as e:
        return False, f"Update failed: {e}", ExitCode.UPDATE_FAILED


# ═══════════════════════════════════════════════════════════════════════════════
#  INSTALL PROCESS — runs in real terminal (suspends curses)
# ═══════════════════════════════════════════════════════════════════════════════

def run_install_in_terminal(url, theme_name):
    """
    Suspend curses, run the install script in the real terminal so the user
    can see output and enter their sudo password, then return control.

    Returns (success, return_code, error_code).
    """
    script_path = "/tmp/_gts_install.sh"

    # Clear the log file for this install
    try:
        LOG_FILE.write_text("")
    except OSError:
        pass

    # ── Print install header ──
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  GNOME Theme Switcher — Installing: {theme_name}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{DIM}  Source: {url}{RESET}")
    print(f"{DIM}  Log:    {LOG_FILE}{RESET}")
    print(f"{CYAN}{'─' * 70}{RESET}\n")

    # ── Step 1: Download the script ──
    print(f"{YELLOW}[1/2]{RESET} Downloading install script...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "gnome-theme-switcher"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        with open(script_path, "wb") as f:
            f.write(content)
        os.chmod(script_path, 0o755)
        print(f"{GREEN}  OK{RESET} — Downloaded ({len(content)} bytes)\n")
    except urllib.error.HTTPError as e:
        print(f"{RED}  FAILED{RESET} — HTTP {e.code}: {e.reason}")
        print(f"\n{RED}[GTS-E{ExitCode.DOWNLOAD_FAILED:03d}]{RESET} {ERROR_MESSAGES[ExitCode.DOWNLOAD_FAILED]}")
        print(f"{DIM}  URL: {url}{RESET}")
        log_to_file(f"DOWNLOAD FAILED: HTTP {e.code} {e.reason} — {url}")
        return False, e.code, ExitCode.DOWNLOAD_FAILED
    except urllib.error.URLError as e:
        print(f"{RED}  FAILED{RESET} — {e.reason}")
        print(f"\n{RED}[GTS-E{ExitCode.NETWORK_ERROR:03d}]{RESET} {ERROR_MESSAGES[ExitCode.NETWORK_ERROR]}")
        log_to_file(f"NETWORK ERROR: {e.reason} — {url}")
        return False, 1, ExitCode.NETWORK_ERROR
    except OSError as e:
        print(f"{RED}  FAILED{RESET} — {e}")
        log_to_file(f"DOWNLOAD OS ERROR: {e}")
        return False, 1, ExitCode.DOWNLOAD_FAILED

    # ── Step 2: Run the script interactively ──
    print(f"{YELLOW}[2/2]{RESET} Running install script...")
    print(f"{DIM}  (You may be prompted for your sudo password below){RESET}\n")
    print(f"{CYAN}{'─' * 70}{RESET}")

    try:
        # Run with full terminal access — stdin, stdout, stderr all inherited
        # This lets the user see all output and enter sudo password naturally
        result = subprocess.run(
            ["bash", script_path],
            timeout=600,  # 10 minute timeout
        )
        return_code = result.returncode
    except subprocess.TimeoutExpired:
        print(f"\n{RED}[GTS-E{ExitCode.INSTALL_TIMEOUT:03d}]{RESET} {ERROR_MESSAGES[ExitCode.INSTALL_TIMEOUT]}")
        log_to_file(f"INSTALL TIMEOUT: {theme_name}")
        return False, 124, ExitCode.INSTALL_TIMEOUT
    except KeyboardInterrupt:
        print(f"\n{YELLOW}  Installation cancelled by user.{RESET}")
        log_to_file(f"INSTALL CANCELLED: {theme_name}")
        return False, 130, ExitCode.GENERAL_ERROR
    except OSError as e:
        print(f"\n{RED}  Failed to run script: {e}{RESET}")
        log_to_file(f"INSTALL OS ERROR: {e}")
        return False, 1, ExitCode.INSTALL_SCRIPT_FAILED
    finally:
        # Cleanup temp script
        try:
            os.remove(script_path)
        except OSError:
            pass

    # ── Print result ──
    print(f"{CYAN}{'─' * 70}{RESET}")

    if return_code == 0:
        print(f"\n{GREEN}{BOLD}  INSTALLATION COMPLETE!{RESET}")
        print(f"{GREEN}  '{theme_name}' has been installed successfully.{RESET}")
        log_to_file(f"INSTALL SUCCESS: {theme_name} (exit code 0)")
    else:
        print(f"\n{RED}{BOLD}  INSTALLATION FAILED{RESET}")
        # Map common exit codes to helpful messages
        if return_code == 1:
            hint = "General error in the install script."
        elif return_code == 2:
            hint = "Shell syntax error or missing command."
        elif return_code == 100:
            hint = "apt/dpkg error — dependency installation failed."
            print(f"{RED}  [GTS-E{ExitCode.INSTALL_DEPS_FAILED:03d}]{RESET} {ERROR_MESSAGES[ExitCode.INSTALL_DEPS_FAILED]}")
        elif return_code == 126:
            hint = "Permission denied — script not executable."
        elif return_code == 127:
            hint = "Command not found — a required tool is missing."
        elif return_code == 128 + 9:
            hint = "Process was killed (SIGKILL)."
        elif return_code == 130:
            hint = "Cancelled by user (Ctrl+C)."
        else:
            hint = f"Script exited with code {return_code}."

        print(f"{RED}  Exit code: {return_code} — {hint}{RESET}")
        print(f"{DIM}  Check the install output above for details.{RESET}")
        print(f"{DIM}  Full log: {LOG_FILE}{RESET}")
        log_to_file(f"INSTALL FAILED: {theme_name} (exit code {return_code})")

    print(f"\n{CYAN}{'=' * 70}{RESET}")

    return return_code == 0, return_code, ExitCode.SUCCESS if return_code == 0 else ExitCode.INSTALL_SCRIPT_FAILED


# ═══════════════════════════════════════════════════════════════════════════════
#  TUI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class ThemeSwitcherTUI:
    """Main TUI application class using curses."""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.themes = get_all_themes()
        self.selected = 0
        self.scroll_offset = 0
        self.status_msg = ""
        self.status_type = "info"  # info, success, error, warning
        self.active_index = detect_active_theme_index(self.themes)
        self.mode = "browse"  # browse, confirm, add_custom, edit_custom, help, update_prompt
        self.confirm_action = None
        self.confirm_callback = None
        self.form_fields = {}
        self.form_field_order = []
        self.form_cursor = 0
        self.update_info = None
        self.needs_restart = False  # Set after self-update

        # Initialize curses
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_WHITE, -1)                       # Normal
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)       # Selected
        curses.init_pair(3, curses.COLOR_GREEN, -1)                       # Success / Active
        curses.init_pair(4, curses.COLOR_RED, -1)                         # Error
        curses.init_pair(5, curses.COLOR_YELLOW, -1)                      # Warning
        curses.init_pair(6, curses.COLOR_CYAN, -1)                        # Info / Headers
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)                     # Purple accent
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)        # Title bar
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)       # Status success
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_RED)        # Status error
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_YELLOW)     # Status warning
        curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_MAGENTA)    # Category header

    # ─── Status ──────────────────────────────────────────────────────────────

    def set_status(self, msg, msg_type="info"):
        """Set the status bar message."""
        self.status_msg = msg
        self.status_type = msg_type

    def refresh_themes(self):
        """Reload themes and detect active."""
        self.themes = get_all_themes()
        self.active_index = detect_active_theme_index(self.themes)
        if self.selected >= len(self.themes):
            self.selected = max(0, len(self.themes) - 1)

    # ─── Safe Drawing ────────────────────────────────────────────────────────

    def safe_addstr(self, y, x, text, attr=0):
        """Safely add a string, truncating if needed."""
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h or x >= w:
            return
        max_len = w - x - 1
        if max_len <= 0:
            return
        try:
            self.stdscr.addnstr(y, x, text, max_len, attr)
        except curses.error:
            pass

    # ─── Drawing Methods ─────────────────────────────────────────────────────

    def draw_title_bar(self):
        """Draw the title bar at the top."""
        h, w = self.stdscr.getmaxyx()
        title = f"  GNOME Theme Switcher v{VERSION}"
        if self.update_info and (self.update_info.get("switcher") or self.update_info.get("themes")):
            title += "  [UPDATE AVAILABLE]"
        right = "Press [?] for help  "
        padding = max(0, w - len(title) - len(right))
        bar = title + " " * padding + right
        self.safe_addstr(0, 0, bar[:w-1], curses.color_pair(8) | curses.A_BOLD)

    def draw_status_bar(self):
        """Draw the status bar at the bottom."""
        h, w = self.stdscr.getmaxyx()
        type_map = {
            "success": curses.color_pair(9) | curses.A_BOLD,
            "error": curses.color_pair(10) | curses.A_BOLD,
            "warning": curses.color_pair(11) | curses.A_BOLD,
        }
        attr = type_map.get(self.status_type, curses.color_pair(8))
        bar = f"  {self.status_msg}" if self.status_msg else ""
        bar = bar + " " * max(0, w - len(bar) - 1)
        self.safe_addstr(h - 1, 0, bar[:w-1], attr)

    def draw_keybinds_bar(self):
        """Draw the keybindings bar above the status bar."""
        h, w = self.stdscr.getmaxyx()
        keys_map = {
            "browse": " [Enter] Apply  [i] Install  [a] Add  [e] Edit  [d] Del  [b] Backup  [r] Restore  [u] Update  [q] Quit",
            "confirm": " [y] Yes  [n] No / Cancel",
            "add_custom": " [Tab] Next  [Shift+Tab] Prev  [Enter] on last = Save  [Esc] Cancel",
            "edit_custom": " [Tab] Next  [Shift+Tab] Prev  [Enter] on last = Save  [Esc] Cancel",
            "update_prompt": " [y] Update now  [n] Skip  [Esc] Cancel",
            "help": " Press any key to close",
        }
        keys = keys_map.get(self.mode, " [q] Quit")
        self.safe_addstr(h - 2, 0, keys[:w-1], curses.color_pair(6))

    def draw_theme_list(self):
        """Draw the theme list on the left panel."""
        h, w = self.stdscr.getmaxyx()
        list_width = min(35, w // 2 - 1)
        list_start_y = 2
        list_height = h - 5

        self.safe_addstr(list_start_y, 1, "Themes", curses.color_pair(6) | curses.A_BOLD | curses.A_UNDERLINE)

        visible_count = list_height - 1
        if self.selected < self.scroll_offset:
            self.scroll_offset = self.selected
        elif self.selected >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected - visible_count + 1

        current_category = ""
        draw_y = list_start_y + 1
        item_index = 0

        for i, theme in enumerate(self.themes):
            if item_index < self.scroll_offset:
                cat = theme.get("category", "Custom")
                if not theme.get("builtin", False):
                    cat = "Custom"
                if cat != current_category:
                    current_category = cat
                item_index += 1
                continue

            if draw_y >= h - 3:
                break

            cat = theme.get("category", "Custom")
            if not theme.get("builtin", False):
                cat = "Custom"
            if cat != current_category:
                current_category = cat
                if draw_y < h - 3:
                    self.safe_addstr(draw_y, 2, f"── {cat} ──", curses.color_pair(7) | curses.A_BOLD)
                    draw_y += 1
                    if draw_y >= h - 3:
                        break

            is_selected = (i == self.selected)
            is_active = (i == self.active_index)
            installed = check_theme_installed(theme)

            prefix = ">" if is_selected else " "
            status_icon = "●" if is_active else ("◌" if installed else "○")
            entry = f" {prefix} {status_icon} {theme['name']}"

            if is_selected:
                attr = curses.color_pair(2) | curses.A_BOLD
            elif is_active:
                attr = curses.color_pair(3) | curses.A_BOLD
            elif installed:
                attr = curses.color_pair(1)
            else:
                attr = curses.color_pair(1) | curses.A_DIM

            self.safe_addstr(draw_y, 1, entry[:list_width].ljust(list_width), attr)
            draw_y += 1
            item_index += 1

        if self.scroll_offset > 0:
            self.safe_addstr(list_start_y + 1, list_width - 1, "▲", curses.color_pair(5))
        if self.scroll_offset + visible_count < len(self.themes):
            self.safe_addstr(min(h - 4, draw_y), list_width - 1, "▼", curses.color_pair(5))

    def draw_detail_panel(self):
        """Draw the detail panel on the right side."""
        h, w = self.stdscr.getmaxyx()
        list_width = min(35, w // 2 - 1)
        panel_x = list_width + 2
        panel_width = w - panel_x - 2
        panel_y = 2

        if panel_width < 20:
            return

        for y in range(2, h - 2):
            self.safe_addstr(y, list_width + 1, "│", curses.color_pair(6))

        if not self.themes:
            return

        theme = self.themes[self.selected]
        is_active = (self.selected == self.active_index)
        installed = check_theme_installed(theme)

        self.safe_addstr(panel_y, panel_x, "Details", curses.color_pair(6) | curses.A_BOLD | curses.A_UNDERLINE)
        panel_y += 2

        self.safe_addstr(panel_y, panel_x, theme["name"], curses.color_pair(7) | curses.A_BOLD)
        panel_y += 1

        badge_x = panel_x
        if is_active:
            self.safe_addstr(panel_y, badge_x, " ACTIVE ", curses.color_pair(9) | curses.A_BOLD)
            badge_x += 10
        if installed:
            self.safe_addstr(panel_y, badge_x, " INSTALLED ", curses.color_pair(3))
        else:
            self.safe_addstr(panel_y, badge_x, " NOT INSTALLED ", curses.color_pair(5))
        panel_y += 2

        details = [
            ("Category", theme.get("category", "Custom")),
            ("GTK Theme", theme.get("gtk_theme", "—")),
            ("Shell Theme", theme.get("shell_theme", "—")),
            ("Icon Theme", theme.get("icon_theme", "—")),
            ("Cursor Theme", theme.get("cursor_theme", "—")),
            ("Color Scheme", theme.get("color_scheme", "—")),
        ]

        label_width = 14
        for label, value in details:
            if panel_y >= h - 5:
                break
            self.safe_addstr(panel_y, panel_x, f"{label}:", curses.color_pair(6))
            self.safe_addstr(panel_y, panel_x + label_width + 1, str(value)[:panel_width - label_width - 2], curses.color_pair(1))
            panel_y += 1

        panel_y += 1

        desc = theme.get("description", "")
        if desc and panel_y < h - 5:
            self.safe_addstr(panel_y, panel_x, "Description:", curses.color_pair(6))
            panel_y += 1
            words = desc.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > panel_width - 1:
                    if panel_y >= h - 5:
                        break
                    self.safe_addstr(panel_y, panel_x, line, curses.color_pair(1) | curses.A_DIM)
                    panel_y += 1
                    line = word
                else:
                    line = f"{line} {word}" if line else word
            if line and panel_y < h - 5:
                self.safe_addstr(panel_y, panel_x, line, curses.color_pair(1) | curses.A_DIM)
                panel_y += 1

        panel_y += 1
        url = theme.get("install_url", "")
        if url and panel_y < h - 5:
            self.safe_addstr(panel_y, panel_x, "Install URL:", curses.color_pair(6))
            panel_y += 1
            self.safe_addstr(panel_y, panel_x, url[:panel_width - 1], curses.color_pair(1) | curses.A_DIM)

    def draw_confirm_dialog(self):
        """Draw a confirmation dialog in the center of the screen."""
        h, w = self.stdscr.getmaxyx()
        msg = self.confirm_action or "Are you sure?"
        box_w = min(60, w - 4)
        box_h = 7
        start_y = (h - box_h) // 2
        start_x = (w - box_w) // 2

        for y in range(start_y, start_y + box_h):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, start_y + box_h - 1):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        title = " Confirm "
        self.safe_addstr(start_y, start_x + (box_w - len(title)) // 2, title, curses.color_pair(11) | curses.A_BOLD)

        inner_w = box_w - 4
        words = msg.split()
        lines = []
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > inner_w:
                lines.append(line)
                line = word
            else:
                line = f"{line} {word}" if line else word
        if line:
            lines.append(line)

        for i, ln in enumerate(lines[:3]):
            self.safe_addstr(start_y + 2 + i, start_x + 2, ln, curses.color_pair(8))

        btn_text = "[Y] Yes    [N] No"
        self.safe_addstr(start_y + box_h - 2, start_x + (box_w - len(btn_text)) // 2, btn_text, curses.color_pair(8) | curses.A_BOLD)

    def draw_update_dialog(self):
        """Draw an update notification dialog."""
        h, w = self.stdscr.getmaxyx()
        box_w = min(64, w - 4)
        lines = [" Updates Available "]
        if self.update_info.get("switcher"):
            sw = self.update_info["switcher"]
            lines.append(f"  Theme Switcher: {sw['current']} -> {sw['latest']}")
        if self.update_info.get("themes"):
            th = self.update_info["themes"]
            lines.append(f"  Theme Collection: {th['current']} -> {th['latest']}")
        lines.append("")
        lines.append("  [Y] Update now    [N] Skip this time")

        box_h = len(lines) + 4
        start_y = (h - box_h) // 2
        start_x = (w - box_w) // 2

        for y in range(start_y, start_y + box_h):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, start_y + box_h - 1):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        title = lines[0]
        self.safe_addstr(start_y, start_x + (box_w - len(title)) // 2, title, curses.color_pair(11) | curses.A_BOLD)

        for i, ln in enumerate(lines[1:]):
            self.safe_addstr(start_y + 2 + i, start_x + 2, ln[:box_w - 4], curses.color_pair(8))

    def draw_form(self, title, fields, field_order, cursor_pos):
        """Draw a form dialog for adding/editing custom themes."""
        h, w = self.stdscr.getmaxyx()
        box_w = min(70, w - 4)
        box_h = min(len(field_order) * 2 + 6, h - 4)
        start_y = max(1, (h - box_h) // 2)
        start_x = max(1, (w - box_w) // 2)

        for y in range(start_y, min(start_y + box_h, h)):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, min(start_y + box_h - 1, h - 1)):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        if start_y + box_h - 1 < h:
            self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        title_str = f" {title} "
        self.safe_addstr(start_y, start_x + (box_w - len(title_str)) // 2, title_str, curses.color_pair(12) | curses.A_BOLD)

        inner_w = box_w - 4
        draw_y = start_y + 2
        for i, key in enumerate(field_order):
            if draw_y + 1 >= start_y + box_h - 1:
                break
            label = key.replace("_", " ").title() + ":"
            value = fields.get(key, "")
            is_active = (i == cursor_pos)

            label_attr = curses.color_pair(8) | curses.A_BOLD if is_active else curses.color_pair(8)
            self.safe_addstr(draw_y, start_x + 2, label[:inner_w], label_attr)
            draw_y += 1

            if is_active:
                field_attr = curses.color_pair(2)
                display = value + "█"
            else:
                field_attr = curses.color_pair(8) | curses.A_DIM
                display = value if value else "(empty)"

            self.safe_addstr(draw_y, start_x + 2, display[:inner_w].ljust(inner_w), field_attr)
            draw_y += 1

        if draw_y < start_y + box_h - 1:
            footer = "[Tab] Next  [Esc] Cancel  [Enter on last] Save"
            self.safe_addstr(start_y + box_h - 2, start_x + (box_w - len(footer)) // 2, footer, curses.color_pair(8) | curses.A_DIM)

    def draw_help_screen(self):
        """Draw a help overlay."""
        h, w = self.stdscr.getmaxyx()
        box_w = min(62, w - 4)
        help_lines = [
            "",
            "  GNOME Theme Switcher — Keyboard Shortcuts",
            "  ──────────────────────────────────────────",
            "",
            "  Navigation:",
            "    Up / k         Move up",
            "    Down / j       Move down",
            "    Home / g       Jump to first theme",
            "    End / G        Jump to last theme",
            "",
            "  Actions:",
            "    Enter          Apply selected theme",
            "    i              Install selected theme",
            "    a              Add a custom theme",
            "    e              Edit selected custom theme",
            "    d              Delete selected custom theme",
            "",
            "  Backup / Restore:",
            "    b              Backup current theme settings",
            "    r              Restore theme from backup",
            "",
            "  Updates:",
            "    u              Check for updates",
            "",
            "  Other:",
            "    ?              Show this help screen",
            "    q / Esc        Quit (or close dialog)",
            "",
            "  Legend:",
            "    ●  Currently active theme",
            "    ◌  Installed but not active",
            "    ○  Not installed",
            "",
            "  Error codes: GTS-E0xx (see README for details)",
            "",
            "  Press any key to close this help screen.",
        ]
        box_h = min(len(help_lines) + 2, h - 2)
        start_y = max(0, (h - box_h) // 2)
        start_x = max(0, (w - box_w) // 2)

        for y in range(start_y, min(start_y + box_h, h)):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, min(start_y + box_h - 1, h - 1)):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        if start_y + box_h - 1 < h:
            self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        for i, line in enumerate(help_lines[:box_h - 2]):
            if start_y + 1 + i < h - 1:
                if "──" in line or "Shortcuts" in line:
                    attr = curses.color_pair(8) | curses.A_BOLD
                else:
                    attr = curses.color_pair(8)
                self.safe_addstr(start_y + 1 + i, start_x + 1, line[:box_w - 3], attr)

    # ─── Main Draw ───────────────────────────────────────────────────────────

    def draw(self):
        """Main draw method."""
        self.stdscr.erase()
        self.draw_title_bar()
        self.draw_theme_list()
        self.draw_detail_panel()
        self.draw_keybinds_bar()
        self.draw_status_bar()

        if self.mode == "confirm":
            self.draw_confirm_dialog()
        elif self.mode in ("add_custom", "edit_custom"):
            title = "Add Custom Theme" if self.mode == "add_custom" else "Edit Custom Theme"
            self.draw_form(title, self.form_fields, self.form_field_order, self.form_cursor)
        elif self.mode == "help":
            self.draw_help_screen()
        elif self.mode == "update_prompt":
            self.draw_update_dialog()

        self.stdscr.refresh()

    # ─── Form Handling ───────────────────────────────────────────────────────

    def start_add_custom(self):
        """Initialize the add custom theme form."""
        self.mode = "add_custom"
        self.form_fields = {
            "name": "", "category": "Custom", "gtk_theme": "", "shell_theme": "",
            "icon_theme": "", "cursor_theme": "", "color_scheme": "prefer-dark",
            "description": "", "install_url": "",
        }
        self.form_field_order = list(self.form_fields.keys())
        self.form_cursor = 0

    def start_edit_custom(self):
        """Initialize the edit custom theme form for the selected theme."""
        if self.selected >= len(self.themes):
            return
        theme = self.themes[self.selected]
        if theme.get("builtin", False):
            self.set_status("Cannot edit built-in themes. Use [a] to add a custom variant.", "warning")
            return
        self.mode = "edit_custom"
        self.form_fields = {k: theme.get(k, "") for k in [
            "name", "category", "gtk_theme", "shell_theme", "icon_theme",
            "cursor_theme", "color_scheme", "description", "install_url"
        ]}
        self.form_field_order = list(self.form_fields.keys())
        self.form_cursor = 0

    def save_form(self):
        """Save the current form as a custom theme."""
        name = self.form_fields.get("name", "").strip()
        if not name:
            self.set_status("Theme name cannot be empty!", "error")
            return False
        gtk = self.form_fields.get("gtk_theme", "").strip()
        if not gtk:
            self.set_status("GTK theme name cannot be empty!", "error")
            return False

        new_theme = {
            "name": name,
            "category": self.form_fields.get("category", "Custom").strip() or "Custom",
            "gtk_theme": gtk,
            "shell_theme": self.form_fields.get("shell_theme", "").strip() or gtk,
            "icon_theme": self.form_fields.get("icon_theme", "").strip(),
            "cursor_theme": self.form_fields.get("cursor_theme", "").strip(),
            "color_scheme": self.form_fields.get("color_scheme", "prefer-dark").strip() or "prefer-dark",
            "description": self.form_fields.get("description", "").strip(),
            "install_url": self.form_fields.get("install_url", "").strip(),
            "builtin": False,
        }

        custom_themes = load_custom_themes()
        if self.mode == "edit_custom":
            custom_index = self.selected - len(BUILTIN_THEMES)
            if 0 <= custom_index < len(custom_themes):
                custom_themes[custom_index] = new_theme
        else:
            custom_themes.append(new_theme)

        save_custom_themes(custom_themes)
        self.refresh_themes()
        self.mode = "browse"
        self.set_status(f"Theme '{name}' saved successfully!", "success")
        return True

    # ─── Input Handlers ──────────────────────────────────────────────────────

    def handle_form_input(self, key):
        """Handle input in form mode."""
        if key == 27:  # Escape
            self.mode = "browse"
            self.set_status("Cancelled.", "info")
            return

        current_field = self.form_field_order[self.form_cursor]

        if key == 9:  # Tab
            self.form_cursor = (self.form_cursor + 1) % len(self.form_field_order)
        elif key == curses.KEY_BTAB or key == 353:  # Shift+Tab
            self.form_cursor = (self.form_cursor - 1) % len(self.form_field_order)
        elif key in (10, curses.KEY_ENTER):
            if self.form_cursor == len(self.form_field_order) - 1:
                self.save_form()
            else:
                self.form_cursor = (self.form_cursor + 1) % len(self.form_field_order)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            val = self.form_fields.get(current_field, "")
            self.form_fields[current_field] = val[:-1]
        elif 32 <= key <= 126:
            val = self.form_fields.get(current_field, "")
            self.form_fields[current_field] = val + chr(key)

    def handle_confirm_input(self, key):
        """Handle input in confirm mode."""
        if key in (ord('y'), ord('Y')):
            if self.confirm_callback:
                self.confirm_callback()
            self.mode = "browse"
        elif key in (ord('n'), ord('N'), 27):
            self.mode = "browse"
            self.set_status("Cancelled.", "info")

    def handle_update_prompt_input(self, key):
        """Handle input in update prompt mode."""
        if key in (ord('y'), ord('Y')):
            self.mode = "browse"
            if self.update_info and self.update_info.get("switcher"):
                self.set_status("Updating theme switcher...", "info")
                self.draw()
                success, msg, code = self_update()
                if success:
                    self.set_status(msg, "success")
                    self.needs_restart = True
                else:
                    self.set_status(f"[GTS-E{code:03d}] {msg}", "error")
            else:
                self.set_status("No switcher update needed. Theme repo updates are noted.", "info")
        elif key in (ord('n'), ord('N'), 27):
            self.mode = "browse"
            self.set_status("Update skipped.", "info")

    def do_update_check(self):
        """Perform update check and show dialog if updates available."""
        self.set_status("Checking for updates...", "info")
        self.draw()
        try:
            results = check_for_updates()
            save_update_check(results)
            if results.get("switcher") or results.get("themes"):
                self.update_info = results
                self.mode = "update_prompt"
            else:
                self.set_status(f"Everything is up to date! (v{VERSION})", "success")
        except Exception:
            self.set_status(f"[GTS-E{ExitCode.NETWORK_ERROR:03d}] Update check failed. Check your connection.", "error")

    # ─── Install (suspends curses) ───────────────────────────────────────────

    def do_install(self, theme):
        """Suspend curses, run install in real terminal, then resume."""
        url = theme.get("install_url", "")
        name = theme["name"]

        # Suspend curses — return terminal to normal mode
        curses.endwin()

        try:
            success, return_code, error_code = run_install_in_terminal(url, name)
        except Exception as e:
            success = False
            return_code = 1
            error_code = ExitCode.GENERAL_ERROR
            print(f"\n\033[31m[GTS-E{error_code:03d}] Unexpected error: {e}\033[0m")
            log_to_file(f"INSTALL EXCEPTION: {e}\n{traceback.format_exc()}")

        # Prompt user before returning to TUI
        print()
        input("\033[36m  Press Enter to return to the theme switcher...\033[0m")

        # Resume curses
        self.stdscr.refresh()
        curses.doupdate()
        curses.curs_set(0)

        # Update state
        self.refresh_themes()

        if success:
            self.set_status(f"'{name}' installed! Press [Enter] to apply it.", "success")
        else:
            self.set_status(
                f"[GTS-E{error_code:03d}] Install of '{name}' failed (exit {return_code}). See log: {LOG_FILE}",
                "error"
            )

    # ─── Main Event Loop ─────────────────────────────────────────────────────

    def run(self):
        """Main event loop."""
        self.set_status("Welcome! Use Up/Down to browse, Enter to apply, [i] to install, [?] for help.", "info")

        # Check for updates on startup
        if should_check_updates():
            try:
                results = check_for_updates()
                save_update_check(results)
                if results.get("switcher") or results.get("themes"):
                    self.update_info = results
                    self.mode = "update_prompt"
            except Exception:
                pass

        self.stdscr.timeout(250)

        while True:
            try:
                self.draw()
            except curses.error:
                # Terminal too small or other drawing error — wait for resize
                time.sleep(0.1)
                continue

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break
            except curses.error:
                continue

            if key == -1:
                continue

            if key == curses.KEY_RESIZE:
                continue

            # ── Mode-specific input ──
            if self.mode == "help":
                self.mode = "browse"
                continue

            if self.mode == "update_prompt":
                self.handle_update_prompt_input(key)
                continue

            if self.mode == "confirm":
                self.handle_confirm_input(key)
                continue

            if self.mode in ("add_custom", "edit_custom"):
                self.handle_form_input(key)
                continue

            # ── Browse mode ──
            if key in (ord('q'), ord('Q')):
                break

            elif key == 27:  # Escape also quits from browse
                break

            elif key == ord('?'):
                self.mode = "help"

            elif key in (curses.KEY_UP, ord('k')):
                if self.selected > 0:
                    self.selected -= 1

            elif key in (curses.KEY_DOWN, ord('j')):
                if self.selected < len(self.themes) - 1:
                    self.selected += 1

            elif key in (curses.KEY_HOME, ord('g')):
                self.selected = 0
                self.scroll_offset = 0

            elif key in (curses.KEY_END, ord('G')):
                self.selected = len(self.themes) - 1

            elif key in (10, curses.KEY_ENTER):  # Apply
                if not self.themes:
                    continue
                theme = self.themes[self.selected]
                if not check_theme_installed(theme):
                    self.set_status(f"'{theme['name']}' is not installed. Press [i] to install first.", "warning")
                    continue

                def do_apply(t=theme):
                    ok, data = backup_current_theme()
                    if not ok:
                        self.set_status(f"[GTS-E{ExitCode.BACKUP_FAILED:03d}] Backup failed: {data}", "warning")
                    success, errors = apply_theme(t)
                    if success:
                        self.active_index = self.selected
                        self.set_status(f"Applied '{t['name']}'! Log out to see full changes.", "success")
                    else:
                        err_summary = errors[0] if errors else "Unknown error"
                        self.set_status(f"[GTS-E{ExitCode.GENERAL_ERROR:03d}] Partial apply: {err_summary}", "error")
                        log_to_file(f"APPLY ERRORS for {t['name']}:\n" + "\n".join(errors))

                self.confirm_action = f"Apply '{theme['name']}'? This changes GTK, Shell, Icons, Cursors."
                self.confirm_callback = do_apply
                self.mode = "confirm"

            elif key in (ord('i'), ord('I')):  # Install
                if not self.themes:
                    continue
                theme = self.themes[self.selected]
                url = theme.get("install_url", "")
                if not url:
                    self.set_status(f"No install URL for '{theme['name']}'. Install manually.", "warning")
                    continue

                def do_install_confirm(t=theme):
                    self.do_install(t)

                self.confirm_action = f"Install '{theme['name']}'? This downloads and runs the install script."
                self.confirm_callback = do_install_confirm
                self.mode = "confirm"

            elif key in (ord('a'), ord('A')):
                self.start_add_custom()

            elif key in (ord('e'), ord('E')):
                self.start_edit_custom()

            elif key in (ord('d'), ord('D')):
                if not self.themes:
                    continue
                theme = self.themes[self.selected]
                if theme.get("builtin", False):
                    self.set_status("Cannot delete built-in themes.", "warning")
                    continue

                def do_delete():
                    custom_themes = load_custom_themes()
                    custom_index = self.selected - len(BUILTIN_THEMES)
                    if 0 <= custom_index < len(custom_themes):
                        removed = custom_themes.pop(custom_index)
                        save_custom_themes(custom_themes)
                        self.refresh_themes()
                        self.set_status(f"Deleted '{removed['name']}'.", "success")

                self.confirm_action = f"Delete custom theme '{theme['name']}'? This cannot be undone."
                self.confirm_callback = do_delete
                self.mode = "confirm"

            elif key in (ord('b'), ord('B')):
                ok, data = backup_current_theme()
                if ok:
                    self.set_status(f"Theme backed up at {data.get('timestamp', 'now')}.", "success")
                else:
                    self.set_status(f"[GTS-E{ExitCode.BACKUP_FAILED:03d}] {data}", "error")

            elif key in (ord('r'), ord('R')):
                backup = load_backup()
                if not backup:
                    self.set_status("No backup found. Press [b] to create one first.", "warning")
                    continue

                def do_restore():
                    success, errors = restore_backup()
                    if success:
                        self.refresh_themes()
                        self.set_status(f"Restored from backup ({backup.get('timestamp', '?')}).", "success")
                    else:
                        self.set_status(f"[GTS-E{ExitCode.RESTORE_FAILED:03d}] Restore failed.", "error")

                ts = backup.get("timestamp", "unknown")
                self.confirm_action = f"Restore from backup ({ts})? GTK: {backup.get('gtk_theme', '?')}"
                self.confirm_callback = do_restore
                self.mode = "confirm"

            elif key in (ord('u'), ord('U')):
                self.do_update_check()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main(stdscr):
    """Entry point for curses wrapper."""
    app = ThemeSwitcherTUI(stdscr)
    app.run()


if __name__ == "__main__":
    # ── Pre-flight checks ──
    if not sys.stdout.isatty():
        print(f"[GTS-E{ExitCode.NOT_A_TERMINAL:03d}] {ERROR_MESSAGES[ExitCode.NOT_A_TERMINAL]}")
        sys.exit(ExitCode.NOT_A_TERMINAL)

    if not check_gsettings():
        print(f"[GTS-E{ExitCode.GSETTINGS_NOT_FOUND:03d}] {ERROR_MESSAGES[ExitCode.GSETTINGS_NOT_FOUND]}")
        sys.exit(ExitCode.GSETTINGS_NOT_FOUND)

    ensure_config_dir()

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(ExitCode.SUCCESS)
    except curses.error as e:
        print(f"\n[GTS-E{ExitCode.CURSES_INIT_FAILED:03d}] {ERROR_MESSAGES[ExitCode.CURSES_INIT_FAILED]}")
        print(f"  Detail: {e}")
        print(f"  Try resizing your terminal to at least 80x24.")
        sys.exit(ExitCode.CURSES_INIT_FAILED)
    except Exception as e:
        print(f"\n[GTS-E{ExitCode.GENERAL_ERROR:03d}] {ERROR_MESSAGES[ExitCode.GENERAL_ERROR]}")
        print(f"  Detail: {e}")
        print(f"  Traceback saved to: {LOG_FILE}")
        try:
            log_to_file(f"FATAL: {e}\n{traceback.format_exc()}")
        except Exception:
            pass
        sys.exit(ExitCode.GENERAL_ERROR)
