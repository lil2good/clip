import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("storage", Path(__file__).parents[1] / "storage.py")
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.state = Path(self.directory.name)
        self.history = self.state / "clipboard-history.json"

    def seed(self, entries):
        self.history.write_text(json.dumps(entries))

    def test_delete_uses_identity_after_reorder_and_strips_extra_fields(self):
        self.seed([{"type": "text", "text": "new"}, {"type": "text", "text": "old", "pin": True},
                   {"type": "image", "path": "/image.png", "capturedAt": "today", "extra": 1}])
        storage.mutate(self.state, "delete", {"identity": "text:old"})
        self.assertEqual(json.loads(self.history.read_text()), [
            {"type": "text", "text": "new"},
            {"type": "image", "path": "/image.png", "mime": "image/png", "capturedAt": "today"}])

    def test_clear_preserves_new_copies(self):
        self.seed(["new copy", "old copy"])
        storage.mutate(self.state, "clear", {"identities": ["text:old copy"]})
        self.assertEqual(json.loads(self.history.read_text()), [{"type": "text", "text": "new copy"}])

    def test_pin_is_private_sidecar_only_and_survives_restart(self):
        self.seed(["hello"])
        before = self.history.read_bytes()
        payload = {"identity": "text:hello"}
        storage.mutate(self.state, "pin", payload)
        path = self.state / "clip-pins.json"
        self.assertEqual(json.loads(path.read_text()), ["text:hello"])
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        storage.mutate(self.state, "pin", payload)
        self.assertEqual(json.loads(path.read_text()), [])
        self.assertEqual(self.history.read_bytes(), before)

    def test_corrupt_history_is_not_overwritten(self):
        self.history.write_text("broken")
        with self.assertRaises(ValueError):
            storage.mutate(self.state, "clear", {"identities": []})
        self.assertEqual(self.history.read_text(), "broken")

    def test_concurrent_capture_retries_from_latest_history(self):
        self.seed(["old"])
        calls = 0
        def transform(values):
            nonlocal calls
            calls += 1
            if calls == 1:
                self.seed(["new", "old"])
            return [v for v in values if v != "old"]
        storage.update(self.history, transform)
        self.assertEqual(json.loads(self.history.read_text()), ["new"])
        self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
