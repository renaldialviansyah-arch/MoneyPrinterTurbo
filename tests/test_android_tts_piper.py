import tempfile,subprocess,unittest,shutil
from pathlib import Path
class TestPiperTTS(unittest.TestCase):
 def test_cli_smoke(self):
  exe=shutil.which("piper")
  if not exe:self.skipTest("Piper CLI not installed")
  model=__import__('os').environ.get('PIPER_TEST_MODEL')
  if not model:self.skipTest("Set PIPER_TEST_MODEL to a downloaded voice model")
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'voice.wav'
   subprocess.run([exe,'--model',model,'--output_file',str(out)],input='Piper neural narration test.',text=True,check=True)
   self.assertTrue(out.exists());self.assertGreater(out.stat().st_size,1000)
if __name__=='__main__':unittest.main()
