# 日报查询 API

## 项目结构

```
daily_core.py   # 核心逻辑：日期解析与日报查找（不涉及传输方式）
daily_api.py    # HTTP / 命令行适配器，调用 daily_core
daily_mcp.py    # MCP 适配器，调用 daily_core
```

HTTP 与 MCP 两个适配器相互独立，均只依赖 `daily_core`。

## 1. 启动服务

HTTP 服务不依赖第三方库，使用 Python 3.9+ 即可运行：

```bash
python3 daily_api.py
```

默认监听 `127.0.0.1:8000`。如需更换地址或端口：

```bash
python3 daily_api.py --host 0.0.0.0 --port 8080
```

也可以不启动 HTTP 服务，直接在命令行查询：

```bash
python3 daily_api.py 2026-09-14
python3 daily_api.py 9月14日
```

## 2. 查询日报

### 请求

```http
GET /api/daily?date=2026-09-14 HTTP/1.1
Host: localhost:8000
```

`date` 为必填参数，支持以下格式：

- `YYYY-MM-DD`，例如 `2026-09-14`
- `MM-DD`，例如 `09-14`
- `M月D日`，例如 `9月14日`
- `YYYY年M月D日`，例如 `2026年9月14日`

当前日报文件名只包含月和日，因此查询中的年份仅用于日期格式校验，不参与文件匹配。

### 成功响应：200

```json
{
  "success": true,
  "date": "2026-09-14",
  "filename": "9月14日.txt",
  "content": "# 9月14日工作日报\n\n..."
}
```

### 错误响应

缺少参数、日期格式错误时返回 `400`：

```json
{
  "success": false,
  "error": "缺少 date 参数"
}
```

对应日期没有日报文件时返回 `404`：

```json
{
  "success": false,
  "error": "未找到日报：10月1日.txt"
}
```

### curl 示例

```bash
curl "http://127.0.0.1:8000/api/daily?date=2026-09-14"
curl --get --data-urlencode "date=9月14日" "http://127.0.0.1:8000/api/daily"
```

## 3. MCP 服务

### 安装依赖

MCP 服务需要 Python 3.10+，使用官方 MCP Python SDK，通过 `stdio` 与支持 MCP 的客户端通信：

```bash
python3 -m pip install -r requirements.txt
```

建议使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

### 启动方式

```bash
python3 daily_mcp.py
```

直接启动后会等待 MCP 客户端通过标准输入发送协议消息，因此终端看起来不会显示普通提示信息。这是正常现象。通常不需要手动启动，而是由 MCP 客户端按配置自动拉起。

### 提供的工具

#### `get_daily_report`

查询指定日期的日报原文。

参数：

| 参数   | 类型     | 必填 | 说明                                                   |
| ------ | -------- | ---- | ------------------------------------------------------ |
| `date` | `string` | 是   | 支持 `YYYY-MM-DD`、`MM-DD`、`M月D日` 或 `YYYY年M月D日` |

成功结果：

```json
{
  "success": true,
  "date": "2026-09-14",
  "filename": "9月14日.txt",
  "content": "# 9月14日工作日报\n\n..."
}
```

### 客户端配置示例

以下为使用 `mcpServers` 格式的客户端配置示例；不同客户端的配置结构和文件位置可能不同（OpenCode 不使用此结构）。配置中的 Python 和脚本路径建议使用绝对路径：

```json
{
  "mcpServers": {
    "zwz-daily": {
      "command": "/Users/zhengwenze/Desktop/codex/zwz-daily/.venv/bin/python",
      "args": ["/Users/zhengwenze/Desktop/codex/zwz-daily/daily_mcp.py"]
    }
  }
}
```

客户端连接后会发现工具并提供给模型，模型可以根据用户问题选择调用 `get_daily_report`，例如：

> 查询 9 月 14 日的日报，并总结当天完成的工作。

注意：`daily_mcp.py` 是 MCP 服务入口，不需要先启动 `daily_api.py`；两者共享相同的日报文件和查询逻辑。

日期非法或日报不存在时，工具返回 `{"success": false, "error": "错误说明"}`；调用方应检查 `success` 字段。这类业务错误通过普通工具结果返回，而非 HTTP 状态码。文件不区分年份，提供年份时仅校验日期是否合法。
