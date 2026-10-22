# -*- coding: utf-8 -*-
"""建 GitHub 仓库并推送 tg-115-saver（走代理）"""
import subprocess
import json
import os

PROJ = r"E:\WorkBuddy\2026-10-22-09-49-08\tg-115-saver"
os.environ["HTTPS_PROXY"] = "http://192.168.31.201:7890"
os.environ["HTTP_PROXY"] = "http://192.168.31.201:7890"

def get_token():
    inp = "protocol=https\nhost=github.com\n\n"
    r = subprocess.run(["git", "credential", "fill"], input=inp, capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    raise SystemExit("取不到 PAT")

token = get_token()
import urllib.request
import urllib.error

proxy_handler = urllib.request.ProxyHandler({"https": "http://192.168.31.201:7890", "http": "http://192.168.31.201:7890"})
opener = urllib.request.build_opener(proxy_handler)

# 1. 建仓库
body = json.dumps({
    "name": "tg-115-saver",
    "description": "Telegram 机器人监听 115 网盘分享链接，自动转存到指定目录（复刻自 media_automator 核心链路）",
    "private": False,
    "has_wiki": False,
    "auto_init": False,
}).encode()
req = urllib.request.Request(
    "https://api.github.com/user/repos",
    data=body,
    headers={"Authorization": "token " + token, "User-Agent": "tg-115-saver",
             "Accept": "application/vnd.github+json"},
    method="POST",
)
try:
    with opener.open(req, timeout=30) as resp:
        info = json.loads(resp.read())
        print("仓库已创建:", info.get("html_url"))
except urllib.error.HTTPError as e:
    if e.code == 422:
        print("仓库已存在，继续推送")
    else:
        print("建仓失败:", e.code, e.read().decode()[:300])
        raise SystemExit(1)

# 2. git init + push（git 也走代理）
os.chdir(PROJ)
env = dict(os.environ)
def sh(*args):
    r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=120)
    out = (r.stdout + r.stderr).strip()
    print("$", " ".join(args[:3]), "->", out[-200:])
    return r

sh("git", "init", "-b", "main")
sh("git", "add", "-A")
sh("git", "-c", "user.name=Russ534", "-c", "user.email=jfh1109@163.com",
   "commit", "-m", "feat: tg-115-saver v1.0.0 - TG bot auto-saving 115 share links")
sh("git", "branch", "-M", "main")
try:
    sh("git", "remote", "add", "origin", "https://github.com/Russ534/tg-115-saver.git")
except Exception:
    pass
r = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True, env=env, timeout=180)
print("push:", (r.stdout + r.stderr).strip()[-300:])
