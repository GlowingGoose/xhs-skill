---
name: xiaohongshu
description: "Automatically check login status, trigger terminal QR-code authentication, and seamlessly invoke xhs-cli to read, search, or analyze Xiaohongshu (小红书) post content and blogger profiles."
---

# Xiaohongshu Skill

Use `xiaohongshu-cli` (invoked via `xhs`) to discover, search, and analyze Xiaohongshu contents. This skill enforces an elegant pre-flight authentication pipeline, enabling automated QR-code login verification whenever session expiry is detected.

## Authentication & Session Lifecycle (Core Workflow)

Always strictly enforce this implicit verification pipeline before attempting any data action (`read`, `search`, `user`):

1. **Passive Execution**: Attempt to execute the requested target command directly with the `--json` flag. The CLI will automatically try to load existing sessions from `~/.xiaohongshu-cli/cookies.json` or seamlessly extract native cookies from local browsers (Chrome, Edge, Arc, Safari, Firefox).
2. **Session Expiry Detection**: If the terminal execution fails and traps errors such as `NoCookieError` or `401 Unauthorized`, intercept the flow immediately. **Do not hallucinate data or exit with failure.**
3. **Trigger QR-Code Interaction**:
   - Immediately execute the interactive login pipeline: `xhs login --qrcode`
   - Capture the terminal-rendered QR-code output and present it directly to the user along with a guidance note:
     > "🔒 **系统提示**：检测到您的小红书登录状态已失效。我已在下方为您调出最新的登录二维码，请使用手机小红书 App 扫描终端显示的内容完成扫码登录。"
4. **Auto-Retry Queue**: Once the terminal hooks the webhook confirmation (`Login confirmed!`), automatically re-submit the initial command that the user originally requested, achieving a seamless continuation of service.

## Supported Actions

### ⚠️ Mandatory Clarification (必须澄清)

**Whenever the user mentions any Xiaohongshu content crawling/extraction intent, you MUST ask this clarifying question FIRST — do not proceed to any action until the user specifies:**

> **请先确认你要查询的是：**
> 
> **A. 博主信息** — 想了解某个博主的主页资料（粉丝数、简介、获赞数等）
> 
> **B. 帖子内容** — 想看某篇帖子的正文、评论、或评论区详情

Only after the user selects A or B (or explicitly states which type of content they want), proceed to the appropriate action below. Do NOT skip this step.

### 1. Get Post Content
**Trigger:** User passes a Xiaohongshu note link/ID, or asks the agent to read, summarize, rewrite, or analyze specific post insights.

**Command:** `xhs read <post-id-url-or-index> --json`

Handles:
- Full Web URL: `https://www.xiaohongshu.com/explore/6a1edb4c0000000010001c01...`
- Legacy Discovery URL: `https://www.xiaohongshu.com/discovery/item/6a1edb4c0000000010001c01`
- Raw Note ID: `6a1edb4c0000000010001c01`
- **Short Index (Cached Mapping)**: If a listing/search command was run previously in the session, the local `index_cache.json` is hit. You can pass raw short digits (e.g., `1`, `2`, `3`) to open the cached items instantly.

**Output fields to extract and present:**
- `title` — 笔记标题
- `desc` — 笔记正文内容
- `nickname` — 博主昵称
- `user_id` — 博主唯一数字 ID
- `liked_count` — 点赞数
- `collected_count` — 收藏数
- `comment_count` — 评论数
- `share_count` — 分享数
- `tag_list` — 话题标签
- `image_list` — 图片 URL 列表（渲染时默认优先采用 Markdown 格式 `![image](url)` 渲染前 3 张，其余折叠或以纯文本列表呈现，防止冗余刷屏）
- `created_at` — 笔记发布时间
- `url` — 笔记标准网页版链接

### 2. Get Blogger Info & Feeds
**Trigger:** User requests to analyze a specific blogger's niche positioning, inspect profiling metrics, or query their total post streams.

**Command:** `xhs user <user-id-or-url> --json`

Handles:
- User profile link: `https://www.xiaohongshu.com/user/profile/693988bb000000002b007b54`
- Raw User ID: `693988bb000000002b007b54`

**Output fields to extract and present:**
- `nickname` — 昵称
- `red_id` — 小红书号
- `ip_location` — IP 属地
- `desc` — 个人简介/个性签名
- `fans_count` — 粉丝基数
- `follows_count` — 关注数
- `liked_count` — 获赞与收藏累计总量
- `tags` — 身份标识标签
- `profile_url` — 个人主页直达链接

### 3. Search Trend Insights
**Trigger:** User searches for hot keywords, trending inspirations, or competitors' top performing copies on a specific topic.

**Command:** `xhs search "<keyword>" --json`

> **Note for Search:** If the user says something like "帮我搜索小红书上关于XX的内容", treat this as a Search action and present results. The user can then ask for details on any result, which triggers the mandatory clarification above.

## URL Parsing & Navigation Rules

- **Short Indexes**: Always match if the user is pointing to contextual listings (e.g., "帮我读第一个", "拆解刚才搜到的第三个"). Pass the matching scalar index straight to `xhs read`.
- **Regex Extraction**: Extract Note IDs via routing boundaries `/explore/`, `/discovery/item/`, `/note/`. Extract User profiles from `/user/profile/`.
- **Short Links Handling**: If a user uploads a mobile native share link (e.g., `xhslink.com/...`), the CLI might throw a parsing exception. If parsing fails, gracefully request the agent environment to trace the redirect location first, or prompt the user to provide a standard web domain url.

## Error Handling & Mitigation

- `xhs: not found` → Mitigation: Prompt host to install the utility globally via `uv tool install xiaohongshu-cli` or `npm install -g jackwener/xiaohongshu-cli`.
- `NeedVerifyError` (Slider Captcha) → Mitigation: Anti-crawler active defense mechanism triggered. Prompt user: "⚠️ 小红书官方触发了人机验证滑块，请立即在浏览器中打开小红书网页端（xiaohongshu.com）任意过一下滑块，或者重新运行 `xhs login --qrcode`。"
- `IpBlockedError` → Mitigation: Current server node IP restricted. Advise the environment operator to toggle local proxy nodes (VPN) or route connections through a mobile cellular hot-spot.

## Execution Constraints

- **Format Binding**: Non-TTY command redirection defaults to raw YAML serialization in this CLI. **Always** forcefully attach the `--json` option to ensure precise structure parsing for the upstream agent compiler.
- **Robustness Boundary**: When serving terminal interfaces under restrictive encodings (such as legacy Windows terminals), prepend environmental parameters if formatting crashes: `PYTHONIOENCODING=utf-8 xhs login --qrcode`.
## Changelog

### 2026-06-21
- 新增 `comments` 命令：获取帖子评论区内容（IP属地、发言时间、点赞量）
- 新增 `status` 命令：检查登录状态
- README.md：补充完整安装和使用文档

## Changelog

### 2026-06-21
- 新增 `comments` 命令：获取帖子评论区内容（IP属地、发言时间、点赞量）
- 新增 `status` 命令：检查登录状态
- README.md：补充完整安装和使用文档
