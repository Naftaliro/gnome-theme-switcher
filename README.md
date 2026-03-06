# GNOME Theme Switcher

> A terminal-based theme manager for switching between system-wide GNOME themes with a single keypress.

**GNOME Theme Switcher** is a lightweight TUI (Terminal User Interface) application built with Python's `curses` library. It has **zero external dependencies** — just Python 3 and a terminal. It ships with 9 pre-configured themes from the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) collection and supports adding your own custom themes.

> **Disclaimer:** This application was created with the assistance of AI. It modifies GNOME desktop settings via `gsettings`. The maintainer takes no responsibility for any changes made to your system. **Use at your own risk.**

## Features

The application provides a complete theme management experience from the terminal:

| Feature | Description |
|---|---|
| **Browse Themes** | Navigate 9 built-in themes organized by category (macOS, Windows, Linux-Native) |
| **Apply Instantly** | Switch your entire desktop (GTK, Shell, Icons, Cursors) with a single Enter keypress |
| **Install Themes** | Download and install themes directly from the TUI via `curl` one-liners |
| **Custom Themes** | Add, edit, and delete your own custom theme configurations |
| **Backup / Restore** | Automatically backs up your current theme before switching; restore anytime |
| **Active Detection** | Shows which theme is currently active and which are installed |
| **Libadwaita Aware** | Themes are configured to work with GTK4 / libadwaita applications |
| **Zero Dependencies** | Uses only Python 3 standard library (`curses`, `json`, `subprocess`) |

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GNOME Theme Switcher v1.0.0                           Press [?] for help  │
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
│ [Enter] Apply  [i] Install  [a] Add Custom  [e] Edit  [d] Delete  [b/r]   │
│  Welcome! Use ↑/↓ to browse themes, Enter to apply, [?] for help.         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Installation

### Method 1: One-Liner Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/main/install.sh | bash
```

This downloads the application to `~/.local/bin/gnome-theme-switcher` and adds it to your PATH.

### Method 2: Clone and Install

```bash
git clone https://github.com/Naftaliro/gnome-theme-switcher.git
cd gnome-theme-switcher
chmod +x install.sh
./install.sh
```

### Method 3: Run Directly (No Install)

```bash
git clone https://github.com/Naftaliro/gnome-theme-switcher.git
cd gnome-theme-switcher
python3 gnome-theme-switcher.py
```

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
| `Home` / `g` | Jump to first theme |
| `End` / `G` | Jump to last theme |
| `Enter` | Apply the selected theme |
| `i` | Install the selected theme (opens terminal with install script) |
| `a` | Add a new custom theme |
| `e` | Edit the selected custom theme |
| `d` | Delete the selected custom theme |
| `b` | Backup current theme settings |
| `r` | Restore theme from backup |
| `?` | Show help screen |
| `q` | Quit |

### Theme Status Icons

| Icon | Meaning |
|---|---|
| `●` | Currently active theme |
| `◌` | Installed but not active |
| `○` | Not installed |

## Built-in Themes

The application ships with 9 pre-configured themes, all set to dark mode with purple accent:

| Theme | Category | Style | GTK Theme Name |
|---|---|---|---|
| **WhiteSur macOS** | macOS | macOS Big Sur / Monterey | `WhiteSur-Dark-purple` |
| **Colloid Material** | macOS | Material Design | `Colloid-Purple-Dark` |
| **Fluent Win11** | Windows | Windows 11 Fluent Design | `Fluent-purple-Dark` |
| **Win11** | Windows | Windows 11 | `Win11-purple-Dark` |
| **We10X Win10** | Windows | Windows 10 | `We10X-purple-Dark` |
| **Orchis Material** | Linux-Native | Material Design | `Orchis-purple-Dark` |
| **Graphite Minimal** | Linux-Native | Minimalist Dark | `Graphite-purple-Dark` |
| **Lavanda Purple** | Linux-Native | Purple-native Elegance | `Lavanda-Dark` |
| **Catppuccin Mocha** | Linux-Native | Soothing Pastel Dark | `Catppuccin-purple-Dark-Macchiato` |

These themes can be installed directly from the TUI by pressing `i` on any theme, which will download and run the corresponding install script from the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository.

## Adding Custom Themes

You can add any GNOME theme as a custom entry. Press `a` in the TUI to open the add form:

1. **Name** — A display name for the theme (e.g., "My Dracula Theme")
2. **Category** — A category label (e.g., "Custom", "Dark", etc.)
3. **GTK Theme** — The exact GTK theme name as it appears in `~/.themes/` or `/usr/share/themes/`
4. **Shell Theme** — The GNOME Shell theme name (usually the same as GTK)
5. **Icon Theme** — The icon theme name from `~/.local/share/icons/` or `/usr/share/icons/`
6. **Cursor Theme** — The cursor theme name
7. **Color Scheme** — Either `prefer-dark`, `prefer-light`, or `default`
8. **Description** — A short description of the theme
9. **Install URL** — (Optional) A URL to a `curl`-able install script

Custom themes are saved to `~/.config/gnome-theme-switcher/custom_themes.json` and persist across sessions.

## How It Works

When you apply a theme, the switcher runs the following `gsettings` commands:

```bash
gsettings set org.gnome.desktop.interface gtk-theme "<GTK_THEME>"
gsettings set org.gnome.desktop.wm.preferences theme "<GTK_THEME>"
gsettings set org.gnome.shell.extensions.user-theme name "<SHELL_THEME>"
gsettings set org.gnome.desktop.interface icon-theme "<ICON_THEME>"
gsettings set org.gnome.desktop.interface cursor-theme "<CURSOR_THEME>"
gsettings set org.gnome.desktop.interface color-scheme "<COLOR_SCHEME>"
```

Before applying, it automatically backs up your current settings to `~/.config/gnome-theme-switcher/backup.json`.

## File Locations

| File | Purpose |
|---|---|
| `~/.local/bin/gnome-theme-switcher` | The application binary |
| `~/.config/gnome-theme-switcher/custom_themes.json` | Your custom theme definitions |
| `~/.config/gnome-theme-switcher/backup.json` | Backup of your previous theme settings |

## Uninstalling

```bash
gnome-theme-switcher-uninstall
```

This removes the application binary. Your config files at `~/.config/gnome-theme-switcher/` are preserved. To remove those too:

```bash
rm -rf ~/.config/gnome-theme-switcher
```

## Compatibility

| Field | Value |
|---|---|
| **Target OS** | ZorinOS 18 Pro, Ubuntu 24.04+, Linux Mint 22+, Pop!_OS 24.04+ |
| **Desktop** | GNOME (42+) |
| **Python** | 3.8+ (uses only standard library) |
| **Terminal** | Any terminal with curses support (GNOME Terminal, Kitty, Alacritty, etc.) |
| **Dependencies** | None (Python 3 standard library only) |

## Related

This application is designed to work with the theme collection at [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes), which contains the full install scripts and documentation for all 9 built-in themes.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

Built with the assistance of AI. Theme install scripts and theme collections are maintained in the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository. All themes are created by their respective open-source authors (vinceliuice, yeyushengfan258, Fausto-Korpsvart, Catppuccin).
