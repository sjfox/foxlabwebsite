"""Behavior checks for the JSON-to-timeline publishing step."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("build_news", Path(__file__).resolve().parents[1] / "scripts/build_news.py")
news = importlib.util.module_from_spec(spec)
spec.loader.exec_module(news)


class NewsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_root = news.ROOT
        news.ROOT = Path(self.temp.name)
        (news.ROOT / "data").mkdir()
        (news.ROOT / "news").mkdir()

    def tearDown(self):
        news.ROOT = self.original_root
        self.temp.cleanup()

    def render(self, items):
        (news.ROOT / "data/news.json").write_text(json.dumps(items))
        news.build()
        return (news.ROOT / "news/_timeline.qmd").read_text()

    def entry(self, title, date="2025-01"):
        return dict(date=date, title=title, summary="A summary", details="Details", tags=["research"])

    def test_new_json_entries_and_tags_appear_in_sorted_output(self):
        old = self.entry("An older update")
        newer = self.entry("Bren's update", "2026-01-02")
        newer["tags"] = ["new-topic"]
        output = self.render([old, newer])
        self.assertLess(output.index('id="brens-update"'), output.index('id="an-older-update"'))
        self.assertIn('<option value="new-topic">', output)
        self.assertIn('aria-controls="detail-brens-update"', output)
        self.assertIn('aria-expanded="true"', output)  # All content is open without JS.

    def test_content_is_text_not_executable_markup(self):
        entry = self.entry("Untrusted <script>")
        entry["details"] = '<img src=x onerror="alert(1)">'
        output = self.render([entry])
        self.assertIn('&lt;img src=x onerror=&quot;', output)
        self.assertNotIn('<img src=x', output)

    def test_duplicate_anchors_and_missing_images_fail_build(self):
        with self.assertRaises(ValueError):
            self.render([self.entry("An update"), self.entry("An update")])
        entry = self.entry("An update")
        entry["images"] = ["../missing.jpg"]
        with self.assertRaises(ValueError):
            self.render([entry])


if __name__ == "__main__":
    unittest.main()
