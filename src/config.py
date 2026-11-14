"""读取项目 .env 并给出路径常量。不依赖第三方 dotenv。"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RUNS = ROOT / "runs"


def load_env() -> None:
    for p in [ROOT / ".env", *ROOT.parents]:
        f = p / ".env" if p.is_dir() else p
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
        break


def model_conf() -> dict:
    load_env()
    return {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    }


def make_model(temperature: float = 0.0, max_tokens: int = 2048):
    from langchain_openai import ChatOpenAI

    c = model_conf()
    return ChatOpenAI(
        model=c["model"], base_url=c["base_url"], api_key=c["api_key"],
        temperature=temperature, max_tokens=max_tokens, timeout=120, max_retries=1,
        streaming=True, stream_usage=True,
    )
