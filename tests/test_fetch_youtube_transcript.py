"""Verify the YouTube URL whitelist without fetching external content."""
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fetch_youtube_transcript",
    ROOT / "skills/shared/fetch-known-url/scripts/fetch_youtube_transcript.py",
)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class YouTubeUrlTests(unittest.TestCase):
    def test_supported_urls_and_bare_video_id(self):
        video_id = "dQw4w9WgXcQ"
        for value in (
            video_id,
            f"https://youtu.be/{video_id}?t=10",
            f"https://youtube.com/watch?v={video_id}",
            f"http://www.youtube.com/watch?v={video_id}&t=10",
            f"https://m.youtube.com/shorts/{video_id}",
            f"https://WWW.YouTube.com/embed/{video_id}",
        ):
            with self.subTest(value=value):
                self.assertEqual(helper.video_id_from_url(value), video_id)

    def test_deceptive_hostnames_are_rejected(self):
        for value in (
            "https://notyoutu.be/dQw4w9WgXcQ",
            "https://youtube.com.attacker.example/watch?v=dQw4w9WgXcQ",
            "https://notyoutube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com@attacker.example/watch?v=dQw4w9WgXcQ",
        ):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                helper.video_id_from_url(value)

    def test_unsupported_schemes_and_invalid_ids_are_rejected(self):
        for value in (
            "ftp://youtube.com/watch?v=dQw4w9WgXcQ",
            "//youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=invalid",
            "https://youtu.be/",
        ):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                helper.video_id_from_url(value)


if __name__ == "__main__":
    unittest.main()
