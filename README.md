# GNOME Theme Switcher

> A terminal-based theme manager for switching between system-wide GNOME themes.

**GNOME Theme Switcher** is a lightweight TUI (Terminal User Interface) application built with Python's `curses` library. It has **zero external dependencies** — just Python 3 and a terminal. It ships with 9 pre-configured themes from the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) collection and supports adding your own custom themes.

---

### Legal Notice & Disclaimer

**This software is provided "as is", without warranty of any kind, express or implied. Use at your own risk.**

This application modifies system configuration files and desktop settings via `gsettings`. The author and contributors of this project are not responsible for any damage to your system, loss of data, or any other issues that may arise from its use. It is your responsibility to back up your data and understand the risks involved.

This project is an independent, unofficial tool. It is **not affiliated with, endorsed by, or connected to** any of the upstream theme authors (such as vinceliuice, Catppuccin, etc.), GNOME, or any Linux distribution. All theme names, icons, and related materials are the intellectual property of their respective owners.

This project was created with the assistance of AI. For full details, see the [LICENSE](LICENSE) file.

---

## Features

| Feature | Description |
|---|---|
| **Browse Themes** | Navigate 9 built-in themes organized by category (macOS, Windows, Linux-Native) |
| **Apply Instantly** | Switch your entire desktop (GTK, Shell, Icons, Cursors) with a single Enter keypress |
| **Install Themes** | Download and install themes directly from the TUI via `curl` one-liners |
| **Custom Themes** | Add, edit, and delete your own custom theme configurations |
| **Backup / Restore** | Automatically backs up your current theme before switching; restore anytime |
| **Active Detection** | Shows which theme is currently active and which are installed |
| **Zero Dependencies** | Uses only Python 3 standard library (`curses`, `json`, `subprocess`) |

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GNOME Theme Switcher v1.1.0                           Press [?] for help  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                │                                            │
│  Themes                        │ Details                                    │
│  ──────                        │ ──────                                     │
│  ── macOS ──                   │ WhiteSur macOS                             │
│  > ● WhiteSur macOS            │  ACTIVE   INSTALLED                        │
│    ◌ Colloid Material          │                                            │
│  ── Windows ──                 │ Category:      macOS                       │
│    ○ Fluent Win11              │ GTK Theme:     WhiteSur-Dark-purple        │
│    ○ Win11                     │ Shell Theme:   WhiteSur-Dark-purple        │
│    ○ We10X Win10               │ Icon Theme:    WhiteSur-dark               │
│  ── Linux-Native ──            │ Cursor Theme:  WhiteSur-cursors            │
│    ◌ Orchis Material           │ Color Scheme:  prefer-dark                 │
│    ◌ Graphite Minimal          │                                            │
│    ◌ Lavanda Purple            │ Description:                               │
│    ◌ Catppuccin Mocha          │ macOS Big Sur / Monterey look with dark    │
│                                │ mode and purple accent. Includes GDM,      │
│                                │ wallpapers, and Firefox theme.             │
│                                │                                            │
│ [Enter] Apply  [i] Install  [a] Add Custom  [e] Edit  [d] Delete  [r] Restore │
│  Welcome! Use arrow keys to browse, [Enter] to apply. Press [?] for help.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/main/install.sh | bash
```

This downloads the application to `~/.local/bin/gnome-theme-switcher` and adds it to your PATH.

## Usage

After installation, simply run:

```bash
gnome-theme-switcher
```

### Keyboard Shortcuts

| Key | Action |
|---|---|
| `↑` / `k` | Move selection up |
| `↓` / `j` | Move selection down |
| `Enter` | Apply the selected theme |
| `i` | Install the selected theme (runs install script) |
| `a` | Add a new custom theme |
| `e` | Edit the selected custom theme |
| `d` | Delete the selected custom theme |
| `r` | Restore the last theme settings |
| `?` | Show help screen |
| `q` | Quit |

## Upstream Themes & Credits

This tool includes pre-configured settings for themes created by the open-source community. **All credit for the themes themselves goes to their original authors.** Please support their work.

| Theme | Original Author(s) | License |
|---|---|---|
| WhiteSur, Colloid, Fluent, Orchis, Graphite, Lavanda, Tela Icons | [vinceliuice](https://github.com/vinceliuice) | GPL-3.0 |
| We10X, Win11 | [yeyushengfan258](https://github.com/yeyushengfan258) | GPL-3.0 |
| Catppuccin | [Catppuccin](https://github.com/catppuccin) & [Fausto-Korpsvart](https://github.com/Fausto-Korpsvart) | MIT |

The install scripts for these themes are maintained in the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository.

## Compatibility

- **OS:** Ubuntu 22.04+, ZorinOS 18+, and other modern GNOME-based distros.
- **Desktop:** GNOME 42+
- **Python:** 3.8+

## License

This application is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full text.
