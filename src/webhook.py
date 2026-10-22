# -*- coding: utf-8 -*-
"""转存完成 webhook：把结果推给下游（如 cms / MoviePilot 等整理器）"""
import logging

import httpx

log = logging.getLogger("tg115saver.webhook")


async def post_webhook(url: str, payload: dict, timeout: float = 10.0):
    """url 为空则静默跳过；失败只记日志，不影响主流程"""
    if not url:
        return
    try:
        async with httpx.AsyncClient(timeout=timeout) as cli:
            resp = await cli.post(url, json=payload)
            log.info("webhook %s -> %s", url, resp.status_code)
    except Exception as e:  # noqa: BLE001
        log.warning("webhook 调用失败: %s", e)
