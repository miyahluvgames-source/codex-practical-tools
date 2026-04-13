# Agent Control Panel Schema

The web UI reads a single JavaScript global:

- `window.AgentControlPanelData`

The same content may also be written as JSON for tooling and diffing.

## Top-level shape

```json
{
  "meta": {},
  "status": [],
  "lanes": [],
  "principles": [],
  "prompts": [],
  "helpers": [],
  "skills": [],
  "parameters": [],
  "docs": [],
  "adapters": []
}
```

## `meta`

General page metadata.

Recommended fields:

- `title`
- `subtitle`
- `agentFamily`
- `generatedAt`
- `stackRoot`
- `backupRoot`
- `operatorNote`

## `status`

Top-level operator summary cards.

Each item should look like:

```json
{
  "label": "Browser lane",
  "value": "Healthy",
  "tone": "good"
}
```

Recommended `tone` values:

- `good`
- `warn`
- `neutral`

## `lanes`

Execution-lane definitions.

Each item should look like:

```json
{
  "name": "Browser-native lane",
  "summary": "Primary DOM route.",
  "useWhen": ["..."],
  "escalateWhen": "..."
}
```

## `principles`

Flat list of routing and validation rules.

Each item:

```json
{
  "title": "Visible truth wins",
  "body": "If the tool says success but the screen does not, trust the screen."
}
```

## `prompts`

Startup or handoff prompt inventory.

Each item:

```json
{
  "title": "Codex-only startup prompt",
  "summary": "Use for local Codex sessions.",
  "body": "Full prompt text..."
}
```

## `helpers`

Operator-facing helper atlas.

Each item:

```json
{
  "name": "resolve-file-picker.ps1",
  "lane": "desktop",
  "summary": "Stable handler for Windows file dialogs.",
  "path": "C:\\path\\to\\script",
  "exists": true
}
```

## `skills`

Installed or available skills.

Each item:

```json
{
  "name": "browser-failsafe-rescue",
  "summary": "Recover from browser stalls and native blockers.",
  "path": "C:\\path\\to\\SKILL.md",
  "group": "installed"
}
```

## `parameters`

Grouped runtime parameters.

Each item:

```json
{
  "group": "Runtime",
  "items": [
    { "label": "Model", "value": "gpt-5" }
  ]
}
```

## `docs`

Primary source documents.

Each item:

```json
{
  "title": "AGENT_BOOTSTRAP.md",
  "summary": "Machine capability map.",
  "path": "C:\\path\\to\\file"
}
```

## `adapters`

Notes about the adapter that produced the snapshot.

Each item:

```json
{
  "name": "Codex adapter",
  "summary": "Builds a snapshot from a local Codex stack."
}
```

## Compatibility rule

Do not hardwire the web UI to one agent brand. Agent-specific logic belongs in
the snapshot builder or config source.
