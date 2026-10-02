"""Executable role/distribution checks; agent behavior is forward-tested separately."""
from pathlib import Path
import shutil, subprocess, sys, tempfile, unittest
ROOT = Path(__file__).resolve().parents[1]
class DelegationDistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/"distribution"
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns(".git","__pycache__"))
    def tearDown(self): self.temp.cleanup()
    def validate(self):
        return subprocess.run([sys.executable,"scripts/validate.py"],cwd=self.root,capture_output=True,text=True)
    def test_only_independent_reviewer_is_managed(self):
        self.assertEqual([p.name for p in (self.root/"agents").glob("sdd-*.toml")],["sdd-reviewer.toml"])
        self.assertEqual(self.validate().returncode,0)
    def test_writable_reviewer_is_rejected(self):
        p=self.root/"agents/sdd-reviewer.toml"
        p.write_text(p.read_text().replace('sandbox_mode = "read-only"','sandbox_mode = "workspace-write"'))
        r=self.validate();self.assertNotEqual(r.returncode,0);self.assertIn("canonical agent settings",r.stderr)
    def test_old_writer_cannot_silently_reenter_distribution(self):
        (self.root/"agents/sdd-implementer-simple.toml").write_text('name = "sdd-implementer-simple"\nmodel = "gpt-6-luna"\nmodel_reasoning_effort = "max"\nsandbox_mode = "workspace-write"\n')
        r=self.validate();self.assertNotEqual(r.returncode,0);self.assertIn("canonical agent set",r.stderr)
if __name__ == "__main__": unittest.main()
