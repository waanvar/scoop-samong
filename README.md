# scoop-samong

A [Scoop](https://scoop.sh) bucket for [Samong](https://github.com/waanvar/samong)
— a local-first, Obsidian-compatible knowledge base. Notes are Markdown files in a
folder you already have, and nothing leaves your machine.

```powershell
scoop bucket add samong https://github.com/waanvar/scoop-samong
scoop install samong
```

Installs four shims: `samong` (CLI), `samong-server` (local web UI and API),
`samong-mcp` (MCP server for AI agents), and `samong-app` (double-click launcher).

## Why install this way

Samong's binaries are not code-signed, and a certificate costs money the project
does not have. Downloading the zip in a browser can trip Windows SmartScreen, which
warns until a file has earned download reputation it will never earn quickly.

Scoop fetches the archive itself and verifies it against the SHA-256 the release
publishes. No browser, no reputation check, nothing to click through.

## About `Open Samong.exe`

The release archive contains both `samong-app.exe` and a copy called
`Open Samong.exe` — the second exists so that someone who unzips the archive by
hand has something obvious to double-click.

This bucket shims **`samong-app.exe`**, not the copy: a shim whose name contains a
space is awkward to invoke from a shell, and the two files are byte-identical
anyway. Run `samong-app` and you get the launcher.

(Those two names being *distinct files* is not a given — v0.3.3 was withdrawn
because `cp` on a case-insensitive filesystem made `samong.exe` a copy of the
launcher. Upstream now asserts they differ before publishing.)

## What is verified

Every push installs the manifest on a Windows runner and then, rather than
stopping at `--version`:

- writes two notes and searches for a word **inside** one of them
- follows a `[[wikilink]]` and checks it resolves
- searches a Thai sentence, which only works if the word-segmentation dictionary
  was packaged into the binary — the assertion that fails if a release was built
  wrong

The manifest's `version`, archive `url` and `extract_dir` are also checked against
each other. Those three move together, and each mismatch breaks the install a
different way: a wrong `extract_dir` in particular leaves every shim pointing one
directory above the binaries.

Only 64-bit x86 is published, because that is the only Windows archive upstream
builds. ARM64 Windows is not covered.

## How it stays current

`bump.py` reads the newest upstream release and rewrites version, url, hash and
`extract_dir`, taking the digest from the `.sha256` file published beside the
archive. `.github/workflows/bump.yml` runs it every six hours, **installs the
result on the runner, and only then commits**.

Run it now instead of waiting: Actions → **Bump** → Run workflow. A specific
version can be pinned there.

## Reporting problems

Manifest problems here. Anything about Samong itself —
[waanvar/samong](https://github.com/waanvar/samong/issues).

Apache-2.0, like the project. The name "Samong" and the logo are not covered by
that licence.
