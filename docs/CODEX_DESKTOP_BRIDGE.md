# Codex Desktop Bridge

Use this document when a remote or mobile web UI must continue the current
Codex Desktop live thread.

This is not the same problem as running a second Codex SDK client.

## Core rule

If the requirement is "continue the same Codex Desktop conversation", do not
start an independent SDK session and do not treat session-file writes as
equivalent to the live desktop thread.

Use a desktop bridge:

- the web UI is the remote control surface
- the visible Codex Desktop window is the execution authority
- local Codex state and session files are the verification and replay sources

## What bridge mode is for

Use bridge mode when the user needs any of these:

- continue the current desktop thread from a phone, tablet, or another computer
- keep the remote UI and desktop app on the same real session
- create a desktop-backed `New Session` from the remote UI
- add a desktop-backed project from the remote UI
- open, preview, or download local files returned by Codex in that thread

Do not use bridge mode when the goal is simply "run Codex remotely" and live
thread continuity is not required. In that case, a normal remote client is
simpler.

## Authority model

Treat these layers differently:

### 1. Desktop-visible session is execution authority

The session currently selected in the Codex Desktop UI is the thread that will
actually receive input.

### 2. Local Codex state is metadata truth

Use the local Codex state directory for project and thread metadata, for
example:

- `%USERPROFILE%\\.codex\\state_*.sqlite`
- `%USERPROFILE%\\.codex\\session_index.jsonl`

### 3. Local session files are conversation truth

Use the session transcript files under:

- `%USERPROFILE%\\.codex\\sessions\\...`

for replay, verification, message recovery, and content fingerprints.

### 4. Web UI is a projection

The remote UI is not the authority. It must resync from desktop-backed sources
after send, complete, reconnect, or ambiguity.

## Existing-session routing rule

When sending to an existing session:

1. identify the target project and target session in the remote UI
2. locate the same project in the desktop sidebar
3. limit candidate matching to the target project's sidebar band
4. collect near-title candidates only inside that band
5. click a candidate, but do not send yet
6. verify the selection using:
   - header text
   - recent content fingerprint from the real session file
7. send only after the candidate is confirmed

Never send based only on:

- global prefix matching
- a guessed project label
- a successful click without post-click validation

## New session sync rule

If the remote UI offers `New Session` and the expectation is desktop sync:

1. create the session through the desktop bridge
2. capture the real created thread from desktop-backed state
3. bind the remote route to that real thread id
4. send the first message only after that binding is confirmed

Do not expose a fake new-session action that creates only a web-local route.

## New project sync rule

If the remote UI offers `Add project` and the expectation is desktop sync:

1. add the project through the desktop-backed flow
2. confirm the new project exists in desktop-backed state
3. only then expose it as a selectable project in the remote UI

If the flow cannot create a real desktop-backed project, do not pretend it did.

## Local file access rule

For files returned by Codex:

- do not expose raw local paths directly as unauthenticated web links
- proxy file reads through a local authenticated endpoint
- validate the requested path before serving it
- support both text preview and binary download

Success is not "the link exists". Success is:

- the remote UI can actually open or download the file
- the content matches the local source

## Frontend state reconciliation rule

Bridge mode must not rely only on optimistic UI or websocket deltas.

Required behavior:

- after `codex-complete`, reload the current session from source
- after websocket reconnect, reload the current session from source
- sync display messages by content signature, not only by message count

This prevents half-states such as:

- user message appears but assistant reply disappears
- new message arrives but the thread view clears until refresh
- avatar grouping or message order breaks after reconnect

## Failure handling

If session selection is ambiguous:

- do not blindly send
- increase validation depth
- prefer a slower verified path over a fast wrong send

If the desktop bridge cannot prove the selected session:

- fail the send explicitly
- keep the remote UI state intact

If the web UI and the desktop thread diverge:

- resync from real session sources
- do not trust the remote UI's local cache

## Anti-patterns

Do not treat these as acceptable solutions:

- starting an independent Codex SDK session and calling it "the same thread"
- writing or mutating session files and assuming the desktop live thread
  followed
- prefix-matching session titles across the whole sidebar
- using the remote UI's optimistic state as the final truth
- calling file upload "working" because one HTTP request returned `200`

## Acceptance checklist

Bridge mode is only correct if all of these are true:

1. a remote send enters the intended desktop live thread
2. the desktop reply appears back in the same remote thread
3. same-project near-title sessions do not misroute
4. remote `New Session` creates a real desktop-backed session
5. remote `Add project` creates or exposes a real desktop-backed project
6. local files returned by Codex can be opened or downloaded remotely
7. refresh is not required to recover ordinary message visibility after each
   send

## Reference implementation

The public reference implementation for this pattern lives in:

- `tools/mobile-codex-desktop-bridge/`

Use that implementation as the starting point if you need a desktop-backed
remote control surface for Codex Desktop.

## Bottom line

Bridge mode is not a fourth execution lane.

It is a control surface that lets a remote UI drive the current Codex Desktop
thread while still obeying the normal browser, desktop, and dynamic routing
model underneath.
