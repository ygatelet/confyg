import tempfile
from pathlib import Path

from weldyn import get_root


def test_get_root():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        sub_dir = root / 'sub_dir'
        sub_sub_dir = sub_dir / 'sub_sub_dir'
        sub_sub_dir.mkdir(parents=True)

        test_file = sub_sub_dir / 'test_file.py'
        test_file.touch()

        assert get_root(str(test_file), 0) == sub_sub_dir
        assert get_root(str(test_file), 1) == sub_dir
        assert get_root(str(test_file), 2) == root
