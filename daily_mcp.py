#!/usr/bin/env python3
"""日报查询 MCP 服务（stdio 传输）。"""

from mcp.server.fastmcp import FastMCP

from daily_core import find_daily


mcp = FastMCP("zwz-daily")


@mcp.tool()
def get_daily_report(date: str) -> dict[str, str | bool]:
    """查询指定日期的工作日报。

    日期支持 YYYY-MM-DD、MM-DD、M月D日和 YYYY年M月D日格式，例如
    2026-09-14 或 9月14日。当前日报文件名只包含月和日，因此年份仅用于
    日期格式校验，不参与文件匹配。
    """
    try:
        filename, content = find_daily(date)
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    except FileNotFoundError as exc:
        return {"success": False, "error": f"未找到日报：{exc.args[0]}"}

    return {
        "success": True,
        "date": date.strip(),
        "filename": filename,
        "content": content,
    }


if __name__ == "__main__":
    # stdio 是 MCP 协议通道，不要向 stdout 写调试日志。
    mcp.run(transport="stdio")
