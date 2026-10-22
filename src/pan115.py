# -*- coding: utf-8 -*-
"""115 网盘转存封装（基于 p115client）"""
import asyncio
import time

from p115client import P115Client


class Pan115:
    def __init__(self, cookie: str):
        self.client = P115Client(cookie)
        self._last_check = 0.0

    async def _to_thread(self, fn, *a, **kw):
        return await asyncio.to_thread(fn, *a, **kw)

    async def alive(self) -> bool:
        """每隔 10 分钟做一次登录态校验（多了没必要）"""
        now = time.time()
        if now - self._last_check < 600:
            return True
        try:
            resp = await self._to_thread(self.client.user_info)
            ok = bool(resp.get("data", {}).get("user_id"))
        except Exception:
            ok = False
        if ok:
            self._last_check = now
        return ok

    async def _list_share_files(self, share_code: str, receive_code: str) -> list[dict]:
        """遍历分享内全部文件（含子目录），返回 [{"id": file_id, "name": ...}, ...]"""
        files: list[dict] = []
        seen_dirs = {0}
        queue = [0]
        while queue:
            cid = queue.pop(0)
            offset = 0
            while True:
                payload = {
                    "share_code": share_code,
                    "receive_code": receive_code,
                    "cid": cid,
                    "offset": offset,
                    "limit": 1150,
                    "order": "file_type",
                    "asc": 1,
                }
                resp = await self._to_thread(self.client.share_list, payload)
                data = resp.get("data") or {}
                batch = data.get("list") or []
                for item in batch:
                    ftype = item.get("fc") or item.get("fid")  # 目录 fc=0/1? 目录项用 fid 表示
                    if item.get("fc") == 0 or str(item.get("fid", "")).startswith("0"):
                        # 目录：fc=0 为文件夹（cate_id 场景除外），进队列继续翻
                        queue.append(item["fid"])
                        seen_dirs.add(item["fid"])
                    else:
                        files.append({"id": item["fid"], "name": item.get("fn", "")})
                total = int(data.get("count") or 0)
                offset += len(batch)
                if not batch or offset >= total:
                    break
        return files

    async def receive_share(
        self, share_code: str, receive_code: str, target_cid: int
    ) -> dict:
        """转存整个分享到 target_cid，返回 {"ok", "saved", "total", "raw"}"""
        try:
            files = await self._list_share_files(share_code, receive_code)
            ids = [f["id"] for f in files if f["id"]]
            if not ids:
                # 分享根目录直接转（空列表时把 cid=0 当作整体交给接口）
                ids = [0]
            payload = {
                "share_code": share_code,
                "receive_code": receive_code,
                "file_id": ",".join(str(i) for i in ids),
                "cid": target_cid,
            }
            resp = await self._to_thread(self.client.share_receive, payload)
            ok = resp.get("state")
            return {
                "ok": bool(ok),
                "saved": len(ids) if ids != [0] else None,
                "total": len(files),
                "raw": resp,
                "err": None if ok else str(resp.get("error") or resp.get("error_msg") or resp),
            }
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "saved": 0, "total": 0, "raw": None, "err": str(e)}

    async def dir_path(self, cid: int) -> str:
        """把目录 id 转成可读路径（失败时退回 id 文本）"""
        try:
            resp = await self._to_thread(
                self.client.fs_file, {"file_id": cid}
            )
            path = resp.get("data", [])
            if isinstance(path, list) and path:
                return "/" + "/".join(
                    p.get("name") if isinstance(p, dict) else str(p) for p in path
                )
        except Exception:  # noqa: BLE001
            pass
        return str(cid)
