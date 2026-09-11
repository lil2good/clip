## [2026-09-10] Omarchy clipboard internals
**By:** Sonic

Stock plugin: `/usr/share/omarchy/shell/plugins/clipboard/`
- `Clipboard.qml` overlay + watchers
- `ClipboardHistory.js` schema/normalize/search
- `capture.sh` used only by stock watchers

Stock helpers (on PATH):
- `/usr/bin/omarchy-clipboard-paste-text`
- `/usr/bin/omarchy-clipboard-paste-file`
- `/usr/bin/omarchy-clipboard-open`
- `/usr/bin/omarchy-menu-clipboard` → `omarchy-shell shell toggle omarchy.clipboard`

Watchers (do not touch):
- `wl-paste --type text --watch .../clipboard/capture.sh text`
- `wl-paste --type image/png --watch .../clipboard/capture.sh image/png`

History schema (text): `{ "type": "text", "text": "..." }`
History schema (image): `{ "type": "image", "path": "...", "mime": "image/png", "capturedAt": "..." }`
Limit 300 in QML; display prefix 50 rows; text display cap 8192 chars.

Native overlay references:
- `/usr/share/omarchy/shell/plugins/clipboard/Clipboard.qml`
- `/usr/share/omarchy/shell/plugins/emojis/Emojis.qml`
- `/usr/share/omarchy/shell/README.md` plugin manifest + IPC
- Third-party overlay example: `~/.config/omarchy/plugins/io.github.tuxclaw.familiar/Overlay.qml`

ACP note: no `/var/home/tux` on this host. Project cwd is `/home/tux/Documents/Projects/omarchy-clip`. acpx `permissionMode` is `approve-reads` (not approve-all).
