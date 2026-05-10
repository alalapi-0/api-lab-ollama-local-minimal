"""api-lab-ollama-local-minimal

调用本机 Ollama 服务跑一次最小推理。

要求：
- 本机已安装 Ollama，且 ollama 服务在监听 11434
- 本机已经 ollama pull 过某个模型，并把名字填进 .env 的 OLLAMA_MODEL

本仓库故意不自动 pull 模型，避免乱占磁盘和带宽。
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROMPT = "请用两句话解释本地模型和云端模型的区别。"
TIMEOUT_SECONDS = 30
NUM_PREDICT = 80


def check_server(base_url: str) -> bool:
    """先 ping 一下 ollama 服务是否可达。"""
    try:
        # /api/tags 列出本机已 pull 的模型，是个轻量 GET
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def main() -> int:
    load_dotenv()

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "").strip()

    if not model:
        print("[错误] 未在 .env 中检测到 OLLAMA_MODEL。")
        print("       请先执行: cp .env.example .env")
        print("       然后用 `ollama list` 看本机已 pull 的模型，把模型名填进 .env。")
        return 2

    print(f"[信息] 检测 Ollama 服务: {base_url}")
    if not check_server(base_url):
        print("[失败] 无法连接到 Ollama 服务。")
        print("       1) 确认本机已安装 Ollama: https://ollama.com/download")
        print("       2) 确认服务已启动: macOS 通常打开 Ollama 应用即可，或运行 `ollama serve`")
        print("       3) 检查 OLLAMA_BASE_URL 是否对（默认 http://localhost:11434）")
        return 1
    print("[信息] Ollama 服务可达。")

    url = f"{base_url}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
        "options": {"num_predict": NUM_PREDICT},
    }

    print(f"[信息] endpoint = {url}")
    print(f"[信息] model    = {model}")
    print(f"[信息] prompt   = {PROMPT}")

    started = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        print(f"[失败] 请求超时（{TIMEOUT_SECONDS}s）。本地小模型偶尔很慢，但这里设了上限。")
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"[失败] 网络请求异常: {exc}")
        return 1
    elapsed = time.time() - started

    if resp.status_code != 200:
        print(f"[失败] HTTP {resp.status_code}")
        print(f"        响应片段: {resp.text[:300]}")
        if resp.status_code == 404 and model:
            print(f"        提示：本机可能没 pull 过 `{model}`。运行 `ollama list` 查可用模型。")
        return 1

    try:
        data = resp.json()
        content = data["message"]["content"]
    except (ValueError, KeyError, TypeError):
        print("[失败] 响应结构与 Ollama /api/chat 预期不符。")
        print(f"        原始响应片段: {resp.text[:300]}")
        return 1

    print()
    print("[成功] 模型返回内容：")
    print(content)
    print()
    print(f"[信息] 耗时 {elapsed:.2f}s（含本地推理）")

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    result = {
        "provider": "ollama-local",
        "base_url": base_url,
        "model": model,
        "prompt": PROMPT,
        "elapsed_seconds": round(elapsed, 3),
        "content": content,
    }
    out_file = out_dir / "result.json"
    out_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[信息] 已写入 {out_file}（不会被 git 提交）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
