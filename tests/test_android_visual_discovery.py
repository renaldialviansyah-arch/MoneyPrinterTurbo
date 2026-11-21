import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("discovery",Path(__file__).parent.parent/"scripts"/"android_visual_discovery.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DiscoveryTests(unittest.TestCase):
 def test_empty_scene_plan_rejected(self):
  with self.assertRaises(ValueError):m.discover({"scenes":[]})
if __name__=="__main__":unittest.main()
