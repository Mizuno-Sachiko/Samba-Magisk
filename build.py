import argparse
import hashlib
import json
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Build a credential-free Samba Magisk module"
)
parser.add_argument(
    "--installer", type=Path, required=True, help="Magisk ZIP containing the installer"
)
parser.add_argument("--installer-sha256", required=True)
parser.add_argument(
    "--library", type=Path, required=True, help="Compiled Android heap-tagging adapter"
)
parser.add_argument("--library-sha256", required=True)
parser.add_argument("--version", required=True)
parser.add_argument("--version-code", type=int, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
for path, digest in [
    (args.installer, args.installer_sha256),
    (args.library, args.library_sha256),
]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"Input SHA-256 mismatch: {path.name}")
root = Path(__file__).resolve().parent
repository = "https://github.com/Mizuno-Sachiko/Samba-Magisk"
args.output.parent.mkdir(parents=True, exist_ok=True)
# Exclusive creation preserves existing release artifacts.
with (
    zipfile.ZipFile(args.installer) as source,
    zipfile.ZipFile(args.output, "x", zipfile.ZIP_DEFLATED) as output,
):
    for name in [
        "META-INF/com/google/android/update-binary",
        "META-INF/com/google/android/updater-script",
    ]:
        output.writestr(name, source.read(name))
    for name in [
        "service.sh",
        "watch.py",
        "config.py",
        "validate-config.py",
        "customize.sh",
        "heap-untag.c",
        "check-parser.py",
        "LICENSE",
        "README.md",
    ]:
        output.writestr(name, (root / name).read_bytes())
    output.writestr("libheap-untag.so", args.library.read_bytes())
    output.writestr(
        "module.prop",
        f"""id=samba_personal
name=Samba for Magisk
version={args.version}
versionCode={args.version_code}
author=contributors
description=Root SMB3 shared storage on the configured interface. Requires Termux Samba, Python and private configuration. No wake lock.
updateJson={repository}/releases/latest/download/update.json
""",
    )
# The latest Release supplies the manifest; downloads stay tied to its version.
release = f"{repository}/releases/download/v{args.version}"
with args.output.with_name("update.json").open("x", encoding="utf-8") as output:
    json.dump(
        {
            "version": args.version,
            "versionCode": args.version_code,
            "zipUrl": f"{release}/{args.output.name}",
            "changelog": f"{release}/changelog.md",
        },
        output,
        indent=2,
    )
    output.write("\n")
print(args.output)
