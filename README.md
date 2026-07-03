# MediaPlayer UI for Endstone

[![CI](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml/badge.svg)](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[English](README.md) | [简体中文](README_ZH.md)

A Python [Endstone](https://github.com/EndstoneMC/endstone) plugin that provides a form-based GUI for the [MediaPlayer](https://github.com/ReallocAll/endstone-mediaplayer) C plugin.

Players type `/mpg` in-game to open an interactive menu for browsing songs, controlling playback, and managing their playlist — no need to memorize command syntax.

## Requirements

- [endstone_mediaplayer](https://github.com/ReallocAll/endstone-mediaplayer) C plugin installed and enabled
- Endstone API >= 0.11

## Installation

1. Build or download `endstone_mediaplayer_ui-*.whl`
2. Copy it into your server's `plugins/` directory
3. Restart the server

Endstone auto-discovers `.whl` files in `plugins/` and installs them on startup.

## Commands

| Command  | Description              |
| -------- | ------------------------ |
| `/mpg`   | Open the music player GUI |

## Features

- **Browse & Play** — Opens a song list form; tap a song to queue it
- **Pause / Resume** — Control playback from the main menu
- **Stop** — Stop playback and clear the playlist
- **Playlist** — View current queue in chat

## Building

```bash
python -m build --wheel
```

Output: `dist/endstone_mediaplayer_ui-*.whl`

## Architecture

- **Language**: Python 3.10+
- **Cross-plugin communication**: Uses `server.dispatch_command()` to send `/mpm` commands to the C plugin
- **Song list**: Scans `plugins/endstone_mediaplayer/nbs/` via `os.listdir()` — same NTFS enumeration order as the C plugin's `FindFirstFileW`

## License

This project is licensed under **GPL-3.0**. See [LICENSE](LICENSE) for details.
