# 小红书助手 · Xiaohongshu Skill for OpenClaw

使用小红书官方接口读取帖子内容和博主信息。

## 安装

```bash
openclaw skills install git:GlowingGoose/xhs-skill
```

## 使用方式

安装后对 OpenClaw 说：
- **A. 博主信息** → 输入博主笔记页面链接，获取博主主页信息
- **B. 帖子内容/评论区** → 输入帖子链接，获取笔记正文或评论区

## 登录

首次使用会自动弹出小红书扫码登录界面，使用小红书 App 扫码即可。

**重要**：登录状态会保存在 `~/.xiaohongshu-cli/cookies.json`，无需每次重新登录。

## 技术说明

- 登录：Camoufox 浏览器执行 QR 扫码，所有 API 请求通过官方 xhs-cli SDK
- 读取：直接调用 xhs_cli 官方接口，无需浏览器
- 反爬：`request_delay` 自动请求间隔，附合小红书频率限制
- Cookie 路径：`~/.xiaohongshu-cli/cookies.json`

## 依赖

- Python ≥ 3.10
- [xhs-cli](https://pypi.org/project/xhs-cli/) ≥ 0.6.4
- [camoufox](https://pypi.org/project/camoufox/) ≥ 1.0

## 作者

GlowingGoose · 2026
