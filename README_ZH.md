# MediaPlayer UI for Endstone

[![CI](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml/badge.svg)](https://github.com/ReallocAll/endstone-mediaplayer-ui/actions/workflows/build.yml)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)
[English](README.md) | [简体中文](README_ZH.md)

为 [MediaPlayer](https://github.com/ReallocAll/endstone-mediaplayer) C 插件提供表单 GUI 的 Python [Endstone](https://github.com/EndstoneMC/endstone) 插件。

`chs` 分支专门用于简体中文界面和菜单易用性优化。它只调用 MediaPlayer 已经公开的 `/mpm` 能力，不在 UI 层伪造后端不存在的播放状态或功能。

玩家在游戏中输入 `/mpg` 即可打开交互式菜单，无需记忆 `/mpm` 命令参数。

## 依赖

- [endstone_mediaplayer](https://github.com/ReallocAll/endstone-mediaplayer) C 插件已安装并启用
- Endstone API >= 0.11

## 安装

1. 下载或构建 `endstone_mediaplayer_ui-*.whl`
2. 将 `.whl` 文件放入服务器的 `plugins/` 目录
3. 重启服务器

Endstone 会在启动时自动发现并安装 `plugins/` 下的 `.whl` 文件。

## 命令

| 命令 | 说明 |
| --- | --- |
| `/mpg` | 打开音乐播放器菜单 |

## 功能

- **全中文菜单**：玩家可见的菜单、按钮和提示均使用简体中文
- **浏览与搜索歌曲**：按歌曲名筛选 `.nbs` 文件，搜索结果仍保留 MediaPlayer 原始歌曲索引
- **快速播放一次**：使用默认 BossBar 进度显示加入播放队列
- **单曲循环**：以 `loop=-1` 无限循环当前歌曲，直到停止播放
- **自定义播放次数**：可输入任意有效正整数作为 `loop` 次数
- **进度显示方式**：可选择 BossBar、Tip、弹窗或不显示
- **播放控制**：直接暂停、继续、停止并清空播放列表
- **查看播放列表**：调用后端 `/mpm playlist`，结果显示在聊天栏

当前 UI 不读取 MediaPlayer 的内部播放列表状态，因此不会伪造可视化队列编辑器；只有后端已经公开且能够由表单安全表达的功能才会加入菜单。

## 播放参数

选择歌曲后可以直接：

- 播放一次
- 单曲无限循环
- 打开“自定义播放参数”，设置：
  - 循环方式
  - 指定播放次数
  - 进度显示方式

底层仍使用 MediaPlayer 原生命令：

```text
/mpm add <index> [loop] [bar]
```

其中：

- `loop=-1`：无限循环
- `loop=1`：播放一次
- `loop=N`：播放 N 次
- `bar=0`：不显示
- `bar=1`：弹窗
- `bar=2`：Tip
- `bar=3`：BossBar

## 构建

```bash
python -m build --wheel
```

产物：`dist/endstone_mediaplayer_ui-*.whl`

## 技术架构

- **语言**：Python 3.10+
- **跨插件通信**：通过 `server.dispatch_command()` 向 C 插件发送 `/mpm` 命令
- **歌曲列表**：使用 `os.listdir()` 扫描 `plugins/endstone_mediaplayer/nbs/`，保持与后端歌曲索引一致
- **表单能力**：使用 Endstone `ActionForm`、`ModalForm`、`Dropdown` 和 `TextInput`
- **后端边界**：不修改 MediaPlayer C 插件，不实现后端未公开的能力

## 许可

本项目使用 **GPL-3.0** 许可。详见 [LICENSE](LICENSE)。
