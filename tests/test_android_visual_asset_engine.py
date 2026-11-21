#!/usr/bin/env python3
"""Tests for the offline Android visual asset resolver."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
MOD=HERE.parent/"scripts"/"android_visual_asset_engine.py"
spec=importlib.util.spec_from_file_location("visual_engine",MOD);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ResolverTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
  (self.base/"a.jpg").write_bytes(b"placeholder");(self.base/"b.mp4").write_bytes(b"placeholder")
  self.plan=self.base/"plan.json";self.plan.write_text(json.dumps({"scenes":[{"narration":"one"},{"narration":"two"}]}))
  self.man=self.base/"manifest.json"
 def tearDown(self):self.tmp.cleanup()
 def test_resolves_in_plan_order_and_metadata(self):
  self.man.write_text(json.dumps({"assets":[{"scene":2,"path":"b.mp4","source":"test"},{"scene":1,"path":"a.jpg"}]}))
  assets,meta,extras=m.build(self.plan,self.man)
  self.assertEqual(Path(assets[0]).name,"a.jpg");self.assertEqual(Path(assets[1]).name,"b.mp4")
  self.assertEqual(meta[1]["asset_type"],"video");self.assertEqual(extras,[])
 def test_missing_scene_fails(self):
  self.man.write_text(json.dumps({"assets":[{"scene":1,"path":"a.jpg"}]}))
  with self.assertRaises(ValueError):m.build(self.plan,self.man)
 def test_duplicate_scene_fails(self):
  self.man.write_text(json.dumps({"assets":[{"scene":1,"path":"a.jpg"},{"scene":1,"path":"a.jpg"},{"scene":2,"path":"b.mp4"}]}))
  with self.assertRaises(ValueError):m.build(self.plan,self.man)
 def test_extra_scenes_reported(self):
  self.man.write_text(json.dumps({"assets":[{"scene":1,"path":"a.jpg"},{"scene":2,"path":"b.mp4"},{"scene":3,"path":"a.jpg"}]}))
  _,_,extras=m.build(self.plan,self.man);self.assertEqual(extras,[3])
if __name__=="__main__":unittest.main()
