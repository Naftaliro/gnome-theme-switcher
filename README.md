# gnome theme switcher

a terminal app for switching gnome themes. it's one python file using `curses`, so all you need is python 3. it comes with the 9 themes from [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) and you can add your own.

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

## what it does

- browse the themes by category (macos, windows, linux)
- enter applies gtk, shell, icons and cursors all at once
- installs themes too. it drops out to your real terminal for that so you can see what's happening and type your sudo password, then comes back
- add, edit and delete your own themes
- backs up your current theme before switching, restore it any time
- shows which theme is active and which ones are installed
- ascii previews (`p`)
- the theme list comes from the themes repo and gets cached, so new themes show up on their own (`S` in the update dialog to sync)
- checks for updates when it starts and can update itself
- error codes when stuff breaks (table at the bottom)

## install

download it, check it against [SHA256SUMS.txt](SHA256SUMS.txt), read it, run it:

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0/install.sh -o gts-install.sh
sha256sum gts-install.sh
less gts-install.sh
chmod +x gts-install.sh && ./gts-install.sh
```

or in one line if you trust it:

```bash
curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0/install.sh | bash
```

it goes in `~/.local/bin/gnome-theme-switcher` and gets added to your PATH. then just run `gnome-theme-switcher`.

## keys

| key | does |
|---|---|
| `↑` / `k` | up |
| `↓` / `j` | down |
| `Enter` | apply the theme |
| `i` | install the theme |
| `a` | add a custom theme |
| `e` | edit a custom theme |
| `d` | delete a custom theme |
| `b` | back up your current theme |
| `r` | restore the backup |
| `u` | check for updates |
| `?` | help |
| `q` | quit |

## uninstall

```bash
gnome-theme-switcher-uninstall
rm -rf ~/.config/gnome-theme-switcher/   # if you want the settings gone too
```

## works on

ubuntu 22.04+, zorin os 18+ and other gnome distros. gnome 42+, python 3.8+.

## credits

the themes belong to the people who made them:

| theme | by | license |
|---|---|---|
| WhiteSur, Colloid, Fluent, Orchis, Graphite, Lavanda, Tela icons | [vinceliuice](https://github.com/vinceliuice) | GPL-3.0 |
| We10X, Win11 | [yeyushengfan258](https://github.com/yeyushengfan258) | GPL-3.0 |
| Catppuccin | [catppuccin](https://github.com/catppuccin) and [Fausto-Korpsvart](https://github.com/Fausto-Korpsvart) | MIT / GPL-3.0 |

## error codes

| code | meaning |
|---|---|
| `GTS-E000` | fine, no error |
| `GTS-E001` | something unexpected |
| `GTS-E002` | not running in a terminal |
| `GTS-E003` | curses wouldn't start |
| `GTS-E004` | can't make or read the config folder |
| `GTS-E005` | `gsettings` not found (is gnome installed?) |
| `GTS-E010` | no internet |
| `GTS-E011` | download failed |
| `GTS-E012` | the install script failed |
| `GTS-E013` | installing dependencies failed (apt/dnf) |
| `GTS-E014` | permission denied (sudo password?) |
| `GTS-E015` | install took longer than 10 minutes |
| `GTS-E020` | self update failed |
| `GTS-E030` | backup failed |
| `GTS-E031` | restore failed |

the install log is at `~/.config/gnome-theme-switcher/last_install.log`.

## license

MIT, see [LICENSE](LICENSE). no warranty, it changes your desktop settings, use at your own risk. not affiliated with gnome, zorin group, canonical, apple, microsoft or any of the theme authors, the names are just there to say what it works with and what things look like.
