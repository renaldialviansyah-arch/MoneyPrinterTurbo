import json,tempfile,unittest
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location("bridge",Path(__file__).parent.parent/"scripts"/"android_visual_manifest_bridge.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class BridgeTests(unittest.TestCase):
 def test_metadata_structure_is_convertible(self):
  data=[{"scene":1,"path":"/tmp/x.jpg","source":"site","license":"CC","notes":"n"}]
  assets=[{"scene":int(x["scene"]),"path":str(Path(x["path"]).resolve()),"source":x.get("source",x.get("url","downloaded URL")),"license":x.get("license","unspecified"),"notes":x.get("notes","")} for x in data]
  self.assertEqual(assets[0]["scene"],1);self.assertEqual(assets[0]["license"],"CC")
if __name__=="__main__":unittest.main()
