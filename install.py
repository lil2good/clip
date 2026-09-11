import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
PLUGIN = "io.github.tuxclaw.clip"
HOME_DIR = Path.home()
STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
REPORT = []


def run(*args, show=True):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)
    output = result.stdout.strip()
    if show:
        message = "$ " + " ".join(args) + "\n" + (output or "exit 0 (no output)")
        print(message, flush=True)
        REPORT.append(message)
    return output


def backup(path):
    if path.exists():
        destination = path.with_name(path.name + ".clip-backup-" + STAMP)
        shutil.copy2(path, destination)
        REPORT.append("Backup: " + str(destination))


def watchers():
    values = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            args = (entry / "cmdline").read_bytes().split(b"\0")
        except (OSError, PermissionError):
            continue
        if args and args[0].split(b"/")[-1] == b"wl-paste":
            values.append((int(entry.name), b" ".join(args).decode().strip()))
    return sorted(values)


def check_watchers(values):
    assert len(values) == 2, "Expected exactly two stock wl-paste watchers"
    assert all("/shell/plugins/clipboard/capture.sh" in command for _, command in values)
    assert any("--type text --watch" in command for _, command in values)
    assert any("--type image/png --watch" in command for _, command in values)


def main():
    run("omarchy", "plugin", "validate", str(ROOT))
    run("omarchy-shell", "shell", "ping")
    initial_watchers = watchers()
    check_watchers(initial_watchers)
    bindings_before = run("omarchy", "menu", "keybindings", "--print", show=False)
    conflicts = [line for line in bindings_before.splitlines()
                 if "SUPER" in line.split("→")[0] and "SHIFT" in line.split("→")[0]
                 and line.split("→")[0].strip().endswith("+ V")]
    REPORT.append("Prior Super+Shift+V: " + ("\n".join(conflicts) or "unbound"))
    print(REPORT[-1], flush=True)
    if not (ROOT / ".git/HEAD").exists():
        run("git", "init", "-b", "andy/clip-overlay")
    elif run("git", "branch", "--show-current", show=False) != "andy/clip-overlay":
        exists = subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/andy/clip-overlay"], cwd=ROOT).returncode == 0
        run("git", "switch", "andy/clip-overlay") if exists else run("git", "switch", "-c", "andy/clip-overlay")
    destination = HOME_DIR / ".config/omarchy/plugins" / PLUGIN
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ("manifest.json", "Overlay.qml", "Clip.js", "storage.py", "README.md"):
        backup(destination / filename)
        shutil.copy2(ROOT / filename, destination / filename)
    run("omarchy", "plugin", "validate", str(destination))
    run("omarchy-shell", "shell", "rescanPlugins")
    run("omarchy", "plugin", "enable", PLUGIN, "--yes")
    bindings = HOME_DIR / ".config/hypr/bindings.lua"
    original = bindings.read_text()
    marker = '-- Omarchy Clip\n'
    if marker not in original:
        backup(bindings)
        addition = "\n" + marker
        if conflicts:
            addition += 'hl.unbind("SUPER + SHIFT + V")\n'
        addition += 'o.bind("SUPER + SHIFT + V", "Omarchy Clip", "omarchy-shell shell toggle io.github.tuxclaw.clip")\n'
        addition += 'hl.layer_rule({ match = { namespace = "^omarchy-clip$" }, no_anim = true, animation = "none" })\n'
        bindings.write_text(original + addition)
    run("hyprctl", "reload")
    errors = run("hyprctl", "configerrors")
    if errors:
        bindings.write_text(original)
        run("hyprctl", "reload")
        raise RuntimeError("Hyprland errors; restored original bindings: " + errors)
    run("omarchy-shell", "shell", "ping")
    plugins = json.loads(run("omarchy", "plugin", "list", "--json", show=False))
    for identifier in (PLUGIN, "omarchy.clipboard"):
        assert any(p["id"] == identifier and p["enabled"] for p in plugins), identifier + " is not enabled"
    listing = run("omarchy", "plugin", "list", show=False)
    REPORT.extend(line for line in listing.splitlines() if PLUGIN in line or "omarchy.clipboard " in line)
    after = run("omarchy", "menu", "keybindings", "--print", show=False)
    relevant = [line for line in after.splitlines() if "SUPER" in line.split("→")[0] and line.split("→")[0].strip().endswith("+ V")]
    REPORT.extend(relevant)
    assert any("SHIFT" in line and "Omarchy Clip" in line for line in relevant), "Clip binding missing"
    stock_before = [line for line in bindings_before.splitlines() if "SUPER" in line.split("→")[0] and "CTRL" in line.split("→")[0] and line.split("→")[0].strip().endswith("+ V")]
    assert stock_before and all(line in after for line in stock_before), "Stock clipboard binding changed"
    run("omarchy-shell", "shell", "hide", PLUGIN)
    run("omarchy-shell", "shell", "toggle", PLUGIN)
    try:
        time.sleep(0.5)
        status = json.loads(run("omarchy-shell", "shell", "call", PLUGIN, "status", ""))
        assert status["opened"], "Overlay did not open"
        layers = run("hyprctl", "layers", "-j", show=False)
        assert 'omarchy-clip"' in layers, "Overlay layer is missing"
        REPORT.append("Layer namespace omarchy-clip: present")
    finally:
        run("omarchy-shell", "shell", "hide", PLUGIN)
    status = json.loads(run("omarchy-shell", "shell", "call", PLUGIN, "status", ""))
    assert not status["opened"], "Overlay did not close"
    final_watchers = watchers()
    check_watchers(final_watchers)
    assert final_watchers == initial_watchers, "Clipboard watcher processes changed"
    REPORT.append("Watchers unchanged:\n" + "\n".join(str(pid) + " " + command for pid, command in final_watchers))
    print("\n".join(REPORT[-12:]), flush=True)


if __name__ == "__main__":
    try:
        main()
    finally:
        (ROOT / ".context/validation.md").write_text("# Clip validation\n\n```text\n" + "\n\n".join(REPORT) + "\n```\n")
