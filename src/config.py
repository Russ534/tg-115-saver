# -*- coding: utf-8 -*-
"""配置加载"""
import json
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # Telegram（Telethon）
    api_id: int
    api_hash: str
    # 用户客户端 session 名（首次运行会要求扫码/手机号登录，生成 .session 文件后免登录）
    session: str = "tg115saver"
    # 只监听这些聊天（聊天 id 数字或 @用户名）；为空则只响应私聊
    allowed_chats: list = field(default_factory=list)
    # 是否响应私聊
    allow_private: bool = True

    # 115
    cookie: str = ""
    # 转存目标目录 id（115 网盘里的目录 cid）
    target_cid: int = 0
    # 转存目标目录名（用于通知展示，可选）
    target_name: str = ""

    # 转存完成后的 webhook（POST JSON），留空则不调用
    webhook_url: str = ""

    # 同一链接去重窗口（小时）
    dedup_hours: int = 24

    # 代理（可选，如 http://127.0.0.1:7890）
    proxy: str = ""


def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    cfg = Config(
        api_id=int(raw["api_id"]),
        api_hash=raw["api_hash"],
        session=raw.get("session", "tg115saver"),
        allowed_chats=raw.get("allowed_chats", []),
        allow_private=raw.get("allow_private", True),
        cookie=raw.get("cookie", os.environ.get("PAN115_COOKIE", "")),
        target_cid=int(raw.get("target_cid", 0)),
        target_name=raw.get("target_name", ""),
        webhook_url=raw.get("webhook_url", ""),
        dedup_hours=int(raw.get("dedup_hours", 24)),
        proxy=raw.get("proxy", os.environ.get("SAVER_PROXY", "")),
    )
    if not cfg.api_id or not cfg.api_hash:
        raise ValueError("api_id / api_hash 未配置")
    if not cfg.cookie:
        raise ValueError("115 cookie 未配置")
    if not cfg.target_cid:
        raise ValueError("target_cid 未配置")
    return cfg
