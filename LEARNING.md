# LEARNING — api-lab-ollama-local-minimal

> 这份文件回答：「我跑完这个仓库，应该真的学到什么？」

## 你跑完应该能回答的问题

1. 「本地模型」三步走：**装服务、拉模型、起服务**——分别在做什么？
2. 为什么**不能**直接用 OpenAI-compatible 那一套打 Ollama？（提示：路径不一样，是 `/api/chat`，不是 `/v1/chat/completions`）
3. 同一个 prompt，云端模型和你本机的小模型回答差距能有多大？
4. 跑本地模型时，**数据**是怎么流动的？跟云端有什么不同？

## 实操验证清单（务必动手）

### 阶段 A — 环境就绪（只做一次）
- [ ] 装 Ollama：https://ollama.com/download（macOS 一个 .dmg）
- [ ] 启动 Ollama（macOS 打开 .app；或终端 `ollama serve`）
- [ ] 验证：`curl http://localhost:11434/api/tags` 应返回 JSON（不报 connection refused 即可）
- [ ] **拉一个小模型**（重要：选小的，避免下载几个 G）：
  ```bash
  ollama pull qwen2.5:0.5b      # 约 400MB，超快
  # 或 ollama pull llama3.2:1b   # 约 1.3GB
  ```
- [ ] `ollama list` 看一眼，记下你刚拉的模型完整名字（含冒号和 tag）

### 阶段 B — 跑本仓库
- [ ] `cp .env.example .env`
- [ ] `pip install -r requirements.txt`
- [ ] 编辑 `.env`：`OLLAMA_MODEL=qwen2.5:0.5b`（用你 `ollama list` 看到的实际名字）
- [ ] `python3 main.py`
- [ ] **观察**：
  - 终端先说「Ollama 服务可达」（说明探活成功）
  - 再说「模型返回内容」
  - 耗时多半比云端慢一些（CPU 推理 + 模型小但本地）

### 阶段 C — 协议差异实验
**重点：本仓库打的是 Ollama 原生 `/api/chat`，路径和 body 都不是 OpenAI 风格。**

- [ ] 看 `main.py` 的 payload，对比 `api-lab-openai-compatible-minimal/main.py`：
  - 路径：`/api/chat` vs `/v1/chat/completions`
  - 不需要 `Authorization` header（本地不验证）
  - 取文本：`data["message"]["content"]` vs `data["choices"][0]["message"]["content"]`

- [ ] **拓展知识**：Ollama 也提供了 OpenAI-compatible 的兼容入口（`/v1/chat/completions`），
      你可以把 `api-lab-openai-compatible-minimal` 的 `AI_BASE_URL` 改成 `http://localhost:11434/v1`，
      用同一份代码也能跑通 Ollama——这是另一条"协议化"的证据。

### 阶段 D — 数据流向思考实验
- [ ] 跑一次 Ollama，拔掉网线（或断 WiFi）
- [ ] 再跑一次 → **应该照常成功**，因为推理完全在本机
- [ ] 跑一次 OpenRouter（接回网线），断网 → **应该立刻失败**
- [ ] 这个实验最直观地告诉你「本地 vs 云端」的本质区别不是速度，是**数据是否离开你的机器**

### 阶段 E — 大小对比（可选）
- [ ] 同一个 prompt，本地 0.5B 模型 vs 云端大模型 → 你会看到本地小模型有时回答有点"傻"，但够用就行
- [ ] 这是为什么"边缘 AI"是真实需求：**为了隐私和成本，可以接受一些智力损失**

## 自检题

1. 我能不能让 Ollama 的服务监听 `0.0.0.0` 而不是 `localhost`，让局域网内别的设备也能用？这样安全吗？
2. 跑同样的 prompt，模型大小翻倍（0.5B → 1B → 3B），耗时大约怎么涨？是线性还是更猛？
3. 如果我电脑只有 8GB 内存，跑 7B 模型会发生什么？
4. Ollama 默认存模型在哪里？删一个模型该怎么操作？（提示：`ollama rm <name>`）

## 与其它仓库的连接

| 关系 | 仓库 | 为什么去看 |
| --- | --- | --- |
| **本地服务对照** | `api-lab-lmstudio-local-minimal` | LM Studio 是 GUI 启动的本地 OpenAI-compatible，跟 Ollama 是同一类问题的两种解法 |
| **协议 vs 服务** | `api-lab-openai-compatible-minimal` | 把 base_url 指向 Ollama 的兼容入口（`http://localhost:11434/v1`）就能复用——证明协议化 |
| **隐私 / 离线话题** | `api-lab-embedding-minimal` | embedding 也常常在本地跑（数据不出机器） |

## 你应该感受到的"啊哈"瞬间

- 当你**断网**还能跑通推理那一刻，你真正理解"本地模型"四个字。
- 当你看到 `/api/chat` 和 `/v1/chat/completions` 是两条路径，但 Ollama 同时支持——你理解了"原生协议"和"兼容协议"可以并存。
- 当你拿小模型回答的"还行但不太聪明"作为参考，看完之后再用云端大模型，**你会更尊重大模型为聪明所付出的代价**。
