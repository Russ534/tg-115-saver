# -*- coding: utf-8 -*-
"""链接解析测试"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from links import parse_share_links


def test_basic():
    r = parse_share_links("冲！https://115.com/s/AbCd123?vi=1 提取码：9xk2\n快的很")
    assert len(r) == 1
    assert r[0]["share_code"] == "AbCd123"
    assert r[0]["receive_code"] == "9xk2"


def test_url_pwd():
    r = parse_share_links("看这个 https://115cdn.com/s/xyz987#访问码")
    assert r[0]["share_code"] == "xyz987"
    # URL 带 #访问码 但码为空 → 回落到全文找
    print(r)


def test_anxia():
    r = parse_share_links("https://anxia.com/s/QWERty12 密码: 8k3d")
    assert r[0]["share_code"] == "QWERty12"
    assert r[0]["receive_code"] == "8k3d"


def test_multi_dedup():
    text = "https://115.com/s/aaa111 和 https://115.com/s/aaa111 还有一个 https://115.com/s/bbb222"
    r = parse_share_links(text)
    assert len(r) == 2
    assert {x["share_code"] for x in r} == {"aaa111", "bbb222"}


def test_no_pwd():
    r = parse_share_links("无码链接 https://115.com/s/nopwd11")
    assert r[0]["receive_code"] == ""


def test_empty():
    assert parse_share_links("") == []
    assert parse_share_links("普通消息没有链接") == []


if __name__ == "__main__":
    test_basic(); test_url_pwd(); test_anxia(); test_multi_dedup(); test_no_pwd(); test_empty()
    print("全部通过 ✔")
