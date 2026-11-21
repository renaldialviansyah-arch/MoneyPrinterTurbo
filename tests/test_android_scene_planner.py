import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("planner",ROOT/"scripts/android_scene_planner.py")
planner=importlib.util.module_from_spec(spec);spec.loader.exec_module(planner)
class PlannerTests(unittest.TestCase):
 def test_empty(self):
  p=planner.build_plan("")
  self.assertEqual(p["scene_count"],0)
  self.assertEqual(p["estimated_duration_seconds"],0)
 def test_fields_and_duration(self):
  p=planner.build_plan("A short sentence. This second sentence contains several more words.")
  self.assertEqual(p["scene_count"],2)
  for scene in p["scenes"]:
   for field in ("narration","visual_prompt","motion_prompt","shot_type","transition","subtitle_text","duration_seconds"):
    self.assertIn(field,scene)
  self.assertGreater(p["estimated_duration_seconds"],0)
 def test_duration_bounds(self):
  self.assertGreaterEqual(planner.estimate_duration("one",minimum=4),4)
  self.assertLessEqual(planner.estimate_duration("word "*100,maximum=10),10)
if __name__=="__main__":unittest.main()
