"""Copy the portable skill; refuse overwrites and removal of modified copies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile


def reject_link(path):
    path=Path(path)
    try:
        info=path.lstat()
    except FileNotFoundError:
        return
    if path.is_symlink() or getattr(info,'st_file_attributes',0) & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400):
        raise ValueError('Refusing symbolic links or Windows reparse points: '+str(path))


def digest_tree(root):
    root = Path(root)
    reject_link(root)
    result = {}
    if not root.is_dir():
        return result
    for path in sorted(root.rglob('*')):
        reject_link(path)
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(source, destination):
    source, destination = Path(source), Path(destination)
    expected = digest_tree(source)
    if 'SKILL.md' not in expected:
        raise ValueError('Source must contain SKILL.md')
    reject_link(destination)
    if destination.exists():
        if destination.is_dir() and digest_tree(destination) == expected:
            return 'already-current'
        raise FileExistsError('Destination differs; preserve it and select another client path or back it up yourself')
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix='.creative-taste-', dir=destination.parent))
    try:
        shutil.copytree(source, staged, dirs_exist_ok=True)
        if digest_tree(staged) != expected:
            raise ValueError('Copied files did not match source')
        # Windows rename refuses an existing destination; never merge over owner files.
        if destination.exists():
            raise FileExistsError('Destination appeared during installation')
        os.rename(staged, destination)
    finally:
        if staged.exists():
            if staged.resolve().parent != destination.parent.resolve():
                raise ValueError('Unsafe staging cleanup path')
            shutil.rmtree(staged)
    return 'installed'


def uninstall(source, destination):
    source, destination = Path(source), Path(destination)
    reject_link(destination)
    if not destination.exists():
        return 'not-installed'
    if destination.name != 'creative-taste' or destination.resolve() == source.resolve():
        raise ValueError('Refusing to remove this path')
    expected = digest_tree(source)
    if 'SKILL.md' not in expected or digest_tree(destination) != expected:
        raise ValueError('Installed files changed; nothing removed. Preserve your edits manually.')
    # Every removable file was just checked against the canonical source.
    validated_destination=destination.resolve()
    for relative in expected:
        reject_link(destination)
        if destination.resolve()!=validated_destination:
            raise ValueError('Destination changed during removal')
        path = destination / relative
        for parent in path.parents:
            if parent==destination.parent:break
            reject_link(parent)
        reject_link(path)
        if not path.resolve().is_relative_to(validated_destination):
            raise ValueError('Unsafe removal path')
        path.unlink()
    for path in sorted(destination.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            path.rmdir()
    destination.rmdir()
    return 'removed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=['shared','codex','zcode'], default='shared')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent / 'skills' / 'creative-taste'
    folder = {'shared':'.agents','codex':'.codex','zcode':'.zcode'}[args.client]
    destination = Path.home() / folder / 'skills' / 'creative-taste'
    if args.check:
        status = 'current' if digest_tree(source) and digest_tree(source) == digest_tree(destination) else 'missing-or-different'
    elif args.uninstall:
        status = uninstall(source, destination)
    else:
        status = install(source, destination)
    print(json.dumps({'client':args.client,'status':status,'path':str(destination)},ensure_ascii=False))
    if args.check and status != 'current':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
