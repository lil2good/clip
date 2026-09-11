# Omarchy Clip

A native Omarchy shell overlay: searchable clipboard history, All / Text / Images / Files / Pins filters, and a split preview with scrollable text, fitted images and hex color swatches. Uses the active menu theme.

Toggle with **Super+Shift+V** or `omarchy-shell shell toggle io.github.tuxclaw.clip`.

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

Requires the installed Omarchy shell, Python 3 and existing `omarchy-clipboard-*` helpers. Run `python3 install.py` from this repo in the desktop session to validate, install, enable, configure the shortcut/layer rule and collect evidence in `.context/validation.md`. It backs up changed user files and verifies the original two stock watchers, stock clipboard enablement and shortcut, Clip's namespace, and open/close IPC. It does not restart the shell.

Development checks:

```sh
omarchy plugin validate .
python3 -m unittest discover -s tests -v
node tests/test_clip.cjs
/usr/lib/qt6/bin/qmlformat --normalize Overlay.qml > /tmp/clip-formatted.qml
```
