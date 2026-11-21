import tempfile,subprocess,shutil,unittest
from pathlib import Path
class TestEspeakTTS(unittest.TestCase):
 def test_synthetic_output(self):
  exe=shutil.which("espeak-ng") or shutil.which("espeak")
  if not exe:self.skipTest("espeak missing")
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/"test.wav"
   subprocess.run([exe,"-v","en-us","-s","150","-w",str(out),"Automated narration smoke test"],check=True)
   self.assertTrue(out.exists());self.assertGreater(out.stat().st_size,1000)
if __name__=="__main__":unittest.main()
