# Agent Control Panel

This repository includes a reusable operator dashboard under:

- `tools/agent-control-panel/`

Preview:

![Agent Control Panel preview](./agent-control-panel-preview.png)

It exists to solve a common problem across local agent stacks: the runtime is
powerful, but too much of it is hidden in config files, skills, shell scripts,
and machine-local conventions.

## What the tool does

The control panel provides:

- a polished static web UI
- a shared snapshot schema
- a Codex adapter that can build a panel from a local Codex stack
- a Claude Code-friendly adapter that can render the same UI from config

## Publishing rule

This repository publishes:

- the UI
- the schema
- the adapters
- the operator documentation

It should not publish stale private machine snapshots as if they were generic
artifacts.

## Compatibility goal

The tool should feel useful to:

- Codex users
- Claude Code users
- teams building adjacent local-agent stacks

That means:

- generic labels where possible
- agent-specific behavior in adapters
- readable docs before source-diving

## Relationship to the original machine-local panel

The original panel was built for one Windows machine and one Codex stack. This
tool extracts the durable parts of that work and republishes them as a portable
utility instead of a machine-specific dashboard dump.
