import json
import os
from pathlib import Path
import sys
import tempfile


def normalize(value):
    if isinstance(value, str):
        value = {"type": "text", "text": value}
    if not isinstance(value, dict):
        return None
    if value.get("type") == "text" and isinstance(value.get("text"), str):
        return {"type": "text", "text": value["text"]} if value["text"].strip() else None
    if value.get("type") == "image" and isinstance(value.get("path"), str) and value["path"]:
        entry = {"type": "image", "path": value["path"], "mime": str(value.get("mime") or "image/png")}
        if value.get("capturedAt") is not None:
            entry["capturedAt"] = str(value["capturedAt"])
        return entry
    return None


def key(entry):
    return "image:" + entry["path"] if entry["type"] == "image" else "text:" + entry["text"]


def read(path, default):
    try:
        raw = path.read_bytes()
        return json.loads(raw), raw
    except FileNotFoundError:
        return default, None


def update(path, transform):
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(5):
        values, before = read(path, [])
        result = transform(values)
        fd, temporary = tempfile.mkstemp(prefix=".clip-", dir=path.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            if read(path, [])[1] != before:
                continue
            os.replace(temporary, path)
            return
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    raise RuntimeError("History changed repeatedly; please try again")


def mutate(state, operation, payload):
    if operation == "pin":
        identity = payload["identity"]
        if not isinstance(identity, str) or not identity.startswith(("text:", "image:")):
            raise ValueError("Invalid pin")
        def pin(values):
            if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                raise ValueError("Invalid pins file")
            return [v for v in values if v != identity] if identity in values else values + [identity]
        update(state / "clip-pins.json", pin)
        return
    if operation not in ("delete", "clear"):
        raise ValueError("Unknown operation")
    targets = {payload["identity"]} if operation == "delete" else set(payload["identities"])
    def remove(values):
        if not isinstance(values, list):
            raise ValueError("Invalid history file")
        entries = [normalize(value) for value in values]
        return [entry for entry in entries if entry is not None and key(entry) not in targets]
    update(state / "clipboard-history.json", remove)


if __name__ == "__main__":
    try:
        mutate(Path.home() / ".local/state/omarchy", sys.argv[1], json.loads(sys.stdin.readline()))
    except Exception as error:
        print("Clip could not save: " + str(error), file=sys.stderr)
        sys.exit(1)
