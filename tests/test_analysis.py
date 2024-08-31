import unittest
from src import analysis

class TestAnalysis(unittest.TestCase):
    def test_extract_video_metadata(self):
        metadata = analysis.extract_video_metadata("sample_video.mp4")
        self.assertIn("frame_count", metadata)
        self.assertIn("bitrate", metadata)

    def test_analyze_structural_elements(self):
        frames = analysis.analyze_structural_elements("sample_video.mp4")
        self.assertTrue(len(frames) > 0)

    def test_detect_scene_changes(self):
        scenes = analysis.detect_scene_changes("sample_video.mp4")
        self.assertTrue(len(scenes) > 0)

    def test_generate_formula(self):
        formula = analysis.generate_formula("My Channel")
        self.assertIn("channel_name", formula)
        self.assertIn("video_style", formula)
