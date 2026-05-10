# api-lab-ollama-local-minimal

> 最小化体验：调用本机 **Ollama** 服务跑一次本地推理。

> 想"通过实操验证理解"而不是"只把代码跑通"？请先翻 [`LEARNING.md`](./LEARNING.md)：
> 里面有 **学习目标 / 实操验证清单 / 自检题 / 跟其它仓库的连接**。本 README 主要负责"具体怎么跑"。

## 它在做什么

- 先 GET `http://localhost:11434/api/tags` 检测 Ollama 是否在跑
- 然后 POST `http://localhost:11434/api/chat` 发起一次非流式聊天
- 把回答打印 + 写入 `output/result.json`

## 它**不**会做的事

- **不会自动 pull 模型**。模型动不动几个 GB，自动下载会浪费你的磁盘和带宽。
- **不会自动启动 Ollama**。需要你自己确认本机服务已运行。
- 不会反复重试。

## 准备工作

1. **安装 Ollama**：https://ollama.com/download
2. **启动服务**：
   - macOS：打开 Ollama.app；或终端跑 `ollama serve`
   - 验证：`curl http://localhost:11434/api/tags` 应返回 JSON
3. **拉一个小模型**（任选一个，越小越快）：
   ```bash
   ollama list                # 看你本机有哪些
   # 还没有就 pull 一个，例如：
   # ollama pull qwen2.5:0.5b
   # ollama pull llama3.2:1b
   ```
4. 把那个模型名填进 `.env` 的 `OLLAMA_MODEL`。

## 运行步骤

```bash
cd api-lab-ollama-local-minimal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env：
#   OLLAMA_BASE_URL=http://localhost:11434
#   OLLAMA_MODEL=qwen2.5:0.5b   （示例，请用 ollama list 看到的实际名字）

python3 main.py
cat output/result.json
```

## 常见报错

| 终端打印 | 可能原因 | 怎么处理 |
| --- | --- | --- |
| `无法连接到 Ollama 服务` | 没装 Ollama / 没启动 / 端口被占 | 装 + 启动；`curl http://localhost:11434/api/tags` 验通 |
| `HTTP 404` + 提示 pull | 本机没拉过那个模型 | `ollama list` 看一眼，或换一个已拉的模型名 |
| `请求超时（30s）` | 模型太大或本机算力不够 | 换更小模型，例如 `qwen2.5:0.5b` / `llama3.2:1b` |
| `响应结构与 Ollama /api/chat 预期不符` | Ollama 版本太旧 | `ollama --version` 看一下，必要时升级 |

## 本地模型 vs 云端模型（这次实验你要体会到的）

| 维度 | 本地模型（Ollama） | 云端模型（OpenRouter / Claude / Gemini） |
| --- | --- | --- |
| 数据隐私 | 数据不出本机 | 走外网 |
| 启动 | 要装服务，要拉模型 | 改 .env 就行 |
| 模型上限 | 受本机内存/显存限制 | 几乎不限 |
| 速度 | 取决于本机 | 取决于网络 + 服务商 |
| 成本 | 免费但费电 | 按 token 收钱 |

## .env.example

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=填入本机已经pull好的模型名
```

## 不会做的事

- 不会自动 pull 大模型
- 不会自动启动 Ollama
- 不会反复重试
