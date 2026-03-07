#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Naftali <https://github.com/Naftaliro>
#
# GNOME Theme Switcher — Installer
#
# This script is provided "as is", without warranty of any kind. Use at your own risk.
# For full details, see the LICENSE file in the repository.
#
# Copyright (c) 2026 Naftali
# Installs the TUI application to ~/.local/bin/ so it can be run from anywhere.
#
# Usage:
#   chmod +x install.sh && ./install.sh
#   # or
#   curl -fsSL https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0/install.sh | bash
#

set -euo pipefail

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }

INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/gnome-theme-switcher"
APP_NAME="gnome-theme-switcher"
REPO_RAW="https://raw.githubusercontent.com/Naftaliro/gnome-theme-switcher/v1.5.0"

echo -e "${BOLD}"
cat << 'EOF'
   ╔══════════════════════════════════════════════════════════╗
   ║          GNOME Theme Switcher — Installer               ║
   ╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# ── Step 1: Ensure Python 3 is available ──────────────────────────────────────
info "Checking for Python 3..."
if ! command -v python3 &>/dev/null; then
    warn "Python 3 not found. Installing..."
    sudo apt update -y && sudo apt install -y python3
fi
PYTHON_VERSION=$(python3 --version 2>&1)
ok "Found ${PYTHON_VERSION}"

# ── Step 2: Create install directory ──────────────────────────────────────────
info "Creating install directory: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
mkdir -p "${CONFIG_DIR}"
ok "Directories created."

# ── Step 3: Download or copy the application ──────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_APP="${SCRIPT_DIR}/gnome-theme-switcher.py"

if [[ -f "${LOCAL_APP}" ]]; then
    info "Installing from local file..."
    cp "${LOCAL_APP}" "${INSTALL_DIR}/${APP_NAME}"
else
    info "Downloading from GitHub..."
    curl -fsSL "${REPO_RAW}/gnome-theme-switcher.py" -o "${INSTALL_DIR}/${APP_NAME}"
fi
chmod +x "${INSTALL_DIR}/${APP_NAME}"
ok "Application installed to ${INSTALL_DIR}/${APP_NAME}"

# ── Step 4: Ensure ~/.local/bin is in PATH ────────────────────────────────────
if [[ ":${PATH}:" != *":${INSTALL_DIR}:"* ]]; then
    warn "${INSTALL_DIR} is not in your PATH."
    info "Adding it to your shell profile..."

    SHELL_NAME=$(basename "${SHELL}")
    case "${SHELL_NAME}" in
        bash)
            PROFILE="${HOME}/.bashrc"
            ;;
        zsh)
            PROFILE="${HOME}/.zshrc"
            ;;
        fish)
            PROFILE="${HOME}/.config/fish/config.fish"
            ;;
        *)
            PROFILE="${HOME}/.profile"
            ;;
    esac

    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "${PROFILE}" 2>/dev/null; then
        echo '' >> "${PROFILE}"
        echo '# Added by GNOME Theme Switcher installer' >> "${PROFILE}"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${PROFILE}"
        ok "Added to ${PROFILE}. Run 'source ${PROFILE}' or open a new terminal."
    else
        ok "PATH entry already exists in ${PROFILE}."
    fi
fi

# ── Step 5: Create uninstall script ──────────────────────────────────────────
UNINSTALL="${INSTALL_DIR}/${APP_NAME}-uninstall"
cat > "${UNINSTALL}" << UNINSTALL_EOF
#!/usr/bin/env bash
echo "Removing GNOME Theme Switcher..."
rm -f "${INSTALL_DIR}/${APP_NAME}"
rm -f "${INSTALL_DIR}/${APP_NAME}-uninstall"
echo "Application removed. Config files kept at ${CONFIG_DIR}/"
echo "To remove config too: rm -rf ${CONFIG_DIR}"
UNINSTALL_EOF
chmod +x "${UNINSTALL}"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}"
cat << 'EOF'
   ╔══════════════════════════════════════════════════════════╗
   ║          Installation Complete!                         ║
   ╠══════════════════════════════════════════════════════════╣
   ║                                                          ║
   ║  Run the theme switcher:                                ║
   ║    $ gnome-theme-switcher                               ║
   ║                                                          ║
   ║  Uninstall:                                             ║
   ║    $ gnome-theme-switcher-uninstall                     ║
   ║                                                          ║
   ║  Config location:                                       ║
   ║    ~/.config/gnome-theme-switcher/                      ║
   ║                                                          ║
   ╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
