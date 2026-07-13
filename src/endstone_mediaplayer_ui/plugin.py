"""MediaPlayer UI -- form frontend for the endstone_mediaplayer C plugin."""

import os

from endstone import Player
from endstone.form import ActionForm
from endstone.plugin import Plugin

NBS_DIR = "plugins/endstone_mediaplayer/nbs"


def _safe_decode(name: str) -> str:
    """Decode surrogateescape-encoded filename back to proper UTF-8."""
    try:
        return name.encode("utf-8", "surrogateescape").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def _list_nbs():
    """Scan nbs/ directory. os.listdir on Windows uses FindFirstFile
    internally, producing the same NTFS order as the C plugin."""
    try:
        return [_safe_decode(f) for f in os.listdir(NBS_DIR) if f.lower().endswith(".nbs")]
    except FileNotFoundError:
        return []


class MediaPlayerUI(Plugin):
    prefix = "MediaPlayerUI"
    api_version = "0.11"
    load = "POSTWORLD"
    depend = ["mediaplayer"]

    commands = {
        "mpg": {
            "description": "Open the music player GUI",
            "usages": ["/mpg"],
            "permissions": ["mediaplayer_ui.command.mpg"],
        }
    }
    permissions = {
        "mediaplayer_ui.command.mpg": {
            "description": "Allow using /mpg",
            "default": True,
        }
    }

    def on_enable(self) -> None:
        self.logger.info("MediaPlayerUI enabled! /mpg to open.")

    def on_disable(self) -> None:
        self.logger.info("MediaPlayerUI disabled.")

    def on_command(self, sender, command, args) -> bool:
        if command.name == "mpg":
            if not isinstance(sender, Player):
                sender.send_message("\u00a7c[MediaPlayer] This command requires a player")
                return True
            self._show_main(sender)
        return True

    def _show_main(self, player: Player):
        form = ActionForm()
        form.title = "\u00a7aMediaPlayer"
        form.content = "Select an option:"
        form.add_button("Browse & Play")
        form.add_button("Pause")
        form.add_button("Resume")
        form.add_button("Stop")
        form.add_button("Playlist")

        def on_submit(s, idx):
            match idx:
                case 0:
                    self._show_songs(s)
                case 1:
                    self.server.dispatch_command(s, "mpm pause")
                case 2:
                    self.server.dispatch_command(s, "mpm resume")
                case 3:
                    self.server.dispatch_command(s, "mpm stop")
                case 4:
                    self.server.dispatch_command(s, "mpm playlist")

        form.on_submit = on_submit
        player.send_form(form)

    def _show_songs(self, player: Player):
        files = _list_nbs()
        if not files:
            player.send_message("\u00a7c[MediaPlayer] No .nbs files!")
            return

        form = ActionForm()
        form.title = "\u00a7aSelect a Song"
        form.content = f"Found \u00a7e{len(files)}\u00a7r song(s)"

        for name in files:
            form.add_button(os.path.splitext(name)[0])

        def on_submit(s, idx):
            self.server.dispatch_command(s, f"mpm add {idx} 1 3")

        form.on_submit = on_submit
        player.send_form(form)
