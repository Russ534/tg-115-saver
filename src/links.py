# -*- coding: utf-8 -*-
"""解析 115 分享链接，提取 share_code 与提取码"""
import re

# 115 系分享链接：115.com/s / 115cdn.com/s / anxia.com / share.115.com 等
_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:115\.com|115cdn\.com|anxia\.com|share\.115\.com)/s/(?P<code>[0-9A-Za-z]+)",
    re.IGNORECASE,
)

# 提取码：常见写法「提取码：abcd」「访问码 abcd」「密码:abcd」「#访问码」
_PWD_RE = re.compile(
    r"(?:提取码|访问码|密码|接码|取件码)\s*[：:=\s]\s*([0-9A-Za-z]{3,8})",
    re.IGNORECASE,
)

# URL 自带访问码的形式：.../s/xxxx?#访问码 或 ?pwd=xxxx
_URL_PWD_RE = re.compile(
    r"/s/[0-9A-Za-z]+[?#](?:pwd=)?([0-9A-Za-z]{3,8})",
    re.IGNORECASE,
)


def parse_share_links(text: str) -> list[dict]:
    """从消息文本中提取全部 115 分享链接。

    返回：[{"url": 完整链接, "share_code": xxx, "receive_code": 提取码或 ""}, ...]
    同一条消息里重复链接自动去重。
    """
    if not text:
        return []
    seen = set()
    results = []
    for m in _URL_RE.finditer(text):
        code = m.group("code")
        if code in seen:
            continue
        seen.add(code)
        pwd = ""
        pm = _URL_PWD_RE.search(m.group(0))
        if pm:
            pwd = pm.group(1)
        else:
            # 提取码通常出现在链接附近的同一条消息里
            pm = _PWD_RE.search(text)
            if pm:
                pwd = pm.group(1)
        results.append({
            "url": m.group(0).split("#")[0],
            "share_code": code,
            "receive_code": pwd,
        })
    return results
