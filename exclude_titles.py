#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 获取错字重定向列表

import requests
import opencc

_TO_SIMPLIFIED_CHINESE = opencc.OpenCC("t2s.json")


def fetch_excluded_titles():
    excluded_titles = set()
    category = "Category:錯字重定向"
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "max",
    }
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])
        for member in members:
            excluded_titles.add(_TO_SIMPLIFIED_CHINESE.convert(member["title"]))
        if "continue" in data:
            params.update(data["continue"])
        else:
            break
    return excluded_titles


def save_excluded_titles(filename="exclude_titles.txt"):
    excluded_titles = fetch_excluded_titles()
    with open(filename, "w", encoding="utf-8") as f:
        for title in excluded_titles:
            f.write(title + "\n")


if __name__ == "__main__":
    save_excluded_titles()