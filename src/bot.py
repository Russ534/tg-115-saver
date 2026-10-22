# -*- coding: utf-8 -*-
"""TG 事件处理：识别 115 分享链接并转存"""
import asyncio
import logging
import time

from telethon import events

from .links import parse_share_links
from .webhook import post_webhook

log = logging.getLogger("tg115saver.bot")


class SaverBot:
    def __init__(self, cfg, pan115, client):
        self.cfg = cfg
        self.pan = pan115
        self.client = client
        # 链接去重: share_code -> 时间戳
        self._seen: dict[str, float] = {}
        # 并发闸门：同一时间只跑 1 个转存任务
        self._lock = asyncio.Lock()

    def _allowed(self, event) -> bool:
        chat = event.chat
        if event.is_private:
            return self.cfg.allow_private
        if not self.cfg.allowed_chats:
            return False
        ids = {str(x).lstrip("@").lower() for x in self.cfg.allowed_chats}
        username = (getattr(chat, "username", "") or "").lower()
        cid = str(getattr(chat, "id", ""))
        return username in ids or cid in ids

    def _is_dup(self, share_code: str) -> bool:
        now = time.time()
        window = self.cfg.dedup_hours * 3600
        # 清理过期
        self._seen = {k: t for k, t in self._seen.items() if now - t < window}
        if share_code in self._seen:
            return True
        self._seen[share_code] = now
        return False

    async def handle(self, event):
        if not self._allowed(event):
            return
        text = event.raw_text or ""
        links = parse_share_links(text)
        if not links:
            return

        for link in links:
            code = link["share_code"]
            if self._is_dup(code):
                await event.reply(f"⏭ {code} 最近已处理过，跳过")
                continue
            async with self._lock:
                log.info("开始转存 share_code=%s 提取码=%s", code, link["receive_code"] or "无")
                result = await self.pan.receive_share(
                    link["share_code"], link["receive_code"], self.cfg.target_cid
                )
            if result["ok"]:
                target = self.cfg.target_name or await self.pan.dir_path(self.cfg.target_cid)
                saved = result.get("saved")
                msg = f"✅ 转存成功\n📁 目标：{target}"
                if saved:
                    msg += f"\n📦 文件/目录数：{saved}"
                await event.reply(msg)
                await post_webhook(
                    self.cfg.webhook_url,
                    {
                        "event": "transfer_done",
                        "share_code": code,
                        "url": link["url"],
                        "target_cid": self.cfg.target_cid,
                        "target_name": target,
                        "saved": saved,
                    },
                )
            else:
                await event.reply(f"❌ 转存失败：{result.get('err') or '未知错误'}")
                log.error("转存失败 %s: %s", code, result.get("err"))

    def register(self):
        self.client.add_event_handler(self.handle, events.NewMessage())
