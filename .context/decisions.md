## [2026-09-10] Additive native Clip overlay
**By:** Sonic
**Context:** Tux asked to inspect Omarchy clipboard and build the nicest Linux clipboard GUI. Then: do not replace anything; must work with Omarchy and feel native.
**Decision:** New third-party overlay plugin `io.github.tuxclaw.clip`. Stock `omarchy.clipboard` stays enabled and owns capture. Clip is a nicer picker over the same store.
**Alternatives considered:** Clone/disable `omarchy.clipboard` (rejected). Standalone CopyQ/Panox/clp/Qt app (rejected — fights watchers, looks foreign).
**Status:** Active

Hard rules:
- Do not edit `/usr/share/omarchy/`
- Do not clone, disable, or replace `omarchy.clipboard`
- Do not start `wl-paste`, `pkill` clipboard watchers, or run `capture.sh`
- Do not write extra fields into `clipboard-history.json` (stock `saveHistory` would strip them)
- Do not steal Super+Ctrl+V, Super+C, Super+V, Super+X

Contract:
- **Id:** `io.github.tuxclaw.clip`
- **Kind:** `overlay` only
- **keepLoaded:** `true` for snappy toggle (no capture processes)
- **History (read-only):** `$HOME/.local/state/omarchy/clipboard-history.json`
- **Images:** `$HOME/.local/state/omarchy/clipboard-images/`
- **Pins sidecar:** `$HOME/.local/state/omarchy/clip-pins.json`
- **Paste text:** `omarchy-clipboard-paste-text --shift-insert --history-index N`
- **Copy text:** `omarchy-clipboard-paste-text --copy-only --history-index N`
- **Paste image:** `omarchy-clipboard-paste-file <mime> <path>`
- **Copy image:** `omarchy-clipboard-paste-file --copy-only <mime> <path>`
- **Open:** `omarchy-clipboard-open --history-index N`
- **Toggle IPC:** `omarchy-shell shell toggle io.github.tuxclaw.clip`
- **Bind:** Super+Shift+V in `~/.config/hypr/bindings.lua` after checking `omarchy menu keybindings --print`
- **Namespace:** `omarchy-clip` plus a user Hyprland layer_rule `no_anim` (do not edit packaged `omarchy-shell.lua`)
- **Theme:** `Color.menu`, `Style`, `BorderSurface`, same type-to-filter grammar as `omarchy.clipboard` / `omarchy.emojis`

V1 UI:
- Split list + preview (stock already has this; make preview actually good)
- Heuristic type chips: text / url / path / image / color — derived, not stored
- Filter row: All · Text · Images · Files · Pins
- Pin/unpin (sidecar only)
- Footer: Enter paste · Shift+Enter copy · Alt+Enter open · Del remove · Shift+Del clear (same confirm as stock). Deletes rewrite `clipboard-history.json` in the stock schema only (text/image objects). Pin/unpin stays in the sidecar.
- Esc closes; type-to-filter; Up/Down; click scrim closes
- Exclusive keyboard focus overlay

Install:
- Source of truth: this repo
- Drop-in: `~/.config/omarchy/plugins/io.github.tuxclaw.clip/`
- `omarchy plugin validate`, `omarchy-shell shell rescanPlugins`, `omarchy plugin enable io.github.tuxclaw.clip --yes`
- Branch `andy/clip-overlay`; never push `main`
