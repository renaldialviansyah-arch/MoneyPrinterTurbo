#!/usr/bin/env python3
"""Level 10 production readiness gate: deterministic local tests, no network/model."""
import json, subprocess, tempfile, unittest
from pathlib import Path
from PIL import Image
from scripts.android_asset_provenance_audit import audit
from scripts.android_video_qc import inspect
from scripts.android_subtitle_generator import generate

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.img=self.root/"asset.png"
        Image.new("RGB",(640,960),(30,80,120)).save(self.img)
    def tearDown(self): self.tmp.cleanup()
    def manifest(self,name,entries):
        p=self.root/name;p.write_text(json.dumps({"assets":entries}),encoding="utf-8");return p
    def entry(self,scene,source,license="CC BY 4.0"):
        return {"scene":scene,"path":str(self.img),"source":source,"license":license}
    def test_complete_external_manifest_passes(self):
        m=self.manifest("pass.json",[self.entry(1,"https://commons.wikimedia.org/wiki/File:A"),self.entry(2,"https://commons.wikimedia.org/wiki/File:B")])
        self.assertEqual(audit(m,2,require_external=True)["status"],"PASS")
    def test_fallback_fails_external_gate(self):
        m=self.manifest("fallback.json",[self.entry(1,"generated fallback graphic","original generated graphic")])
        self.assertEqual(audit(m,1,require_external=True)["status"],"FAIL")
    def test_duplicate_source_degraded_and_rejected_when_external_required(self):
        u="https://commons.wikimedia.org/wiki/File:Same"
        m=self.manifest("dup.json",[self.entry(1,u),self.entry(2,u)])
        self.assertEqual(audit(m,2)["status"],"DEGRADED")
        self.assertEqual(audit(m,2,require_external=True)["status"],"FAIL")
    def test_missing_asset_fails(self):
        m=self.manifest("missing.json",[{"scene":1,"path":str(self.root/"missing.png"),"source":"https://example.org/a","license":"CC BY"}])
        self.assertEqual(audit(m,1)["status"],"FAIL")
    def test_scene_count_mismatch_fails(self):
        m=self.manifest("count.json",[self.entry(1,"https://example.org/a")])
        self.assertEqual(audit(m,2)["status"],"FAIL")
    def test_subtitle_generation_has_text_and_timing(self):
        s=generate({"scenes":[{"duration_seconds":2.5,"narration":"First readiness caption."},{"duration_seconds":3,"subtitle_text":"Second caption."}]})
        self.assertIn("First readiness caption.",s);self.assertIn("Second caption.",s);self.assertIn("00:00:02,500 --> 00:00:05,500",s)
    def test_video_audio_subtitle_qc_passes(self):
        v=self.root/"fixture.mp4";srt=self.root/"fixture.srt"
        srt.write_text("1\n00:00:00,000 --> 00:00:01,500\nReadiness fixture\n",encoding="utf-8")
        cmd=["ffmpeg","-y","-v","error","-f","lavfi","-i","color=c=blue:s=360x640:d=2","-f","lavfi","-i","sine=frequency=440:duration=2","-i",str(srt),"-shortest","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-c:s","mov_text",str(v)]
        subprocess.run(cmd,check=True)
        q=inspect(v,expected_duration=2,require_subtitles=True,min_width=300,min_height=500)
        self.assertEqual(q["status"],"PASS",q)
    def test_qc_rejects_missing_file(self):
        with self.assertRaises(Exception): inspect(self.root/"missing.mp4")
if __name__=="__main__":
    unittest.main(verbosity=2)
