# tg-115-saver

> Telegram 机器人监听 115 分享链接，自动转存到你网盘的指定目录。
> 复刻自 [media_automator](https://github.com/remedy5902/media_automator) 的核心链路，只保留最关键的功能：**监听 → 识别 → 转存 → 回报**。

## 它干什么

把项目拉进 TG 群（或私聊它），群里出现 115 分享链接（`115.com/s`、`115cdn.com/s`、`anxia.com/s` 等）时，机器人自动：

1. 识别链接与提取码（支持「提取码：xxxx」「#访问码」等常见写法）
2. 用 [p115client](https://github.com/ChenyangGao/web-mount-packs) 遍历分享内全部文件并转存到配置的目录
3. 回报转存结果（目标路径、文件数）
4. 可选：转存完成后 POST webhook，通知下游整理器（如 cloud-media-sync / MoviePilot）

24 小时内同一链接只处理一次；转存任务串行排队，不会挤爆 115 接口。

## 部署

```bash
git clone https://github.com/Russ534/tg-115-saver.git
cd tg-115-saver
cp config.example.json data/config.json   # 编辑配置
docker compose up -d
```

首次运行需要在日志里完成 Telethon 登录（输入手机号 + 验证码），成功后生成 `data/tg115saver.session`，之后免登录。

## 配置说明

| 字段 | 说明 |
|---|---|
| `api_id` / `api_hash` | 到 [my.telegram.org](https://my.telegram.org) 申请 |
| `allowed_chats` | 监听的群/频道（`@用户名` 或 `-100` 开头的 id）；空 = 不监听群组 |
| `allow_private` | 是否响应私聊（默认开） |
| `cookie` | 115 网盘 Cookie（浏览器 F12 复制 Cookie 请求头），失效需更换 |
| `target_cid` | 转存目标目录 id（115 网页版地址栏里的 cid） |
| `target_name` | 目标目录可读名（可选，只用于通知展示） |
| `webhook_url` | 转存完成回调地址（POST JSON），留空不调用 |
| `dedup_hours` | 同链接去重窗口小时数（默认 24） |
| `proxy` | 访问 Telegram 的代理（可选，如 `http://192.168.1.1:7890`） |

## webhook 数据格式

```json
{
  "event": "transfer_done",
  "share_code": "abcd1234",
  "url": "https://115.com/s/abcd1234",
  "target_cid": 123456789,
  "target_name": "/我的网盘/待整理",
  "saved": 42
}
```

## 与 media_automator 的关系

原项目功能很全（订阅、洗版、豆瓣、Emby、签到……核心逻辑编译成 .so 不便维护）。本项目只抽最关键的「分享链接转存」链路，全部明文 ~400 行，方便自己改。

- 转存核心：115 webapi `share_list` + `share_receive`（经 p115client）
- 监听：Telethon 用户客户端（跟原项目同栈）

## License

MIT
