import importlib.util, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("fetcher",Path(__file__).parent.parent/"scripts"/"android_visual_fetcher.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class URLTests(unittest.TestCase):
 def test_reject_http_by_default(self):
  with self.assertRaises(ValueError):m.safe_url("http://example.com/a.jpg")
 def test_credentials_rejected(self):
  with self.assertRaises(ValueError):m.safe_url("https://user:pass@example.com/a.jpg")
 def test_localhost_rejected(self):
  with self.assertRaises(ValueError):m.safe_url("https://localhost/a.jpg")
 def test_non_https_allowed_only_flag(self):
  with self.assertRaises(ValueError):m.safe_url("http://example.com/a.jpg")
if __name__=="__main__":unittest.main()
