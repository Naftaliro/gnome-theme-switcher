# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the GNOME Theme Switcher application or its installer, **please do NOT open a public GitHub issue.** Instead, report it privately using one of the following methods:

1. **GitHub Security Advisory (preferred):** Navigate to the [Security tab](https://github.com/Naftaliro/gnome-theme-switcher/security/advisories) of this repository and click "Report a vulnerability."
2. **Private contact:** Open a [private vulnerability report](https://github.com/Naftaliro/gnome-theme-switcher/security/advisories/new) directly.

## Scope

This policy covers the GNOME Theme Switcher TUI application (`gnome-theme-switcher.py`) and its installer (`install.sh`). Vulnerabilities in the **upstream theme projects** or the companion [zorinos-gnome-themes](https://github.com/Naftaliro/zorinos-gnome-themes) repository should be reported to those respective projects.

## What Qualifies

The following are examples of issues that should be reported as security vulnerabilities:

- The application executes arbitrary code beyond its documented purpose
- The application transmits data to an unexpected remote endpoint
- The installer modifies system files outside its documented scope
- Hardcoded credentials or secrets accidentally committed to the repository
- A supply-chain risk introduced by an unpinned dependency or URL

## Response

I will acknowledge receipt of your report within **72 hours** and aim to provide a fix or mitigation within **7 days** for confirmed vulnerabilities.

## Supported Versions

| Version | Supported |
|---|---|
| Latest release | Yes |
| Older releases | Best effort |
