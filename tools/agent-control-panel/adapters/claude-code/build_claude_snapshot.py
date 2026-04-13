from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a portable Agent Control Panel snapshot for Claude Code from a JSON config.")
    parser.add_argument("--config", required=True, help="Path to the JSON config file")
    parser.add_argument("--output-dir", required=True, help="Directory where panel-data.json and panel-data.js should be written")
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    meta = dict(payload.get("meta", {}))
    meta.setdefault("title", "Agent Control Panel")
    meta.setdefault("subtitle", "Portable operator dashboard for Claude Code and adjacent local-agent stacks.")
    meta.setdefault("agentFamily", "Claude Code")
    meta.setdefault("generatedAt", datetime.now().astimezone().isoformat(timespec="seconds"))
    payload["meta"] = meta
    for key in ["status", "lanes", "principles", "prompts", "helpers", "skills", "parameters", "docs", "adapters"]:
        payload.setdefault(key, [])
    return payload


def write_outputs(output_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "panel-data.json"
    js_path = output_dir / "panel-data.js"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    js_path.write_text("window.AgentControlPanelData = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
    return json_path, js_path


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    payload = normalize_payload(load_config(config_path))
    json_path, js_path = write_outputs(output_dir, payload)
    print(json.dumps({"ok": True, "json": str(json_path), "js": str(js_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
