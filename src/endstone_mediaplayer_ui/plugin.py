"""MediaPlayer UI -- Chinese form frontend for the endstone_mediaplayer C plugin."""

import json
import os

from endstone import Player
from endstone.form import ActionForm, Dropdown, ModalForm, TextInput
from endstone.plugin import Plugin

NBS_DIR = "plugins/endstone_mediaplayer/nbs"
BAR_VALUES = (3, 2, 1, 0)
BAR_LABELS = {
    3: "BossBar",
    2: "Tip",
    1: "弹窗",
    0: "不显示",
}
MAX_LOOP_COUNT = 2_147_483_647
DEFAULT_LOOP = 1
DEFAULT_BAR = 3


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


def _song_title(filename: str) -> str:
    return os.path.splitext(filename)[0]


def _loop_label(loop: int) -> str:
    if loop == -1:
        return "单曲循环"
    if loop == 1:
        return "播放一次"
    return f"播放 {loop} 次"


class MediaPlayerUI(Plugin):
    prefix = "MediaPlayerUI"
    api_version = "0.11"
    load = "POSTWORLD"
    depend = ["mediaplayer"]

    commands = {
        "mpg": {
            "description": "打开音乐播放器菜单",
            "usages": ["/mpg"],
            "permissions": ["mediaplayer_ui.command.mpg"],
        }
    }
    permissions = {
        "mediaplayer_ui.command.mpg": {
            "description": "允许使用 /mpg",
            "default": True,
        }
    }

    def on_enable(self) -> None:
        self._play_settings: dict[str, tuple[int, int]] = {}
        self.logger.info("MediaPlayerUI 中文菜单已启用，输入 /mpg 打开。")

    def on_disable(self) -> None:
        self.logger.info("MediaPlayerUI 已禁用。")

    def on_command(self, sender, command, args) -> bool:
        if command.name == "mpg":
            if not isinstance(sender, Player):
                sender.send_message("§c[MediaPlayer] 该命令只能由玩家使用。")
                return True
            self._show_main(sender)
        return True

    def _player_key(self, player: Player) -> str:
        return player.xuid or player.name

    def _get_play_settings(self, player: Player) -> tuple[int, int]:
        return self._play_settings.get(
            self._player_key(player), (DEFAULT_LOOP, DEFAULT_BAR)
        )

    def _set_play_settings(self, player: Player, loop: int, bar: int) -> None:
        self._play_settings[self._player_key(player)] = (loop, bar)

    def _settings_summary(self, player: Player) -> str:
        loop, bar = self._get_play_settings(player)
        return f"{_loop_label(loop)} · {BAR_LABELS.get(bar, 'BossBar')}"

    def _show_main(self, player: Player):
        form = ActionForm()
        form.title = "§l§a媒体播放器§r"
        form.content = "请选择要执行的操作："
        form.add_button("§l§a点歌§r\n搜索并直接播放歌曲")
        form.add_button(
            f"§l§b点歌设置§r\n当前：{self._settings_summary(player)}"
        )
        form.add_button("§e暂停播放")
        form.add_button("§a继续播放")
        form.add_button("§c停止播放§r\n同时清空播放队列")
        form.add_button("§b查看播放列表§r\n结果显示在聊天栏")

        def on_submit(s, idx):
            match idx:
                case 0:
                    self._show_songs(s)
                case 1:
                    self._show_play_settings(s)
                case 2:
                    self.server.dispatch_command(s, "mpm pause")
                case 3:
                    self.server.dispatch_command(s, "mpm resume")
                case 4:
                    self.server.dispatch_command(s, "mpm stop")
                case 5:
                    self.server.dispatch_command(s, "mpm playlist")

        form.on_submit = on_submit
        player.send_form(form)

    def _show_songs(self, player: Player, query: str = ""):
        files = _list_nbs()
        if not files:
            player.send_message("§c[MediaPlayer] 没有找到 .nbs 音乐文件。")
            return

        normalized_query = query.strip().casefold()
        visible = [
            (index, name)
            for index, name in enumerate(files)
            if not normalized_query or normalized_query in _song_title(name).casefold()
        ]

        form = ActionForm()
        form.title = "§l§a点歌§r"
        if normalized_query:
            form.content = (
                f"搜索：§e{query.strip()}§r\n"
                f"匹配 §e{len(visible)}§r / {len(files)} 首歌曲\n"
                f"当前设置：{self._settings_summary(player)}"
            )
        else:
            form.content = (
                f"共找到 §e{len(files)}§r 首歌曲\n"
                f"当前设置：{self._settings_summary(player)}"
            )

        form.add_button("§b搜索歌曲§r\n按名称筛选")
        clear_filter = bool(normalized_query)
        if clear_filter:
            form.add_button("§e清除搜索筛选")

        for _, name in visible:
            form.add_button(_song_title(name))

        back_index = 1 + int(clear_filter) + len(visible)
        form.add_button("返回主菜单")

        def on_submit(s, idx):
            if idx == 0:
                self._show_search(s, query.strip())
                return

            song_offset = 1
            if clear_filter:
                if idx == 1:
                    self._show_songs(s)
                    return
                song_offset = 2

            song_pos = idx - song_offset
            if 0 <= song_pos < len(visible):
                song_index, _ = visible[song_pos]
                loop, bar = self._get_play_settings(s)
                self._enqueue(s, song_index, loop, bar)
            elif idx == back_index:
                self._show_main(s)

        form.on_submit = on_submit
        player.send_form(form)

    def _show_search(self, player: Player, current_query: str = ""):
        form = ModalForm()
        form.title = "§l§a搜索歌曲§r"
        form.add_control(
            TextInput(
                label="歌曲名",
                placeholder="输入完整或部分歌曲名；留空显示全部",
                default_value=current_query,
            )
        )
        form.submit_button = "搜索"

        def on_submit(s, data):
            try:
                values = json.loads(data)
                query = str(values[0]).strip()
            except (TypeError, ValueError, IndexError):
                s.send_message("§c[MediaPlayer] 无法读取搜索内容，请重试。")
                return
            self._show_songs(s, query)

        form.on_submit = on_submit
        player.send_form(form)

    def _show_play_settings(self, player: Player):
        current_loop, current_bar = self._get_play_settings(player)

        if current_loop == 1:
            loop_mode = 0
            count_text = "2"
        elif current_loop == -1:
            loop_mode = 1
            count_text = "2"
        else:
            loop_mode = 2
            count_text = str(current_loop)

        try:
            bar_mode = BAR_VALUES.index(current_bar)
        except ValueError:
            bar_mode = 0

        form = ModalForm()
        form.title = "§l§a点歌设置§r"
        form.add_control(
            Dropdown(
                label="播放方式",
                options=["播放一次", "单曲循环（无限）", "指定播放次数"],
                default_index=loop_mode,
            )
        )
        form.add_control(
            TextInput(
                label="指定播放次数",
                placeholder="仅在选择“指定播放次数”时生效",
                default_value=count_text,
            )
        )
        form.add_control(
            Dropdown(
                label="进度显示",
                options=["BossBar（默认）", "Tip", "弹窗", "不显示"],
                default_index=bar_mode,
            )
        )
        form.submit_button = "保存设置"

        def on_submit(s, data):
            try:
                values = json.loads(data)
                selected_loop_mode = int(values[0])
                selected_count_text = str(values[1]).strip()
                selected_bar_mode = int(values[2])
            except (TypeError, ValueError, IndexError):
                s.send_message("§c[MediaPlayer] 无法读取点歌设置，请重试。")
                return

            if selected_loop_mode == 0:
                loop = 1
            elif selected_loop_mode == 1:
                loop = -1
            elif selected_loop_mode == 2:
                try:
                    loop = int(selected_count_text)
                except ValueError:
                    loop = 0
                if loop < 1 or loop > MAX_LOOP_COUNT:
                    s.send_message(
                        "§c[MediaPlayer] 播放次数必须是 1 到 2147483647 之间的整数。"
                    )
                    self._show_play_settings(s)
                    return
            else:
                s.send_message("§c[MediaPlayer] 无效的播放方式。")
                return

            if not 0 <= selected_bar_mode < len(BAR_VALUES):
                s.send_message("§c[MediaPlayer] 无效的进度显示方式。")
                return

            bar = BAR_VALUES[selected_bar_mode]
            self._set_play_settings(s, loop, bar)
            s.send_message(
                f"§a[MediaPlayer] 点歌设置已保存：{_loop_label(loop)} · {BAR_LABELS[bar]}"
            )
            self._show_main(s)

        form.on_submit = on_submit
        player.send_form(form)

    def _enqueue(self, player: Player, song_index: int, loop: int, bar: int):
        self.server.dispatch_command(player, f"mpm add {song_index} {loop} {bar}")
