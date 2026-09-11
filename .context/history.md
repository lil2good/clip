## [2026-09-10] Project seeded
**Agent:** Sonic
**Branch:** none yet
**Changes:** Created repo dir and `.context/` after Tux said Go. Tails to implement overlay.
**Files:** `.context/decisions.md`, `.context/notes.md`
**Commit:** none

## [2026-09-10] Clip overlay implemented; installation blocked
**Agent:** Tails
**Branch:** `andy/clip-overlay` requested; creation blocked by read-only `.git` and rejected execution approval.
**Changes:** Built an overlay-only, keepLoaded native picker with watched history, sidecar pins, type/filter chips, split preview, keyboard actions, confirmation, stock helper activation, and a backup-aware installer with live acceptance checks.
**Files:** `manifest.json`, `Overlay.qml`, `Clip.js`, `storage.py`, `install.py`, `README.md`, `.gitignore`, `tests/test_storage.py`, `tests/test_clip.cjs`, `.context/validation.md`, `.context/history.md`.
**Validation:** Manifest and QML syntax pass; 5 storage tests and 8 JS checks pass. Runtime and install remain unverified. Both elevated command requests were rejected; no host files or watchers were changed. See `.context/validation.md` for exact limits.
**Commit:** none; no push.

## [2026-09-10] Live install after enable flag fix
**Agent:** Sonic
**Branch:** andy/clip-overlay
**Changes:** `omarchy plugin enable` has no `--yes`. Enabled plugin, bound Super+Shift+V, added `omarchy-clip` layer rule. Live toggle opened 34 entries; stock clipboard still enabled; watchers still stock capture.sh.
**Files:** `~/.config/omarchy/plugins/io.github.tuxclaw.clip/`, `~/.config/hypr/bindings.lua`
**Commit:** pending
