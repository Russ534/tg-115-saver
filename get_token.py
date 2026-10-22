# -*- coding: utf-8 -*-
"""从 Windows 凭据管理器取 GitHub PAT 并测试权限"""
import subprocess, json, urllib.request

inp = "protocol=https\nhost=github.com\n\n"
r = subprocess.run(["git", "credential", "fill"], input=inp, capture_output=True, text=True)
token = None
for line in r.stdout.splitlines():
    if line.startswith("password="):
        token = line.split("=", 1)[1]
print("PAT 获取:", "成功 len=%d" % len(token) if token else "失败")

req = urllib.request.Request("https://api.github.com/user",
                             headers={"Authorization": "token " + token, "User-Agent": "tg-115-saver"})
try:
    with urllib.request.urlopen(req) as resp:
        u = json.loads(resp.read())
        print("登录身份:", u.get("login"), "| repos:", u.get("public_repos"), "public /", u.get("total_private_repos"), "private")
        scopes = resp.headers.get("X-OAuth-Scopes", "")
        print("token scopes:", scopes)
except Exception as e:
    print("API 调用失败:", e)
