# Omarchy Clip

A native Omarchy shell overlay: searchable clipboard history, All / Text / Images / Files / Pins filters, and a split preview with scrollable text, fitted images and hex color swatches. Uses the active menu theme.

Plugin id: `io.github.tuxclaw.clip` (kinds `overlay`, `bar-widget`). MIT. Does not replace stock `omarchy.clipboard` capture.

## Install

```sh
omarchy plugin add https://github.com/tuxclaw/clip.git --enable --yes
omarchy bar put io.github.tuxclaw.clip --section right --before omarchy.tray
```

Optional Super+Shift+V in `~/.config/hypr/bindings.lua`:

```lua
o.bind("SUPER + SHIFT + V", "Omarchy Clip", "omarchy-shell shell toggle io.github.tuxclaw.clip")
hl.layer_rule({ match = { namespace = "^omarchy-clip$" }, no_anim = true, animation = "none" })
```

## Remove

```sh
omarchy plugin disable io.github.tuxclaw.clip
omarchy plugin remove io.github.tuxclaw.clip --yes
```

Stock clipboard, Super+Ctrl+V, and the `wl-paste` watchers stay.

Toggle with **Super+Shift+V**, the **Clip** clipboard button in the bar, **Clip** in the installed-apps launcher, or `omarchy-shell shell toggle io.github.tuxclaw.clip`.

The header's **Clear all** button uses the same confirmation as Shift+Delete and is disabled when history is empty or unavailable, or a save is in progress.

| Input | Action |
|---|---|
| Type / Backspace / Ctrl+U | Search / edit filter |
| Up / Down, Page Up / Down | Move selection |
| Enter / Shift+Enter / Alt+Enter | Paste / copy / open |
| Delete / Shift+Delete | Remove / confirm clear |
| Ctrl+P / pin button | Pin or unpin |
| Tab / Shift+Tab | Cycle filters |
| Click / double-click entry | Preview / paste |
| Escape / click outside | Close |

`open(payloadJson)` accepts optional `query` and `filter` strings. `close()`, `toggle(payloadJson)` and a read-only `status()` are available through shell IPC.

History is watched through a read-only FileView at `~/.local/state/omarchy/clipboard-history.json`. Stock Omarchy owns capture. Only explicit delete/clear actions invoke `storage.py`, which rereads history and atomically replaces it using stock text/image objects. Clear targets its confirmation snapshot so new captures survive. Concurrent changes detected before replacement are retried; stock capture does not share a transaction lock, so simultaneous writes still have a narrow race window.

Pins are content identities in `~/.local/state/omarchy/clip-pins.json` (mode 0600). They survive reorder and restart, but do not extend stock history retention. Deleted or evicted entries disappear from Pins; copying identical content later restores its pin. Images remain owned by stock Omarchy. No remote preview requests are made. Preview text is capped at 64K characters; paste/copy uses the full stock entry. Type chips are heuristics. Files includes file URIs and absolute/home-relative paths.

Requires the installed Omarchy shell, Python 3 and existing `omarchy-clipboard-*` helpers. Run `python3 install.py` from this repo in the desktop session to validate, install, enable if needed, configure the shortcut/layer rule and collect evidence in `.context/validation.md`. Existing Clip bindings are left in place. It backs up changed user files and verifies the original two stock watchers, stock clipboard enablement and shortcut, Clip's namespace, and open/close IPC. It does not restart the shell.

The installer copies `BarWidget.qml` and `assets/` along with the overlay, adds Clip to `bar.layout.right` before `omarchy.tray` (falling back to index 0), and rescans plugins. Familiar hosts this layout through `omarchyWidgets`; no Familiar source changes are needed. It installs `assets/io.github.tuxclaw.clip.desktop` to `~/.local/share/applications/` and `assets/clip.svg` to `~/.local/share/icons/hicolor/scalable/apps/io.github.tuxclaw.clip.svg`. Desktop validation and icon/application cache refreshes run when their tools are available.

Development checks:

```sh
omarchy plugin validate .
python3 -m unittest discover -s tests -v
node tests/test_clip.cjs
/usr/lib/qt6/bin/qmlformat --normalize Overlay.qml > /tmp/clip-formatted.qml
```
