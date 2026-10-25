"""Verify historical publication isolation and archive integrity."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

import pytest

spec = importlib.util.spec_from_file_location(
    "public_release", Path(__file__).parents[1] / "scripts/prepare_public_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def test_historical_release_preserves_data_and_adds_context(tmp_path):
    output = tmp_path / "public"
    release.prepare("legacy_snapshot", output)
    manifest = json.loads(release.MANIFEST.read_text())
    with tarfile.open(release.ROOT / manifest["archive"]) as bundle:
        for item in bundle.getmembers():
            if item.isfile() and item.name.startswith("./data/"):
                assert (output / item.name).read_bytes() == bundle.extractfile(item).read()
    assert 'id="historical-release-note"' in (output / "index.html").read_text()
    assert json.loads((output / "release.json").read_text())["frozen"] is True
    with pytest.raises(FileExistsError):
        release.prepare("legacy_snapshot", output)


def test_current_mode_copies_current_site_without_legacy_note(tmp_path, monkeypatch):
    (tmp_path / "site").mkdir()
    (tmp_path / "site/index.html").write_text("current build")
    monkeypatch.setattr(release, "ROOT", tmp_path)
    release.prepare("current", tmp_path / "public")
    assert (tmp_path / "public/index.html").read_text() == "current build"
    assert json.loads((tmp_path / "public/release.json").read_text())["frozen"] is False


def test_checksum_failure_does_not_create_output(tmp_path):
    archive = tmp_path / "bad.tar.gz"
    archive.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        release.extract_snapshot(archive, tmp_path / "public", "incorrect")
    assert not (tmp_path / "public").exists()


@pytest.mark.parametrize("name,kind", [("../escape", tarfile.REGTYPE),
                                      ("/absolute", tarfile.REGTYPE),
                                      ("link", tarfile.SYMTYPE)])
def test_unsafe_archive_is_rejected_before_extracting(tmp_path, name, kind):
    archive = tmp_path / "unsafe.tar"
    with tarfile.open(archive, "w") as bundle:
        member = tarfile.TarInfo(name)
        member.type = kind
        if kind == tarfile.REGTYPE:
            member.size = 1
            bundle.addfile(member, io.BytesIO(b"x"))
        else:
            member.linkname = "/etc/passwd"
            bundle.addfile(member)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="Unsafe"):
        release.extract_snapshot(archive, tmp_path / "public", digest)
    assert not (tmp_path / "public").exists()
