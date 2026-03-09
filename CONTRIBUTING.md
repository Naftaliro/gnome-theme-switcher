# Contributing

Thank you for your interest in contributing to the GNOME Theme Switcher! Whether you want to add features, fix bugs, or improve documentation, contributions are welcome.

## How to Contribute

### Bug Fixes and Features

1. **Fork** this repository and create a new branch.
2. Make your changes to `gnome-theme-switcher.py` or `install.sh`.
3. Ensure your code passes:
   - `python3 -m py_compile gnome-theme-switcher.py`
   - `bash -n install.sh`
   - [ShellCheck](https://www.shellcheck.net/) for `install.sh`
4. Open a **Pull Request** with a clear description of the change.

### Adding Built-in Theme Presets

If you want to add a new built-in theme to the switcher:

1. Add a new entry to the `FALLBACK_THEMES` list in `gnome-theme-switcher.py`, or add the theme to `themes.json` in the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository (preferred).
2. Follow the existing dictionary structure with all required keys:
   - `name`, `category`, `gtk_theme`, `shell_theme`, `icon_theme`, `cursor_theme`, `color_scheme`, `install_script`, `description`
3. Ensure the corresponding install script exists in the [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository.
4. Update `THIRD_PARTY_NOTICES.md` if the theme introduces new upstream dependencies.

### Code Style

- Python: Follow PEP 8 conventions. Use type hints where practical.
- Bash: Use `set -euo pipefail`, quote all variables, and use `[[ ]]` for conditionals.
- Both: Include SPDX headers in new files.

## Reporting Bugs

Open a [GitHub Issue](https://github.com/Naftaliro/gnome-theme-switcher/issues) with:

- Your OS and GNOME version
- Python version (`python3 --version`)
- Terminal emulator used
- The error output or unexpected behavior
- Steps to reproduce

## Code of Conduct

Be respectful and constructive. This is a hobby project maintained in spare time. Patience is appreciated.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
