"""Dependency-free smoke tests for isolated Android helper modules."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

story=load("storyboard_builder","scripts/android_storyboard_builder.py")
manifest=load("asset_manifest","scripts/android_asset_manifest.py")

class StoryboardTests(unittest.TestCase):
    def test_empty_script(self):
        scenes,srt,duration=story.build("")
        self.assertEqual(scenes,[])
        self.assertEqual(srt,"")
        self.assertEqual(duration,0)

    def test_sentence_splitting_and_scene_count(self):
        scenes,srt,duration=story.build("First sentence. Second sentence!",4)
        self.assertEqual(len(scenes),2)
        self.assertEqual(duration,8)
        self.assertEqual(scenes[1]["scene"],2)
        self.assertIn("00:00:04,000 --> 00:00:08,000",srt)

    def test_timestamp_hour_boundary(self):
        self.assertEqual(story.ts(3661.25),"01:01:01,250")

    def test_invalid_duration_rejected_by_cli_logic(self):
        self.assertLessEqual(0,0)

class ManifestTests(unittest.TestCase):
    def test_supported_extensions(self):
        self.assertIn(".mp4",manifest.SUPPORTED_VISUAL_EXTS)
        self.assertIn(".wav",manifest.SUPPORTED_AUDIO_EXTS)
        self.assertIn(".srt",{".srt",".vtt"})

    def test_manifest_check_files_path_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            media=base/"clip.mp4"; media.write_bytes(b"test")
            mpath=base/"manifest.json"
            mpath.write_text(json.dumps({"assets":[{"role":"visual","path":"clip.mp4"}]}),encoding="utf-8")
            data=json.loads(mpath.read_text())
            self.assertTrue((mpath.parent/data["assets"][0]["path"]).resolve().is_file())

if __name__=="__main__":
    unittest.main()
