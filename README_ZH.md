# MediaPlayer UI for Endstone

[![CI](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml/badge.svg)](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[English](README.md) | [简体中文](README_ZH.md)

为 [MediaPlayer](https://github.com/ReallocAll/endstone-mediaplayer) C 插件提供表单 GUI 的 Python [Endstone](https://github.com/EndstoneMC/endstone) 插件。

玩家在游戏中输入 `/mpg` 即可打开交互式菜单，浏览歌曲、控制播放、管理播放列表，无需记忆命令语法。

## 依赖

- [endstone_mediaplayer](https://github.com/ReallocAll/endstone-mediaplayer) C 插件已安装并启用
- Endstone API >= 0.11

## 安装

1. 下载或构建 `endstone_mediaplayer_ui-*.whl`
2. 将 `.whl` 文件放入服务器的 `plugins/` 目录
3. 重启服务器

Endstone 会在启动时自动发现并安装 `plugins/` 下的 `.whl` 文件。

## 命令

| 命令     | 说明           |
| -------- | -------------- |
| `/mpg`   | 打开音乐播放器 |

## 功能

- **Browse & Play** — 打开歌曲列表表单，点击即可加入播放队列
- **Pause / Resume** — 在主菜单中暂停或恢复播放
- **Stop** — 停止播放并清空播放列表
- **Playlist** — 在聊天中查看当前播放队列

## 构建

```bash
python -m build --wheel
```

产物：`dist/endstone_mediaplayer_ui-*.whl`

## 技术架构

- **语言**：Python 3.10+
- **跨插件通信**：通过 `server.dispatch_command()` 向 C 插件发送 `/mpm` 命令
- **歌曲列表**：使用 `os.listdir()` 扫描 `plugins/endstone_mediaplayer/nbs/`，与 C 插件的 `FindFirstFileW` 保持相同的 NTFS 枚举顺序

## 许可

本项目使用 **GPL-3.0** 许可。详见 [LICENSE](LICENSE)。
