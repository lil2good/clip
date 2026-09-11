import datetime
import json
from pathlib import Path
import shutil
import subprocess
import time

from safe_io import atomic_write, ensure_directory, read_bytes

MAX_CONFIG_BYTES = 1024 * 1024
MAX_ASSET_BYTES = 16 * 1024 * 1024

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
    try:
        data = read_bytes(path, MAX_CONFIG_BYTES)
    except FileNotFoundError:
        return
    destination = path.with_name(path.name + ".clip-backup-" + STAMP)
    atomic_write(destination, data)
    REPORT.append("Backup: " + str(destination))


def install_file(source, target):
    data = read_bytes(source, MAX_ASSET_BYTES)
    atomic_write(target, data, mode=source.stat().st_mode & 0o777)


def write_text(path, text):
    atomic_write(path, text.encode("utf-8"))


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
    ensure_directory(destination)
    for filename in ("manifest.json", "Overlay.qml", "BarWidget.qml", "Clip.js", "storage.py", "safe_io.py", "README.md"):
        backup(destination / filename)
        install_file(ROOT / filename, destination / filename)
    ensure_directory(destination / "assets")
    for asset in (ROOT / "assets").iterdir():
        if asset.is_file():
            backup(destination / "assets" / asset.name)
            install_file(asset, destination / "assets" / asset.name)
    applications = HOME_DIR / ".local/share/applications"
    icons = HOME_DIR / ".local/share/icons/hicolor"
    desktop = applications / (PLUGIN + ".desktop")
    icon = icons / "scalable/apps" / (PLUGIN + ".svg")
    for source, target in ((ROOT / "assets" / desktop.name, desktop),
                           (ROOT / "assets/clip.svg", icon)):
        ensure_directory(target.parent)
        backup(target)
        install_file(source, target)
    if shutil.which("desktop-file-validate"):
        run("desktop-file-validate", str(desktop))
    for command in (("gtk-update-icon-cache", "--force", "--ignore-theme-index", str(icons)),
                    ("update-desktop-database", str(applications))):
        if shutil.which(command[0]):
            run(*command)
    REPORT.append("Desktop launcher: " + str(desktop) + "\nIcon: " + str(icon))
    run("omarchy", "plugin", "validate", str(destination))
    run("omarchy-shell", "shell", "rescanPlugins")
    plugins = json.loads(run("omarchy", "plugin", "list", "--json", show=False))
    shell_config = HOME_DIR / ".config/omarchy/shell.json"
    backup(shell_config)
    if not any(p["id"] == PLUGIN and p["enabled"] for p in plugins):
        run("omarchy", "plugin", "enable", PLUGIN)
    try:
        run("omarchy", "bar", "put", PLUGIN, "--section", "right", "--before", "omarchy.tray")
    except subprocess.CalledProcessError as error:
        REPORT.append("Before-tray placement failed: " + error.stderr.strip())
        run("omarchy", "bar", "put", PLUGIN, "--section", "right", "--index", "0")
    right = json.loads(read_bytes(shell_config, MAX_CONFIG_BYTES).decode("utf-8"))["bar"]["layout"]["right"]
    identifiers = [entry if isinstance(entry, str) else entry["id"] for entry in right]
    assert PLUGIN in identifiers, "Clip bar launcher missing"
    if "omarchy.tray" in identifiers:
        assert identifiers.index(PLUGIN) < identifiers.index("omarchy.tray")
    REPORT.append("bar.layout.right: " + json.dumps(identifiers))
    bindings = HOME_DIR / ".config/hypr/bindings.lua"
    original = read_bytes(bindings, MAX_CONFIG_BYTES).decode("utf-8")
    marker = '-- Omarchy Clip\n'
    if marker not in original:
        backup(bindings)
        addition = "\n" + marker
        if conflicts:
            addition += 'hl.unbind("SUPER + SHIFT + V")\n'
        addition += 'o.bind("SUPER + SHIFT + V", "Omarchy Clip", "omarchy-shell shell toggle io.github.tuxclaw.clip")\n'
        addition += 'hl.layer_rule({ match = { namespace = "^omarchy-clip$" }, no_anim = true, animation = "none" })\n'
        write_text(bindings, original + addition)
        run("hyprctl", "reload")
        errors = run("hyprctl", "configerrors")
        if errors:
            write_text(bindings, original)
            run("hyprctl", "reload")
            run("hyprctl", "configerrors")
            raise RuntimeError("Hyprland errors; restored original bindings: " + errors)
    run("omarchy-shell", "shell", "ping")
    plugins = json.loads(run("omarchy", "plugin", "list", "--json", show=False))
    for identifier in (PLUGIN, "omarchy.clipboard"):
        assert any(p["id"] == identifier and p["enabled"] for p in plugins), identifier + " is not enabled"
    clip = next(p for p in plugins if p["id"] == PLUGIN)
    assert {"overlay", "bar-widget"}.issubset(clip["kinds"]), "Clip kinds missing"
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
        write_text(ROOT / ".context/validation.md", "# Clip validation\n\n```text\n" + "\n\n".join(REPORT) + "\n```\n")
