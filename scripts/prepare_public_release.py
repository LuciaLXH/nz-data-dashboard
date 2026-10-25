"""Select the current build or a frozen historical demo for Pages publication."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "releases/legacy-19669bc/manifest.json"
NOTE = ('<p class="sub" id="historical-release-note" role="note">'
        'Historical demo · Earlier estimates are under review. '
        'Do not use them to assess water shortages or investment priorities.</p>')


def extract_snapshot(archive, destination, expected_sha256):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected_sha256:
        raise ValueError("Historical release archive checksum mismatch")
    with tarfile.open(archive) as bundle:
        members = bundle.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsafe archive member: {member.name}")
        bundle.extractall(destination, members=members, filter="data")


def prepare(mode, output):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    if mode == "current":
        shutil.copytree(ROOT / "site", output)
        release = {"mode": "current", "frozen": False}
    elif mode == "legacy_snapshot":
        manifest = json.loads(MANIFEST.read_text())
        extract_snapshot(ROOT / manifest["archive"], output, manifest["archive_sha256"])
        for name, digest in manifest["original_assets_sha256"].items():
            if hashlib.sha256((output / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"Unexpected legacy asset: {name}")
        for name in ("flow_percentile", "supply_per_capita", "population_growth"):
            data = json.loads((output / "data" / f"{name}.json").read_text())
            if data["schema_version"] != 1:
                raise ValueError(f"Historical UI requires schema v1: {name}")
        index = output / "index.html"
        html = index.read_text()
        if html.count("</header>") != 1:
            raise ValueError("Unexpected legacy header; cannot add historical context")
        index.write_text(html.replace("</header>", NOTE + "\n</header>"))
        release = {**manifest, "mode": mode,
                   "presentation_change": "Added historical-demo context; original datasets unchanged"}
    else:
        raise ValueError(f"Unknown publication mode: {mode}")
    (output / "release.json").write_text(json.dumps(release, indent=2) + "\n")
    print(f"Prepared {mode} publication at {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("current", "legacy_snapshot"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.mode, args.output)
