import ipaddress
import tomllib
from pathlib import Path
from typing import Any

CONFIG = Path("/data/adb/samba/config.toml")


def load_config(
    path: Path = CONFIG,
) -> tuple[str, ipaddress.IPv4Network, dict[str, Any]]:
    with path.open("rb") as source:
        config = tomllib.load(source)
    dev_name = config["interface"]
    if not dev_name:
        raise ValueError("Set interface to the sharing interface name")
    # The subnet selects listener addresses and filters SMB client access.
    network = ipaddress.IPv4Network(config["subnet"])
    return dev_name, network, config
