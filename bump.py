"""Rewrite bucket/samong.json for the newest upstream release.

Scoop's own `checkver` / `autoupdate` fields are declared in the manifest, but
those are driven by Scoop's maintainer tooling (excavator / auto-pr), which is a
pile of PowerShell this bucket would have to vendor. This does the same job in a
form that can be run and tested anywhere.

The hash comes from the `.sha256` file the release already publishes rather than
from downloading the 30 MB archive — that file is the release's own claim about its
contents.

Three fields move together and all three must, or the install breaks in a
different way each time: `version`, the archive `url`, and `extract_dir`, which has
to match the directory inside the zip.

Usage: bump.py [--version X.Y.Z] [--check]
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = "waanvar/samong"
MANIFEST = Path(__file__).parent / "bucket" / "samong.json"
TIMEOUT = 60
SHA256 = re.compile(r"^[a-f0-9]{64}$")


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "scoop-samong-bump"})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        return response.read()


def latest_tag() -> str:
    return json.loads(get(f"https://api.github.com/repos/{REPO}/releases/latest"))["tag_name"]


def main() -> int:
    args = sys.argv[1:]
    tag = None
    if "--version" in args:
        tag = "v" + args[args.index("--version") + 1].lstrip("v")
    tag = tag or latest_tag()
    version = tag.lstrip("v")

    raw = MANIFEST.read_text(encoding="utf-8-sig")
    manifest = json.loads(raw)
    if manifest["version"] == version:
        print(f"manifest is already at {version}")
        return 0
    print(f"{manifest['version']} -> {version}")
    if "--check" in args:
        return 1

    stem = f"samong-v{version}-x86_64-windows"
    url = f"https://github.com/{REPO}/releases/download/{tag}/{stem}.zip"
    digest = get(f"{url}.sha256").decode("utf-8").split()[0]
    if not SHA256.match(digest):
        raise SystemExit(f"{url}.sha256 did not contain a digest")

    manifest["version"] = version
    arch = manifest["architecture"]["64bit"]
    arch["url"] = url
    arch["hash"] = digest
    # The zip unpacks into one directory named after the release; Scoop needs to be
    # told, or every shim points one level above the binaries.
    arch["extract_dir"] = stem

    # Four-space indent and a trailing newline: Scoop's own buckets are formatted
    # that way, and matching them keeps diffs to the fields that changed.
    MANIFEST.write_text(json.dumps(manifest, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")

    written = json.loads(MANIFEST.read_text(encoding="utf-8"))
    arch = written["architecture"]["64bit"]
    assert written["version"] == version, "version not written"
    assert version in arch["url"], "url does not name the new version"
    assert arch["extract_dir"] == stem, "extract_dir does not match the archive"
    assert SHA256.match(arch["hash"]), "hash is not a digest"
    print(f"manifest rewritten for {version} ({digest[:16]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
