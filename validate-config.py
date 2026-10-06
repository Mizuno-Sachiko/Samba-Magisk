import subprocess
from pathlib import Path

from config import load_config

_, _, settings = load_config()
state = Path(settings["state_dir"])
prefix = Path(settings["termux_prefix"])
for directory in ["private", "state", "cache", "lock", "log", "run"]:
    if not (state / directory).is_dir():
        raise ValueError(f"Missing Samba directory: {state / directory}")
if not (state / "private/passdb.tdb").is_file():
    raise ValueError("Existing private Samba account database is required")
subprocess.run([prefix / "bin/smbd", "--version"], check=True)
# testparm can print account names and paths; keep its configuration output private.
subprocess.run(
    [prefix / "bin/testparm", "-s", state / "smb.conf"],
    check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
