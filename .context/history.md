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

## [2026-09-10] Clear all and launchers prepared; live installation blocked
**Agent:** Tails
**Branch:** `andy/clip-overlay`
**Changes:** Added a visible header Clear all button using Pin's chrome and existing requestClear/ConfirmDialog; disabled for empty/unavailable history and pending saves. Shift+Delete is unchanged. Added overlay+bar-widget manifest, stock WidgetButton clipboard glyph and Clip tooltip, desktop launcher and monochrome SVG. Installer now ships the new files/assets, skips enable when already enabled, drops unsupported --yes, places Clip before the right tray with index-0 fallback, installs desktop/icon and refreshes available caches. Existing Hyprland bindings are not reloaded or changed on repeat install.
**Validation:** Repository manifest, both QML syntax checks, desktop-file-validate, 5 storage tests and 8 JS checks passed. Live installer execution was rejected by the approval system (reported as "rejected by user"); it did not run. Live acceptance for Clear all, Familiar button, app list and watcher identity remains pending. No installed plugin, Familiar, packaged Omarchy, Hyprland or capture watcher changes were made in this turn.
**Commit:** Blocked: elevated git add/commit was also rejected by the approval system (reported as "rejected by user"). Changes remain in the working tree on `andy/clip-overlay`; the pre-existing decisions.md edit was preserved. No push.
