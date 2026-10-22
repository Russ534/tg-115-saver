# -*- coding: utf-8 -*-
"""tg-115-saver 入口"""
import asyncio
import logging
import os
import sys

from telethon import TelegramClient, connection

from .bot import SaverBot
from .config import load_config
from .pan115 import Pan115

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("tg115saver")

CONFIG_PATH = os.environ.get("SAVER_CONFIG", "config.json")


async def amain():
    cfg = load_config(CONFIG_PATH)
    log.info("配置加载完成，目标目录 cid=%s", cfg.target_cid)

    pan = Pan115(cfg.cookie)
    if not await pan.alive():
        log.error("115 cookie 已失效，请更新后重试")
        sys.exit(1)
    log.info("115 登录态有效")

    proxy = None
    if cfg.proxy:
        import socks  # PySocks

        proxy = (socks.HTTP if cfg.proxy.startswith("http") else socks.SOCKS5,)  # noqa
        # telethon proxy 元组: (type, host, port)
        from urllib.parse import urlparse

        u = urlparse(cfg.proxy)
        proxy = (socks.HTTP if u.scheme.startswith("http") else socks.SOCKS5, u.hostname, u.port or 1080)

    tg = TelegramClient(
        cfg.session,
        cfg.api_id,
        cfg.api_hash,
        proxy=proxy,
        connection=connection.ConnectionTcpFull,
    )
    await tg.connect()

    saver = SaverBot(cfg, pan, tg)
    saver.register()
    log.info("TG 监听已启动，等待分享链接…")
    await tg.run_until_disconnected()


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
