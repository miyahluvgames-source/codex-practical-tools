from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a portable Agent Control Panel snapshot from a local Codex stack.")
    parser.add_argument("--stack-root", required=True, help="Local Codex stack root, for example C:\\path\\to\\your\\stack")
    parser.add_argument("--output-dir", required=True, help="Directory where panel-data.json and panel-data.js should be written")
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"), help="Codex home directory. Defaults to ~/.codex")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None or not path.exists():
        return {}
    return tomllib.loads(read_text(path))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(read_text(path))


def parse_markdown_sections(text: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append({"title": current_title, "body": "\n".join(current_lines).strip()})
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append({"title": current_title, "body": "\n".join(current_lines).strip()})
    return sections


def extract_section(path: Path, title: str) -> str:
    for section in parse_markdown_sections(read_text(path)):
        if section["title"] == title:
            return section["body"]
    return ""


def extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("- "):
            if current:
                bullets.append(current.strip())
            current = line[2:].strip()
            continue
        if current and (raw_line.startswith("  ") or raw_line.startswith("\t")):
            current += " " + line.strip()
            continue
        if current and not line.strip():
            bullets.append(current.strip())
            current = None

    if current:
        bullets.append(current.strip())
    return bullets


def collect_skills(codex_home: Path) -> list[dict[str, str]]:
    skills: list[dict[str, str]] = []
    for skill_file in sorted((codex_home / "skills").glob("**/SKILL.md")):
        name = skill_file.parent.name
        summary = ""
        text = read_text(skill_file)
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                header = parts[1]
                for line in header.splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"')
                    elif line.startswith("description:"):
                        summary = line.split(":", 1)[1].strip()
        if not summary:
            for line in text.splitlines():
                if line.strip() and not line.startswith("#") and not line.startswith("---"):
                    summary = line.strip()
                    break
        skills.append(
            {
                "name": name,
                "summary": summary or "No description found.",
                "group": "system" if ".system" in str(skill_file) else "installed",
                "path": str(skill_file),
            }
        )
    return skills


def collect_prompts(stack_root: Path) -> list[dict[str, str]]:
    prompt_path = stack_root / "docs" / "STARTUP_PROMPTS.md"
    if not prompt_path.exists():
        return []

    prompts: list[dict[str, str]] = []
    for section in parse_markdown_sections(read_text(prompt_path)):
        if not section["title"].lower().endswith("startup prompt") and "supplement" not in section["title"].lower():
            continue
        prompts.append(
            {
                "title": section["title"],
                "summary": section["body"].splitlines()[0].strip() if section["body"] else "",
                "body": section["body"],
            }
        )
    return prompts


def collect_helpers(stack_root: Path) -> list[dict[str, Any]]:
    helper_names = [
        ("codex-browser-preflight.ps1", "browser", "Preflight before the first serious browser action."),
        ("codex-browser-stall-rescue.ps1", "browser", "First rescue step after browser no-op, timeout, or native-blocker symptoms."),
        ("codex-browser-visual-audit.ps1", "browser", "Desktop-visible-state audit when browser results disagree with the screen."),
        ("resolve-chrome-prompt.ps1", "browser", "Handles native Chrome allow or block prompts."),
        ("resolve-file-picker.ps1", "desktop", "Handles Windows Open and Save dialogs."),
        ("desktop-relative-click.ps1", "desktop", "Relative clicking for weak-UIA windows."),
        ("desktop-stable-input.ps1", "desktop", "Clipboard-backed verified text input."),
        ("desktop-dismiss-overlays.ps1", "desktop", "Dismisses or classifies overlay blockers."),
        ("game_prepare_window.py", "dynamic", "Normalizes windows before dynamic capture."),
        ("dynamic_surface_collect_browser_sample.py", "dynamic", "Collects geometry samples for browser-aware dynamic surfaces."),
        ("dynamic_surface_browser_pipeline.py", "dynamic", "Single-entry browser-aware dynamic escalation path."),
        ("dynamic_surface_pipeline.py", "dynamic", "General dynamic surface pipeline."),
        ("game_realtime_probe.py", "dynamic", "Dynamic-lane probe for capture and hit loops."),
        ("game_continuous_controller.py", "dynamic", "Persistent watch-think-act controller."),
        ("bootstrap-session-project.ps1", "ops", "Forks the main stack into an isolated project stack."),
        ("sync-agent-foundation.ps1", "ops", "Refreshes the D-drive backup."),
    ]

    helpers: list[dict[str, Any]] = []
    for name, lane, summary in helper_names:
      path = stack_root / "scripts" / name
      helpers.append(
          {
              "name": name,
              "lane": lane,
              "summary": summary,
              "path": str(path),
              "exists": path.exists(),
          }
      )
    return helpers


def collect_docs(stack_root: Path) -> list[dict[str, str]]:
    items = [
        ("AGENTS.md", "Top-level operating rules for new sessions.", stack_root / "AGENTS.md"),
        ("AGENT_BOOTSTRAP.md", "Machine capability map and proven operating facts.", stack_root / "AGENT_BOOTSTRAP.md"),
        ("UNIVERSAL_COMPUTER_AUTOMATION.md", "Top-level routing model across browser, desktop, and dynamic lanes.", stack_root / "docs" / "UNIVERSAL_COMPUTER_AUTOMATION.md"),
        ("BROWSER_FAILSAFE_MODE.md", "Browser stall, native blocker, and visual-audit rules.", stack_root / "docs" / "BROWSER_FAILSAFE_MODE.md"),
        ("WINDOWS_DESKTOP_CONTROL.md", "Desktop-control rules, weak-UIA tactics, and verified input guidance.", stack_root / "docs" / "WINDOWS_DESKTOP_CONTROL.md"),
        ("GAME_AUTOMATION.md", "Dynamic-control lane guidance for motion-heavy surfaces.", stack_root / "docs" / "GAME_AUTOMATION.md"),
        ("STARTUP_PROMPTS.md", "Canonical startup prompt pack for local sessions.", stack_root / "docs" / "STARTUP_PROMPTS.md"),
        ("SESSION_PROJECT_ISOLATION.md", "Rules for forking project-local stacks without polluting the main stack.", stack_root / "docs" / "SESSION_PROJECT_ISOLATION.md"),
    ]
    docs = []
    for title, summary, path in items:
        docs.append({"title": title, "summary": summary, "path": str(path)})
    return docs


def build_snapshot(stack_root: Path, codex_home: Path) -> dict[str, Any]:
    config = load_toml(codex_home / "config.toml")
    mcp_config = load_json(stack_root / ".mcp.json")
    principles = extract_bullets(extract_section(stack_root / "AGENTS.md", "Current Default"))
    prompt_path = stack_root / "docs" / "STARTUP_PROMPTS.md"
    startup_note = extract_section(prompt_path, "Critical local browser-stall note") if prompt_path.exists() else ""

    mcp_items = []
    for name, server in config.get("mcp_servers", {}).items():
        mcp_items.append({"label": name, "value": str(server.get("command") or server.get("url", "built-in"))})
    for name, server in mcp_config.get("mcpServers", {}).items():
        mcp_items.append({"label": f".mcp.json:{name}", "value": str(server.get("command", server.get("type", "unknown")))})

    return {
        "meta": {
            "title": "Agent Control Panel",
            "subtitle": "Portable operator view generated from a local Codex stack.",
            "agentFamily": "Codex",
            "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
            "stackRoot": str(stack_root),
            "backupRoot": "D:\\AI-Agent-Backups\\Agent-Foundation",
            "operatorNote": startup_note or "Use browser DOM first, desktop as visible truth, and dynamic control only when normal automation is too static.",
        },
        "status": [
            {"label": "Browser lane", "value": "Configured", "tone": "good", "note": "Primary DOM route remains the default."},
            {"label": "Desktop lane", "value": "Configured", "tone": "good", "note": "Native UI and visible-truth layer."},
            {"label": "Dynamic lane", "value": "Configured", "tone": "neutral", "note": "Escalation path for motion and timing-sensitive work."},
            {"label": "Skills", "value": str(len(collect_skills(codex_home))), "tone": "neutral", "note": "Installed local skills currently visible to Codex."},
        ],
        "lanes": [
            {
                "name": "Browser-native lane",
                "accent": "browser",
                "summary": "Use the browser DOM tooling while the page remains healthy and the task stays inside the webpage surface.",
                "useWhen": [
                    "DOM reads, form work, navigation, standard clicks, and scroll operations.",
                    "Default route when no native blocker is present."
                ],
                "escalateWhen": "Escalate when native browser UI, file pickers, no-op actions, or visible-state mismatches appear.",
            },
            {
                "name": "Desktop-control lane",
                "accent": "desktop",
                "summary": "Use the desktop lane when native UI, browser chrome, weak-UIA apps, or visible truth matter more than DOM state.",
                "useWhen": [
                    "Native browser prompts, file pickers, system dialogs, and weak-UIA desktop surfaces.",
                    "Final acceptance when the visible result is easier to verify than internal state."
                ],
                "escalateWhen": "Escalate again only when the target is moving, animated, drag-validated, or timing-sensitive.",
            },
            {
                "name": "Dynamic-control lane",
                "accent": "dynamic",
                "summary": "Use the dynamic lane for moving, animated, or short-window interactions that static screenshot reasoning cannot keep up with.",
                "useWhen": [
                    "Canvas surfaces, drag validation, game-like UI, or burst timing windows.",
                    "Only after the browser or normal desktop lane is too static for the task."
                ],
                "escalateWhen": "Drop back to the browser or desktop lane as soon as a cheaper route is healthy again.",
            },
        ],
        "principles": [{"title": f"Rule {index + 1}", "body": item} for index, item in enumerate(principles)],
        "prompts": collect_prompts(stack_root),
        "helpers": collect_helpers(stack_root),
        "skills": collect_skills(codex_home),
        "parameters": [
            {
                "group": "Runtime",
                "items": [
                    {"label": "Model", "value": str(config.get("model", "unknown"))},
                    {"label": "Reasoning", "value": str(config.get("model_reasoning_effort", "unknown"))},
                    {"label": "Personality", "value": str(config.get("personality", "unknown"))},
                ],
            },
            {
                "group": "MCP",
                "items": mcp_items or [{"label": "MCP", "value": "No MCP entries found"}],
            },
            {
                "group": "Paths",
                "items": [
                    {"label": "Codex home", "value": str(codex_home)},
                    {"label": "Stack root", "value": str(stack_root)},
                    {"label": "Startup prompts", "value": str(stack_root / "docs" / "STARTUP_PROMPTS.md")},
                ],
            },
        ],
        "docs": collect_docs(stack_root),
        "adapters": [
            {
                "name": "Codex adapter",
                "summary": "Reads a local Codex stack, installed skills, and config files to build the panel snapshot.",
                "path": str(Path(__file__).resolve()),
            },
            {
                "name": "Claude Code adapter",
                "summary": "Uses a JSON config to render the same panel structure for Claude Code or similar stacks.",
                "path": str(Path(__file__).resolve().parents[1] / "claude-code" / "build_claude_snapshot.py"),
            },
        ],
    }


def write_outputs(output_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "panel-data.json"
    js_path = output_dir / "panel-data.js"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    js_path.write_text("window.AgentControlPanelData = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n", encoding="utf-8")
    return json_path, js_path


def main() -> None:
    args = parse_args()
    stack_root = Path(args.stack_root).expanduser().resolve()
    codex_home = Path(args.codex_home).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    payload = build_snapshot(stack_root, codex_home)
    json_path, js_path = write_outputs(output_dir, payload)
    print(json.dumps({"ok": True, "json": str(json_path), "js": str(js_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
