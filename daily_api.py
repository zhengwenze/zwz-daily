#!/usr/bin/env python3
"""日报查询的 HTTP / 命令行适配器，核心逻辑见 daily_core。"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from daily_core import find_daily


def make_response(status: int, payload: dict) -> tuple[int, bytes]:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return status, body


class DailyRequestHandler(BaseHTTPRequestHandler):
    """处理 GET /api/daily?date=YYYY-MM-DD 请求。"""

    def do_GET(self) -> None:  # noqa: N802 - 由 BaseHTTPRequestHandler 约定
        parsed = urlparse(self.path)
        if parsed.path != "/api/daily":
            status, body = make_response(404, {"success": False, "error": "接口不存在"})
        else:
            values = parse_qs(parsed.query).get("date", [])
            if not values or not values[0].strip():
                status, body = make_response(
                    400, {"success": False, "error": "缺少 date 参数"}
                )
            else:
                try:
                    filename, content = find_daily(values[0])
                    status, body = make_response(
                        200,
                        {
                            "success": True,
                            "date": values[0].strip(),
                            "filename": filename,
                            "content": content,
                        },
                    )
                except ValueError as exc:
                    status, body = make_response(
                        400, {"success": False, "error": str(exc)}
                    )
                except FileNotFoundError as exc:
                    status, body = make_response(
                        404,
                        {"success": False, "error": f"未找到日报：{exc.args[0]}"},
                    )

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), DailyRequestHandler)
    print(f"日报 API 已启动：http://{host}:{port}")
    print("查询示例：http://localhost:%d/api/daily?date=2026-09-14" % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n日报 API 已停止")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="按日期查询日报")
    parser.add_argument(
        "date", nargs="?", help="日期，例如 2026-09-14、09-14 或 9月14日"
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="API 监听地址，默认 127.0.0.1"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="API 监听端口，默认 8000"
    )
    args = parser.parse_args()

    if args.date:
        try:
            filename, content = find_daily(args.date)
            print(f"--- {filename} ---")
            print(content, end="" if content.endswith("\n") else "\n")
        except (ValueError, FileNotFoundError) as exc:
            parser.error(str(exc))
    else:
        run_server(args.host, args.port)


if __name__ == "__main__":
    main()
