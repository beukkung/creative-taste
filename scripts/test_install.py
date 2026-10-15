import importlib.util
from pathlib import Path
import tempfile
import unittest
import os
import subprocess

spec = importlib.util.spec_from_file_location('installer', Path(__file__).with_name('install.py'))
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source/'SKILL.md').write_text('original', encoding='utf-8')
        (self.source/'references').mkdir()
        (self.source/'references'/'music.md').write_text('music', encoding='utf-8')
        self.dest = self.root/'skills'/'creative-taste'

    def test_copy_and_idempotence(self):
        self.assertEqual(installer.install(self.source,self.dest),'installed')
        self.assertEqual(installer.install(self.source,self.dest),'already-current')
        self.assertEqual(installer.digest_tree(self.source),installer.digest_tree(self.dest))

    def test_existing_different_content_is_preserved(self):
        self.dest.mkdir(parents=True)
        (self.dest/'SKILL.md').write_text('owner edits',encoding='utf-8')
        with self.assertRaises(FileExistsError): installer.install(self.source,self.dest)
        self.assertEqual((self.dest/'SKILL.md').read_text(),'owner edits')

    def test_changed_uninstall_is_refused(self):
        installer.install(self.source,self.dest)
        (self.dest/'notes.txt').write_text('keep me')
        with self.assertRaises(ValueError): installer.uninstall(self.source,self.dest)
        self.assertTrue((self.dest/'notes.txt').exists())

    def test_matching_uninstall(self):
        installer.install(self.source,self.dest)
        self.assertEqual(installer.uninstall(self.source,self.dest),'removed')
        self.assertFalse(self.dest.exists())

    def test_symbolic_destination_is_refused(self):
        other=self.root/'other'; other.mkdir()
        self.dest.parent.mkdir()
        try: self.dest.symlink_to(other,target_is_directory=True)
        except OSError: self.skipTest('symlinks unavailable on this host')
        with self.assertRaises(ValueError): installer.install(self.source,self.dest)

    def junction(self, link, target):
        if os.name!='nt':self.skipTest('Windows junction fixture')
        link.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['cmd','/c','mklink','/J',str(link),str(target)],check=True,capture_output=True)

    def test_junction_uninstall_preserves_linked_target(self):
        target=self.root/'owned-target'
        installer.install(self.source,target)
        self.junction(self.dest,target)
        with self.assertRaises(ValueError):installer.uninstall(self.source,self.dest)
        self.assertEqual((target/'SKILL.md').read_text(),'original')

    def test_junction_install_is_refused(self):
        target=self.root/'owned-target'
        installer.install(self.source,target)
        self.junction(self.dest,target)
        with self.assertRaises(ValueError):installer.install(self.source,self.dest)

    def test_junction_inside_source_is_refused(self):
        target=self.root/'outside';target.mkdir()
        (target/'owner.txt').write_text('preserve')
        self.junction(self.source/'linked',target)
        with self.assertRaises(ValueError):installer.digest_tree(self.source)

    def test_junction_inside_destination_is_refused(self):
        installer.install(self.source,self.dest)
        target=self.root/'outside';target.mkdir()
        self.junction(self.dest/'linked',target)
        with self.assertRaises(ValueError):installer.uninstall(self.source,self.dest)


if __name__=='__main__': unittest.main()
