# GNOME Theme Switcher

> A terminal-based theme manager for switching between system-wide GNOME themes.

**GNOME Theme Switcher** is a lightweight TUI (Terminal User Interface) application built with Python's `curses` library. It has **zero external dependencies** — just Python 3 and a terminal. It ships with 9 pre-configured themes from the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) collection and supports adding your own custom themes.

---

### Legal Notice and Disclaimer

**This software is provided "as is", without warranty of any kind, express or implied. Use at your own risk.**

This application modifies system configuration files and desktop settings via `gsettings`. The author and contributors of this project are not responsible for any damage to your system, loss of data, or any other issues that may arise from its use. It is your responsibility to back up your data and understand the risks involved.

This project is an independent, unofficial tool. It is **not affiliated with, endorsed by, or connected to** any of the upstream theme authors (such as vinceliuice, Catppuccin, yeyushengfan258, etc.), GNOME, or any Linux distribution.

This project was created with the significant assistance of AI. For full details, see the [LICENSE](LICENSE) file.

---

### Trademarks

"GNOME" is a trademark of The GNOME Foundation. "ZorinOS" is a trademark of Zorin Group. "macOS" and "Apple" are trademarks of Apple Inc. "Windows" and "Microsoft" are trademarks of Microsoft Corporation. "Ubuntu" is a trademark of Canonical Ltd. All other product names, logos, and brands are the property of their respective owners. These names are used in this project solely to describe compatibility and visual inspiration, and their use does not imply any affiliation or endorsement.

---

## Features

| Feature | Description |
|---|---|
| **Browse Themes** | Navigate 9 built-in themes organized by category (macOS, Windows, Linux-Native) |
| **Apply Instantly** | Switch your entire desktop (GTK, Shell, Icons, Cursors) with a single Enter keypress |
| **Install Themes** | Download and install themes directly from the TUI via install scripts |
| **Custom Themes** | Add, edit, and delete your own custom theme configurations |
| **Backup / Restore** | Automatically backs up your current theme before switching; restore anytime |
| **Active Detection** | Shows which theme is currently active and which are installed |
| **Auto-Update** | Checks GitHub for new versions on startup and offers one-click self-update |
| **Interactive Install** | Theme installation suspends the TUI and runs in your real terminal — you can see all output and enter your sudo password naturally. TUI resumes automatically when done. |
| **Zero Dependencies** | Uses only Python 3 standard library (`curses`, `json`, `subprocess`, `urllib`) |
| **Theme Previews** | ASCII art previews for each theme displayed in the detail panel — toggle with [p] |
| **Remote Theme List** | Theme definitions are fetched from the themes repo and cached locally — new themes appear automatically when the repo is updated. Press [S] in the update dialog to sync. |
| **Error Codes** | All errors include a machine-readable code (GTS-E0xx) with a human-readable message for easy troubleshooting |

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GNOME Theme Switcher v1.5.0                           Press [?] for help  │
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

### Recommended: Download, Inspect, Then Run

```bash
# Step 1: Download the installer
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0/install.sh -o gts-install.sh

# Step 2: Verify the checksum (compare against SHA256SUMS.txt in this repo)
sha256sum gts-install.sh

# Step 3: Review the script
less gts-install.sh

# Step 4: Run it
chmod +x gts-install.sh && ./gts-install.sh
```

SHA-256 checksums for all files are published in the **[SHA256SUMS.txt](SHA256SUMS.txt)** file and in each GitHub Release.

### Quick Install (One-Liner)

For convenience, the installer can also be run directly. **By using this method, you are trusting the code at the current HEAD of this repository.**

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0/install.sh | bash
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
| `Up` / `k` | Move selection up |
| `Down` / `j` | Move selection down |
| `Enter` | Apply the selected theme |
| `i` | Install the selected theme (runs install script) |
| `a` | Add a new custom theme |
| `e` | Edit the selected custom theme |
| `d` | Delete the selected custom theme |
| `b` | Backup current theme settings |
| `r` | Restore the last theme settings |
| `u` | Check for updates |
| `?` | Show help screen |
| `q` | Quit |

## Uninstall

```bash
gnome-theme-switcher-uninstall
```

To also remove configuration files:

```bash
rm -rf ~/.config/gnome-theme-switcher/
```

## Upstream Themes and Credits

This tool includes pre-configured settings for themes created by the open-source community. **All credit for the themes themselves goes to their original authors.** Please support their work.

| Theme | Original Author(s) | License |
|---|---|---|
| WhiteSur, Colloid, Fluent, Orchis, Graphite, Lavanda, Tela Icons | [vinceliuice](https://github.com/vinceliuice) | GPL-3.0 |
| We10X, Win11 | [yeyushengfan258](https://github.com/yeyushengfan258) | GPL-3.0 |
| Catppuccin | [Catppuccin](https://github.com/catppuccin) and [Fausto-Korpsvart](https://github.com/Fausto-Korpsvart) | MIT / GPL-3.0 |

The install scripts for these themes are maintained in the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository.

## Compatibility

| Field | Value |
|---|---|
| **OS** | Ubuntu 22.04+, ZorinOS 18+, and other modern GNOME-based distros |
| **Desktop** | GNOME 42+ |
| **Python** | 3.8+ |

## License

This application is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full text.

## Error Codes

When something goes wrong, the application displays a structured error code for easy troubleshooting.

| Code | Meaning |
|---|---|
| `GTS-E000` | Success (no error) |
| `GTS-E001` | General / unexpected error |
| `GTS-E002` | Not running in a terminal (TTY required) |
| `GTS-E003` | Failed to initialize curses TUI |
| `GTS-E004` | Cannot create or access config directory |
| `GTS-E005` | `gsettings` not found (GNOME not installed?) |
| `GTS-E010` | Network error (no internet connection) |
| `GTS-E011` | Download failed (bad URL or HTTP error) |
| `GTS-E012` | Install script exited with an error |
| `GTS-E013` | Dependency installation failed (apt/dnf) |
| `GTS-E014` | Permission denied (sudo password issue) |
| `GTS-E015` | Installation timed out (10 minute limit) |
| `GTS-E020` | Self-update failed |
| `GTS-E030` | Backup failed |
| `GTS-E031` | Restore from backup failed |

If you encounter an error, check the log file at `~/.config/gnome-theme-switcher/last_install.log` for details.
