#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Naftali <https://github.com/Naftaliro>
"""
GNOME Theme Switcher

This software is provided "as is", without warranty of any kind, express or implied.
Use at your own risk. For full details, see the LICENSE file in the repository.
This project is not affiliated with any of the upstream theme authors.

Copyright (c) 2026 Naftali
"""

import curses
import json
import os
import subprocess
import sys
import shutil
import copy
from pathlib import Path
from datetime import datetime

# ─── Paths ────────────────────────────────────────────────────────────────────
CONFIG_DIR = Path.home() / ".config" / "gnome-theme-switcher"
CUSTOM_THEMES_FILE = CONFIG_DIR / "custom_themes.json"
BACKUP_FILE = CONFIG_DIR / "backup.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

VERSION = "1.2.0"

# ─── Base URL for install scripts ─────────────────────────────────────────────
REPO_BASE = "https://raw.githubusercontent.com/Naftaliro/zorinos-gnome-themes/v1.2.0"

# ─── Built-in Theme Definitions ──────────────────────────────────────────────
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
        "gtk_theme": "Orchis-purple-Dark",
        "shell_theme": "Orchis-purple-Dark",
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


# ─── Utility Functions ────────────────────────────────────────────────────────

def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_custom_themes():
    """Load custom themes from the JSON config file."""
    if CUSTOM_THEMES_FILE.exists():
        try:
            with open(CUSTOM_THEMES_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_custom_themes(themes):
    """Save custom themes to the JSON config file."""
    ensure_config_dir()
    with open(CUSTOM_THEMES_FILE, "w") as f:
        json.dump(themes, f, indent=2)


def get_all_themes():
    """Return builtin themes + custom themes."""
    custom = load_custom_themes()
    return BUILTIN_THEMES + custom


def gsettings_get(schema, key):
    """Get a gsettings value, return empty string on failure."""
    try:
        result = subprocess.run(
            ["gsettings", "get", schema, key],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().strip("'\"")
    except Exception:
        return ""


def gsettings_set(schema, key, value):
    """Set a gsettings value. Returns True on success."""
    try:
        subprocess.run(
            ["gsettings", "set", schema, key, value],
            capture_output=True, text=True, timeout=5, check=True
        )
        return True
    except Exception:
        return False


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
    """Apply a theme by setting all gsettings keys."""
    results = []
    results.append(gsettings_set("org.gnome.desktop.interface", "gtk-theme", theme["gtk_theme"]))
    results.append(gsettings_set("org.gnome.desktop.wm.preferences", "theme", theme["gtk_theme"]))
    results.append(gsettings_set("org.gnome.shell.extensions.user-theme", "name", theme.get("shell_theme", theme["gtk_theme"])))
    results.append(gsettings_set("org.gnome.desktop.interface", "icon-theme", theme["icon_theme"]))
    results.append(gsettings_set("org.gnome.desktop.interface", "cursor-theme", theme["cursor_theme"]))
    results.append(gsettings_set("org.gnome.desktop.interface", "color-scheme", theme.get("color_scheme", "prefer-dark")))
    return all(results)


def backup_current_theme():
    """Backup current theme settings to a JSON file."""
    ensure_config_dir()
    current = get_current_theme_settings()
    current["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(BACKUP_FILE, "w") as f:
        json.dump(current, f, indent=2)
    return current


def load_backup():
    """Load backup theme settings."""
    if BACKUP_FILE.exists():
        try:
            with open(BACKUP_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def restore_backup():
    """Restore theme from backup."""
    backup = load_backup()
    if backup:
        apply_theme(backup)
        return True
    return False


def check_theme_installed(theme):
    """Check if a theme's GTK theme directory exists."""
    gtk_name = theme.get("gtk_theme", "")
    if not gtk_name:
        return False
    # Check user themes
    user_dir = Path.home() / ".themes" / gtk_name
    user_local_dir = Path.home() / ".local" / "share" / "themes" / gtk_name
    system_dir = Path("/usr/share/themes") / gtk_name
    return user_dir.exists() or user_local_dir.exists() or system_dir.exists()


def detect_active_theme_index(themes):
    """Find which theme matches the currently active settings."""
    current = get_current_theme_settings()
    gtk = current.get("gtk_theme", "")
    for i, t in enumerate(themes):
        if t.get("gtk_theme", "") == gtk:
            return i
    return -1


def run_install_script(url):
    """Run an install script from a URL using curl | bash in a subprocess."""
    try:
        proc = subprocess.Popen(
            ["bash", "-c", f"curl -fsSL '{url}' | bash"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return proc
    except Exception:
        return None


# ─── TUI Application ─────────────────────────────────────────────────────────

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
        self.mode = "browse"  # browse, install, add_custom, edit_custom, confirm
        self.confirm_action = None
        self.confirm_callback = None
        self.form_fields = {}
        self.form_field_order = []
        self.form_cursor = 0
        self.install_proc = None
        self.install_output = []

        # Initialize curses
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_WHITE, -1)       # Normal
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
        curses.init_pair(3, curses.COLOR_GREEN, -1)        # Success / Active
        curses.init_pair(4, curses.COLOR_RED, -1)          # Error
        curses.init_pair(5, curses.COLOR_YELLOW, -1)       # Warning
        curses.init_pair(6, curses.COLOR_CYAN, -1)         # Info / Headers
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)      # Purple accent
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_CYAN)   # Title bar
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Status success
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_RED)   # Status error
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Status warning
        curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # Category header

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

    def draw_title_bar(self):
        """Draw the title bar at the top."""
        h, w = self.stdscr.getmaxyx()
        title = f"  GNOME Theme Switcher v{VERSION}"
        right = "Press [?] for help  "
        bar = title + " " * max(0, w - len(title) - len(right)) + right
        self.safe_addstr(0, 0, bar[:w-1], curses.color_pair(8) | curses.A_BOLD)

    def draw_status_bar(self):
        """Draw the status bar at the bottom."""
        h, w = self.stdscr.getmaxyx()
        if self.status_type == "success":
            attr = curses.color_pair(9) | curses.A_BOLD
        elif self.status_type == "error":
            attr = curses.color_pair(10) | curses.A_BOLD
        elif self.status_type == "warning":
            attr = curses.color_pair(11) | curses.A_BOLD
        else:
            attr = curses.color_pair(8)

        bar = f"  {self.status_msg}" if self.status_msg else ""
        bar = bar + " " * max(0, w - len(bar) - 1)
        self.safe_addstr(h - 1, 0, bar[:w-1], attr)

    def draw_keybinds_bar(self):
        """Draw the keybindings bar above the status bar."""
        h, w = self.stdscr.getmaxyx()
        if self.mode == "browse":
            keys = " [Enter] Apply  [i] Install  [a] Add Custom  [e] Edit  [d] Delete  [b] Backup  [r] Restore  [q] Quit"
        elif self.mode == "confirm":
            keys = " [y] Yes  [n] No / Cancel"
        elif self.mode in ("add_custom", "edit_custom"):
            keys = " [Tab] Next Field  [Shift+Tab] Prev  [Enter] on last field to Save  [Esc] Cancel"
        else:
            keys = " [q] Quit"
        self.safe_addstr(h - 2, 0, keys[:w-1], curses.color_pair(6))

    def draw_theme_list(self):
        """Draw the theme list on the left panel."""
        h, w = self.stdscr.getmaxyx()
        list_width = min(35, w // 2 - 1)
        list_start_y = 2
        list_height = h - 5  # Leave room for title, keybinds, status

        # Header
        self.safe_addstr(list_start_y, 1, "Themes", curses.color_pair(6) | curses.A_BOLD | curses.A_UNDERLINE)

        # Calculate visible range
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
                # Check if we need to account for category headers
                cat = theme.get("category", "Custom")
                if not theme.get("builtin", False):
                    cat = "Custom"
                if cat != current_category:
                    current_category = cat
                item_index += 1
                continue

            if draw_y >= h - 3:
                break

            # Category separator
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

            # Theme entry
            is_selected = (i == self.selected)
            is_active = (i == self.active_index)
            installed = check_theme_installed(theme)

            # Build the display string
            prefix = ">"  if is_selected else " "
            status_icon = "●" if is_active else ("◌" if installed else "○")
            name = theme["name"]
            entry = f" {prefix} {status_icon} {name}"

            if is_selected:
                attr = curses.color_pair(2) | curses.A_BOLD
            elif is_active:
                attr = curses.color_pair(3) | curses.A_BOLD
            elif installed:
                attr = curses.color_pair(1)
            else:
                attr = curses.color_pair(1) | curses.A_DIM

            # Pad to fill the column
            entry = entry[:list_width].ljust(list_width)
            self.safe_addstr(draw_y, 1, entry, attr)
            draw_y += 1
            item_index += 1

        # Scroll indicators
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

        # Vertical separator
        for y in range(2, h - 2):
            self.safe_addstr(y, list_width + 1, "│", curses.color_pair(6))

        if not self.themes:
            return

        theme = self.themes[self.selected]
        is_active = (self.selected == self.active_index)
        installed = check_theme_installed(theme)

        # Header
        self.safe_addstr(panel_y, panel_x, "Details", curses.color_pair(6) | curses.A_BOLD | curses.A_UNDERLINE)
        panel_y += 2

        # Theme name
        self.safe_addstr(panel_y, panel_x, theme["name"], curses.color_pair(7) | curses.A_BOLD)
        panel_y += 1

        # Status badges
        if is_active:
            self.safe_addstr(panel_y, panel_x, " ACTIVE ", curses.color_pair(9) | curses.A_BOLD)
            badge_offset = 10
        else:
            badge_offset = 0

        if installed:
            self.safe_addstr(panel_y, panel_x + badge_offset, " INSTALLED ", curses.color_pair(3))
        else:
            self.safe_addstr(panel_y, panel_x + badge_offset, " NOT INSTALLED ", curses.color_pair(5))
        panel_y += 2

        # Details table
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

        # Description
        desc = theme.get("description", "")
        if desc and panel_y < h - 5:
            self.safe_addstr(panel_y, panel_x, "Description:", curses.color_pair(6))
            panel_y += 1
            # Word wrap
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

        # Install URL
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

        # Draw box
        for y in range(start_y, start_y + box_h):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        # Border
        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, start_y + box_h - 1):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        # Title
        title = " Confirm "
        title_x = start_x + (box_w - len(title)) // 2
        self.safe_addstr(start_y, title_x, title, curses.color_pair(11) | curses.A_BOLD)

        # Message (word wrap)
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

        # Buttons
        btn_text = "[Y] Yes    [N] No"
        btn_x = start_x + (box_w - len(btn_text)) // 2
        self.safe_addstr(start_y + box_h - 2, btn_x, btn_text, curses.color_pair(8) | curses.A_BOLD)

    def draw_form(self, title, fields, field_order, cursor_pos):
        """Draw a form dialog for adding/editing custom themes."""
        h, w = self.stdscr.getmaxyx()
        box_w = min(70, w - 4)
        box_h = min(len(field_order) * 2 + 6, h - 4)
        start_y = max(1, (h - box_h) // 2)
        start_x = max(1, (w - box_w) // 2)

        # Clear area
        for y in range(start_y, min(start_y + box_h, h)):
            self.safe_addstr(y, start_x, " " * box_w, curses.color_pair(8))

        # Border
        self.safe_addstr(start_y, start_x, "┌" + "─" * (box_w - 2) + "┐", curses.color_pair(8))
        for y in range(start_y + 1, min(start_y + box_h - 1, h - 1)):
            self.safe_addstr(y, start_x, "│", curses.color_pair(8))
            self.safe_addstr(y, start_x + box_w - 1, "│", curses.color_pair(8))
        if start_y + box_h - 1 < h:
            self.safe_addstr(start_y + box_h - 1, start_x, "└" + "─" * (box_w - 2) + "┘", curses.color_pair(8))

        # Title
        title_str = f" {title} "
        title_x = start_x + (box_w - len(title_str)) // 2
        self.safe_addstr(start_y, title_x, title_str, curses.color_pair(12) | curses.A_BOLD)

        # Fields
        inner_w = box_w - 4
        draw_y = start_y + 2
        for i, key in enumerate(field_order):
            if draw_y + 1 >= start_y + box_h - 1:
                break
            label = key.replace("_", " ").title() + ":"
            value = fields.get(key, "")
            is_active = (i == cursor_pos)

            # Label
            label_attr = curses.color_pair(8) | curses.A_BOLD if is_active else curses.color_pair(8)
            self.safe_addstr(draw_y, start_x + 2, label[:inner_w], label_attr)
            draw_y += 1

            # Value field
            if is_active:
                field_attr = curses.color_pair(2)
                # Show cursor
                display = value + "█"
            else:
                field_attr = curses.color_pair(8) | curses.A_DIM
                display = value if value else "(empty)"

            display = display[:inner_w]
            self.safe_addstr(draw_y, start_x + 2, display.ljust(inner_w), field_attr)
            draw_y += 1

        # Footer
        if draw_y < start_y + box_h - 1:
            footer = "[Tab] Next  [Esc] Cancel  [Enter on last] Save"
            footer_x = start_x + (box_w - len(footer)) // 2
            self.safe_addstr(start_y + box_h - 2, footer_x, footer, curses.color_pair(8) | curses.A_DIM)

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
            "    ↑ / k         Move up",
            "    ↓ / j         Move down",
            "    Home / g       Jump to first theme",
            "    End / G        Jump to last theme",
            "",
            "  Actions:",
            "    Enter          Apply selected theme",
            "    i              Install selected theme (curl | bash)",
            "    a              Add a custom theme",
            "    e              Edit selected custom theme",
            "    d              Delete selected custom theme",
            "",
            "  Backup / Restore:",
            "    b              Backup current theme settings",
            "    r              Restore theme from backup",
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
                elif line.strip().startswith("●") or line.strip().startswith("◌") or line.strip().startswith("○"):
                    attr = curses.color_pair(8)
                else:
                    attr = curses.color_pair(8)
                self.safe_addstr(start_y + 1 + i, start_x + 1, line[:box_w - 3], attr)

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

        self.stdscr.refresh()

    def start_add_custom(self):
        """Initialize the add custom theme form."""
        self.mode = "add_custom"
        self.form_fields = {
            "name": "",
            "category": "Custom",
            "gtk_theme": "",
            "shell_theme": "",
            "icon_theme": "",
            "cursor_theme": "",
            "color_scheme": "prefer-dark",
            "description": "",
            "install_url": "",
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
        self.form_fields = {
            "name": theme.get("name", ""),
            "category": theme.get("category", "Custom"),
            "gtk_theme": theme.get("gtk_theme", ""),
            "shell_theme": theme.get("shell_theme", ""),
            "icon_theme": theme.get("icon_theme", ""),
            "cursor_theme": theme.get("cursor_theme", ""),
            "color_scheme": theme.get("color_scheme", "prefer-dark"),
            "description": theme.get("description", ""),
            "install_url": theme.get("install_url", ""),
        }
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
            # Find the custom theme index
            builtin_count = len(BUILTIN_THEMES)
            custom_index = self.selected - builtin_count
            if 0 <= custom_index < len(custom_themes):
                custom_themes[custom_index] = new_theme
        else:
            custom_themes.append(new_theme)

        save_custom_themes(custom_themes)
        self.refresh_themes()
        self.mode = "browse"
        self.set_status(f"Theme '{name}' saved successfully!", "success")
        return True

    def handle_form_input(self, key):
        """Handle input in form mode."""
        if key == 27:  # Escape
            self.mode = "browse"
            self.set_status("Cancelled.", "info")
            return

        current_field = self.form_field_order[self.form_cursor]

        if key == 9:  # Tab — next field
            self.form_cursor = (self.form_cursor + 1) % len(self.form_field_order)
        elif key == curses.KEY_BTAB or key == 353:  # Shift+Tab — prev field
            self.form_cursor = (self.form_cursor - 1) % len(self.form_field_order)
        elif key == 10 or key == curses.KEY_ENTER:  # Enter
            if self.form_cursor == len(self.form_field_order) - 1:
                self.save_form()
            else:
                self.form_cursor = (self.form_cursor + 1) % len(self.form_field_order)
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            val = self.form_fields.get(current_field, "")
            self.form_fields[current_field] = val[:-1]
        elif 32 <= key <= 126:  # Printable characters
            val = self.form_fields.get(current_field, "")
            self.form_fields[current_field] = val + chr(key)

    def handle_confirm_input(self, key):
        """Handle input in confirm mode."""
        if key in (ord('y'), ord('Y')):
            if self.confirm_callback:
                self.confirm_callback()
            self.mode = "browse"
        elif key in (ord('n'), ord('N'), 27):  # n, N, or Escape
            self.mode = "browse"
            self.set_status("Cancelled.", "info")

    def run(self):
        """Main event loop."""
        self.set_status("Welcome! Use ↑/↓ to browse themes, Enter to apply, [?] for help.", "info")

        while True:
            self.draw()
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == curses.KEY_RESIZE:
                continue

            # Mode-specific input handling
            if self.mode == "help":
                self.mode = "browse"
                continue

            if self.mode == "confirm":
                self.handle_confirm_input(key)
                continue

            if self.mode in ("add_custom", "edit_custom"):
                self.handle_form_input(key)
                continue

            # Browse mode
            if key in (ord('q'), ord('Q')):
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

            elif key in (10, curses.KEY_ENTER):  # Enter — apply theme
                if not self.themes:
                    continue
                theme = self.themes[self.selected]
                if not check_theme_installed(theme):
                    self.set_status(f"Theme '{theme['name']}' is not installed. Press [i] to install first.", "warning")
                    continue

                def do_apply():
                    backup_current_theme()
                    if apply_theme(theme):
                        self.active_index = self.selected
                        self.set_status(f"Applied '{theme['name']}' successfully! (Previous theme backed up)", "success")
                    else:
                        self.set_status(f"Failed to apply '{theme['name']}'. Some gsettings may not be available.", "error")

                self.confirm_action = f"Apply theme '{theme['name']}'? This will change your GTK, Shell, Icons, and Cursors."
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

                def do_install():
                    self.set_status(f"Installing '{theme['name']}'... This will open a new terminal.", "info")
                    self.draw()
                    try:
                        # Run in a visible terminal so user can see progress and enter sudo password
                        cmd = f"curl -fsSL '{url}' | bash"
                        # Try various terminal emulators
                        terminals = [
                            ["gnome-terminal", "--", "bash", "-c", f"{cmd}; echo ''; echo 'Press Enter to close...'; read"],
                            ["xfce4-terminal", "-e", f"bash -c \"{cmd}; echo ''; echo 'Press Enter to close...'; read\""],
                            ["xterm", "-e", f"bash -c \"{cmd}; echo ''; echo 'Press Enter to close...'; read\""],
                        ]
                        launched = False
                        for term_cmd in terminals:
                            if shutil.which(term_cmd[0]):
                                subprocess.Popen(term_cmd)
                                launched = True
                                break

                        if not launched:
                            # Fallback: run in background and notify
                            subprocess.Popen(["bash", "-c", cmd])

                        self.set_status(f"Install script launched for '{theme['name']}' in a new terminal window.", "success")
                    except Exception as e:
                        self.set_status(f"Failed to launch installer: {e}", "error")

                self.confirm_action = f"Install '{theme['name']}'? This will download and run the install script in a new terminal window."
                self.confirm_callback = do_install
                self.mode = "confirm"

            elif key in (ord('a'), ord('A')):  # Add custom
                self.start_add_custom()

            elif key in (ord('e'), ord('E')):  # Edit custom
                self.start_edit_custom()

            elif key in (ord('d'), ord('D')):  # Delete custom
                if not self.themes:
                    continue
                theme = self.themes[self.selected]
                if theme.get("builtin", False):
                    self.set_status("Cannot delete built-in themes.", "warning")
                    continue

                def do_delete():
                    custom_themes = load_custom_themes()
                    builtin_count = len(BUILTIN_THEMES)
                    custom_index = self.selected - builtin_count
                    if 0 <= custom_index < len(custom_themes):
                        removed = custom_themes.pop(custom_index)
                        save_custom_themes(custom_themes)
                        self.refresh_themes()
                        self.set_status(f"Deleted custom theme '{removed['name']}'.", "success")

                self.confirm_action = f"Delete custom theme '{theme['name']}'? This cannot be undone."
                self.confirm_callback = do_delete
                self.mode = "confirm"

            elif key in (ord('b'), ord('B')):  # Backup
                backup = backup_current_theme()
                self.set_status(f"Current theme backed up at {backup.get('timestamp', 'now')}.", "success")

            elif key in (ord('r'), ord('R')):  # Restore
                backup = load_backup()
                if not backup:
                    self.set_status("No backup found. Press [b] to create one first.", "warning")
                    continue

                def do_restore():
                    if restore_backup():
                        self.refresh_themes()
                        self.set_status(f"Restored theme from backup ({backup.get('timestamp', 'unknown')}).", "success")
                    else:
                        self.set_status("Failed to restore backup.", "error")

                ts = backup.get("timestamp", "unknown")
                self.confirm_action = f"Restore theme from backup ({ts})? GTK: {backup.get('gtk_theme', '?')}"
                self.confirm_callback = do_restore
                self.mode = "confirm"


def main(stdscr):
    """Entry point for curses wrapper."""
    app = ThemeSwitcherTUI(stdscr)
    app.run()


if __name__ == "__main__":
    # Check if running in a terminal
    if not sys.stdout.isatty():
        print("Error: This application must be run in a terminal.")
        sys.exit(1)

    # Ensure config directory exists
    ensure_config_dir()

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you are running this in a terminal with curses support.")
        sys.exit(1)
