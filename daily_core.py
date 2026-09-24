#!/usr/bin/env python3
"""日报查询的核心逻辑：日期解析与文件查找，不涉及任何传输方式。"""

import re
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def parse_date(value: str) -> tuple[int, int]:
    """解析 YYYY-MM-DD、MM-DD、YYYY年M月D日 或 M月D日。"""
    value = value.strip()
    patterns = (
        r"^(?:\d{4}-)?(\d{1,2})-(\d{1,2})$",
        r"^(?:\d{4}年)?(\d{1,2})月(\d{1,2})日?$",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, value)
        if match:
            month, day = map(int, match.groups())
            # 指定年份时校验真实日期；省略年份时允许 2 月 29 日。
            year_match = re.match(r"^(\d{4})[-年]", value)
            year = int(year_match.group(1)) if year_match else 2024
            date(year, month, day)
            return month, day
    raise ValueError("日期格式应为 YYYY-MM-DD、MM-DD 或 M月D日")


def find_daily(date_value: str) -> tuple[str, str]:
    """返回日报文件名和正文；找不到时抛出 FileNotFoundError。"""
    month, day = parse_date(date_value)
    filename = f"{month}月{day}日.txt"
    file_path = BASE_DIR / filename
    if not file_path.is_file():
        raise FileNotFoundError(filename)
    return filename, file_path.read_text(encoding="utf-8")
