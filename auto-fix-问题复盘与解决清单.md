# long-task2 auto-fix 问题复盘与解决清单

## 一、问题结论

本次 `auto-fix` 多次重复，并非 GPT 单纯修不好，而是连续遇到两个基础设施问题：

1. Harbor Oracle 缺少环境变量，验证持续失败。
2. OpenCode 找不到项目必需的 Skill，GPT 无法执行修复，客户审查结果反复不变。

旧任务已经停止。后续统一使用新数据集路径：

```text
/Users/zhengwenze/Desktop/zwz/dataset-2-fix-4
```

不要再使用：

```text
/Users/zhengwenze/Downloads/dataset-2-fix-4
```

## 二、问题 1：Harbor Oracle 环境变量缺失

### 原因

父进程执行 Harbor Oracle 时缺少：

```env
ANTHROPIC_BASE_URL
ANTHROPIC_AUTH_TOKEN
```

Oracle 因此退出码为 1、未生成 trial，`auto-fix` 将其判断为修复失败并再次调用 GPT。

### 解决办法

`/Users/zhengwenze/Desktop/zwz/LLM_Agentic/.env.local` 已写入：

```env
ANTHROPIC_BASE_URL=http://127.0.0.1
ANTHROPIC_AUTH_TOKEN=unused
```

验证结果：

```json
{"ok":true,"missing":[],"errors":[]}
```

Oracle 能生成 1 个 trial，reward 为 `1.0`。该问题已解决，不要再修改 `.env.local`。

## 三、问题 2：OpenCode 找不到必需 Skill

### 现象

客户审查连续多轮出现相同失败项：

```text
C-GOLD-003
C-PS-001
C-PS-002
C-VER-003
```

同时 GPT 输出：

```text
Skill "long-task-agent-repair" not found
```

任务文件没有发生修改，于是形成以下循环：

```text
客户审查失败 → Skill 加载失败 → GPT 未修改文件 → 再次客户审查
```

### 原因

项目 Skill 位于：

```text
/Users/zhengwenze/Desktop/zwz/LLM_Agentic/.opencode/skills
```

OpenCode 却从数据集任务目录启动，默认无法发现 `LLM_Agentic/.opencode/skills`。

### 解决办法

启动 `auto-fix` 前设置：

```bash
cd /Users/zhengwenze/Desktop/zwz/LLM_Agentic
export OPENCODE_CONFIG_DIR="$PWD/.opencode"
```

`long-task2` 创建子进程时会继承 `process.env`，因此 OpenCode 可以收到该变量，无需修改源码，也不需要把 Skill 复制到每个任务目录。

`long-task-agent-repair` 已手工加载成功；其余 Skill 若遇到 Provider overloaded，应在服务恢复后重试，不能误判为 Skill 不可见。

## 四、为什么重复修复 8 次

重试由 `long-task2 auto-fix` 控制：

```text
调用 GPT → 执行验证 → 验证失败 → 再次调用 GPT
```

前半段重复由 Oracle 环境变量缺失引起，后半段重复由 Skill 不可见引起。它不是 GPT 主动决定连续修复 8 次。

## 五、重新启动前检查

```bash
cd /Users/zhengwenze/Desktop/zwz/LLM_Agentic

# 检查环境变量文件
cat .env.local

# 检查必需 Skill
ls -la .opencode/skills

# 指定 OpenCode 配置目录
export OPENCODE_CONFIG_DIR="$PWD/.opencode"
echo "$OPENCODE_CONFIG_DIR"
```

应确认存在：

```text
long-task-agent-repair
audit-harbor-initial-reward
customer-task-audit
```

## 六、推荐启动命令

```bash
long-task2 auto-fix \
  --dataset "/Users/zhengwenze/Desktop/zwz/dataset-2-fix-4" \
  --env handoffs-delegation-continuity \
  --concurrency 1
```

## 七、启动后的判断标准

正常情况：

- `opencode run --dir` 使用 Desktop/zwz 下的新数据集路径；
- 不再出现 `Skill "..." not found`；
- `instruction.md`、`tests/validator.py`、`solution/solve.py` 等文件产生实际修改；
- 客户审查失败项减少或发生变化。

出现以下任一情况应停止任务并检查环境：

- 仍使用旧 Downloads 路径；
- 再次出现 Skill not found；
- 连续多轮客户审查结果完全相同，且任务文件没有修改。

`ProviderHeaderTimeoutError` 或 `Our servers are currently overloaded` 属于模型服务临时异常，可短暂重试，与 Skill 不可见不是同一问题。
